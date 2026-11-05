
"""
Data loading and initial validation.

Responsible for reading the cleaned auction datasets,
validating their structure and standardising country names.
"""

import pandas as pd

from src.country_mapping import convert_country
from src.shared.config import DATASET1_FILE, REQUIRED_COLUMNS


def load_data():
    """
    Load the cleaned auction dataset.

    Currently, only dataset 1 is included in the analysis.
    Dataset 2 can be added later once duplicate observations
    and compatibility between the datasets have been examined.

    Returns:
        pandas.DataFrame: The loaded auction observations.
    """

    df1 = pd.read_csv(
        DATASET1_FILE,
        encoding="latin1",
        low_memory=False
    )

    # TODO: Examine duplicates and compatibility before combining
    # dataset 1 and dataset 2.

    return df1


def validate_columns(df, required_columns):
    """
    Check that a DataFrame contains all required columns.

    Args:
        df (pandas.DataFrame): Dataset to validate.
        required_columns (list): Column names required for the analysis.

    Raises:
        ValueError: If one or more required columns are missing.
    """

    missing_columns = [
        col for col in required_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}. "
            f"Available columns: {df.columns.tolist()}"
        )


def standardise_countries(df):
    """
    Standardise artist and sale country names.

    Applies the country mapping function to ensure that different
    spellings and representations of countries are consistent.

    Args:
        df (pandas.DataFrame): Dataset containing country information.

    Returns:
        pandas.DataFrame: Dataset with standardised country names.

    Raises:
        ValueError: If the required country columns are missing.
    """

    df = df.copy()

    country_columns = [
        "artist_country",
        "sale_country"
    ]

    validate_columns(df, country_columns)

    for col in country_columns:
        df[col] = df[col].apply(convert_country)

    return df


def load_and_validate_data():
    """
    Load the auction dataset and perform initial validation.

    Returns:
        pandas.DataFrame: Loaded and standardised dataset.
    """

    df = load_data()

    validate_columns(df, REQUIRED_COLUMNS)

    df = standardise_countries(df)

    return df
