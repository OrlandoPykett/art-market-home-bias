"""National pride (WVS wave 7, Q254): prepare and merge only."""

import pandas as pd

from src.shared.country_mapping import convert_wvs_country
from src.shared.non_destructive_merge import merge_on_keys


def prepare_national_pride_data(survey_file):
    survey = pd.read_csv(
        survey_file,
        usecols=["B_COUNTRY", "Q254"],
        low_memory=False
    )

    # TEMPORARY DIAGNOSTIC: inspect original WVS country codes
    print("\n========== RAW WVS COUNTRY CODES ==========")

    print("B_COUNTRY data type:", survey["B_COUNTRY"].dtype)

    print("\nUnique country codes and observation counts:")
    print(
        survey["B_COUNTRY"]
        .value_counts(dropna=False)
        .sort_index()
        .to_string()
    )

    print("============================================\n")

    survey["sale_country"] = survey["B_COUNTRY"].apply(
        convert_wvs_country
    )

    survey["Q254"] = pd.to_numeric(
        survey["Q254"], errors="coerce"
    )

    survey = survey[
        survey["Q254"].notna()
        & (survey["Q254"] > 0)
        & survey["sale_country"].notna()
    ]

    survey["very_proud"] = (survey["Q254"] == 1).astype(int)

    return (
        survey.groupby("sale_country")
        .agg(
            national_pride=("very_proud", "mean"),
            survey_responses=("very_proud", "count")
        )
        .reset_index()
    )


def add_national_pride(df, survey_file):
    pride = prepare_national_pride_data(survey_file)

    return merge_on_keys(
        df, pride,
        keys=["sale_country"],
        value_cols=["national_pride", "survey_responses"],
        label="national_pride",
    )