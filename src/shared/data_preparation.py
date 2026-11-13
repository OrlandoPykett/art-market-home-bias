
"""
Data preparation.

Contains functions for cleaning the auction dataset, converting
variable types, filtering observations and handling missing values.

Prepares the dataset for analytical variable construction and
regression analysis.
"""

import pandas as pd
import numpy as np

from src.shared.config import (
    REQUIRED_COLUMNS,
    NUMERIC_COLUMNS,
    NUMERIC_PREDICTORS,
    CATEGORICAL_PREDICTORS
)

# Filter observations
# --------------------

def filter_observations(df):
    """
    Remove observations with missing essential variables.

    An observation must have an artist name, artist country,
    sale country, sale year and real sale price to be included.

    Observations with a non-positive real price are also excluded,
    since logarithms can only be calculated for positive values.

    Args:
        df (pandas.DataFrame): Dataset to filter.

    Returns:
        pandas.DataFrame: Filtered dataset.
    """

    df = df.dropna(subset=REQUIRED_COLUMNS).copy()

    df = df[df["real_price_usd"] > 0].copy()

    return df


# Convert numeric columns
# --------------------

def convert_numeric_columns(df):
    """
    Convert available numeric variables to numeric data types.

    Invalid values are converted to NaN rather than raising errors.

    Args:
        df (pandas.DataFrame): Dataset to convert.

    Returns:
        pandas.DataFrame: Dataset with converted numeric columns.
    """

    df = df.copy()

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    return df


# Handle missing predictors
# --------------------

def handle_missing_predictors(df):
    """
    Handle missing values in numeric and categorical predictors.

    Numeric predictors are imputed using their median values.
    Missingness indicators are created to identify observations
    where the original numeric values were missing.

    Categorical predictors receive an 'Unknown' category
    when their values are missing.

    Args:
        df (pandas.DataFrame): Dataset to process.

    Returns:
        pandas.DataFrame: Dataset with missing predictors handled.
    """

    df = df.copy()

    # Numeric predictors: median imputation + missingness indicators
    for col in NUMERIC_PREDICTORS:
        if col in df.columns:
            missing_col = f"{col}_missing"

            df[missing_col] = df[col].isna().astype(int)

            median_value = df[col].median()

            if pd.notna(median_value):
                df[col] = df[col].fillna(median_value)

    # Categorical predictors: give missing values their own category
    for col in CATEGORICAL_PREDICTORS:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str)

    return df


# Clean country names
# --------------------

def clean_country_names(df):
    """
    Standardise country identifiers before constructing home bias.

    Removes leading and trailing whitespace and converts invalid
    country placeholders into missing values.

    Args:
        df (pandas.DataFrame): Dataset containing country variables.

    Returns:
        pandas.DataFrame: Dataset with cleaned country identifiers.
    """

    df = df.copy()

    country_columns = [
        "artist_country",
        "sale_country"
    ]

    invalid_countries = [
        "nan",
        "none",
        "null",
        "unknown",
        "n/a"
    ]

    for col in country_columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

        df.loc[
            df[col].str.lower().isin(invalid_countries).fillna(False),
            col
        ] = pd.NA

    return df


# Calculate artwork size
# --------------------

def create_artwork_size(df):
    """
    Construct artwork area, volume and log size.

    Volume is used when height, width and depth are all positive.
    Otherwise, area (height multiplied by width) is used when
    both dimensions are positive.

    Observations without a valid size measurement receive a
    missing log_size value.

    Returns:
        DataFrame with artwork_area, artwork_volume,
        size_measure and log_size columns.
    """
    df = df.copy()

    valid_area = df["height"].gt(0) & df["width"].gt(0)
    valid_volume = valid_area & df["depth"].gt(0)

    df["artwork_area"] = np.nan
    df.loc[valid_area, "artwork_area"] = (
        df.loc[valid_area, "height"]
        * df.loc[valid_area, "width"]
    )

    df["artwork_volume"] = np.nan
    df.loc[valid_volume, "artwork_volume"] = (
        df.loc[valid_volume, "height"]
        * df.loc[valid_volume, "width"]
        * df.loc[valid_volume, "depth"]
    )

    df["size_measure"] = (
        df["artwork_volume"].fillna(df["artwork_area"])
    )

    df["log_size"] = np.log(df["size_measure"])

    return df



# Prepare dataset
# --------------------

def prepare_dataset(df):
    """
    Perform the complete data preparation workflow.

    1. Convert numeric columns.
    2. Remove observations with missing essential variables.
    3. Exclude observations with non-positive real prices.
    4. Handle missing predictor values.
    5. Clean country names.
    6. Construct the log-price dependent variable.

    Args:
        df (pandas.DataFrame): Loaded auction dataset.

    Returns:
        pandas.DataFrame: Prepared dataset ready for analytical
        variable construction and regression analysis.
    """

    df = convert_numeric_columns(df)

    df = filter_observations(df)

    df = handle_missing_predictors(df)

    df = clean_country_names(df)

    # Dependent variable: log real price
    df["log_price"] = np.log(df["real_price_usd"])

    return df
