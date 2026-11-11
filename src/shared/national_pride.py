"""National pride (WVS wave 6, V211), (EVS 2008, v256): prepare and merge only."""

import pandas as pd

from src.shared.country_mapping import convert_wvs_country
from src.shared.config import WVS_FILE_1, WVS_FILE_2, WVS_FILE_3, WVS_FILE_4, WVS_FILE_5, WVS_FILE_6, EVS_FILE_1, EVS_FILE_2, EVS_FILE_3, EVS_FILE_4


def prepare_national_pride_data(wvs_file, evs_file):

    wvs = pd.read_csv(wvs_file)
    evs = pd.read_csv(evs_file)

    wvs = wvs.rename(columns={
        wvs.columns[0]: "COUNTRY",
        wvs.columns[2]: "QUESTION"
    })

    evs = evs.rename(columns={
        evs.columns[0]: "COUNTRY",
        evs.columns[2]: "QUESTION"
    })
    
    frames = [wvs, evs]
    survey = pd.concat(frames)

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


def add_national_pride(df):

    df = df.copy()

    # Year ranges and corresponding survey files
    survey_periods = [
        (0, 1990, WVS_FILE_1, EVS_FILE_1),
        (1990, 1995, WVS_FILE_2, EVS_FILE_2),
        (1995, 1999, WVS_FILE_3, EVS_FILE_2),
        (1999, 2005, WVS_FILE_4, EVS_FILE_3),
        (2005, 2008, WVS_FILE_5, EVS_FILE_3),
        (2008, 2010, WVS_FILE_5, EVS_FILE_4),
        (2010, float("inf"), WVS_FILE_6, EVS_FILE_4),
    ]

    # Initialise columns
    df["national_pride"] = float("nan")
    df["survey_responses"] = float("nan")

    # Ensure sale_y is numeric
    years = pd.to_numeric(df["sale_y"], errors="coerce")

    # Process each year range separately
    for start, end, wvs_file, evs_file in survey_periods:

        mask = (years >= start) & (years < end)

        if not mask.any():
            continue

        # Prepare the corresponding survey data
        pride = prepare_national_pride_data(wvs_file, evs_file)

        # Create country-to-pride lookup
        pride = pride.set_index("sale_country")

        # Assign values to matching rows
        df.loc[mask, "national_pride"] = (
            df.loc[mask, "sale_country"].map(pride["national_pride"])
        )

        df.loc[mask, "survey_responses"] = (
            df.loc[mask, "sale_country"].map(pride["survey_responses"])
        )

    return df