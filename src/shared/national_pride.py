"""National pride (WVS wave 7, Q254), (EVS 2008, v256): prepare and merge only."""

import pandas as pd

from src.shared.country_mapping import convert_wvs_country
from src.shared.non_destructive_merge import merge_on_keys


def prepare_national_pride_data(wvs_file, evs_file):

    wvsQ = "Q254"
    evsQ = "v256"
    
    wvs = pd.read_csv(
        wvs_file,
        usecols=["B_COUNTRY", wvsQ],
        low_memory=False
    )

    evs = pd.read_csv(
        evs_file,
        usecols=["country", evsQ]
    )

    wvs = wvs.rename(columns={
        "B_COUNTRY": "COUNTRY",
        wvsQ: "QUESTION"
    })

    evs = evs.rename(columns={
        "country": "COUNTRY",
        evsQ: "QUESTION"
    })
    
    frames = [wvs, evs]
    survey = pd.concat(frames)

    # TEMPORARY DIAGNOSTIC: inspect original WVS country codes
    print("\n========== RAW WVS COUNTRY CODES ==========")

    print("Country data type:", survey["COUNTRY"].dtype)

    print("\nUnique country codes and observation counts:")
    print(
        survey["COUNTRY"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )

    print("============================================\n")

    survey["sale_country"] = survey["COUNTRY"].apply(
        convert_wvs_country
    )

    survey["QUESTION"] = pd.to_numeric(
        survey["QUESTION"], errors="coerce"
    )

    survey = survey[
        survey["QUESTION"].notna()
        & (survey["QUESTION"] > 0)
        & survey["sale_country"].notna()
    ]

    survey["very_proud"] = (survey["QUESTION"] == 1).astype(int)

    return (
        survey.groupby("sale_country")
        .agg(
            national_pride=("very_proud", "mean"),
            survey_responses=("very_proud", "count")
        )
        .reset_index()
    )


def add_national_pride(df, wvs_file, evs_file):
    pride = prepare_national_pride_data(wvs_file, evs_file)

    return merge_on_keys(
        df, pride,
        keys=["sale_country"],
        value_cols=["national_pride", "survey_responses"],
        label="national_pride",
    )