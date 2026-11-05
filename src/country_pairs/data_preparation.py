
"""
Data preparation for the country-pair analysis.

Uses shared preparation functions where possible and creates
the variables required specifically for the country-pair
regression analysis.
"""

import numpy as np
import pandas as pd

from src.shared.data_preparation import (
    convert_numeric_columns,
    clean_country_names
)


# Clean categorical columns
# --------------------

def clean_categorical_columns(df):
    """
    Clean categorical variables by removing whitespace and
    converting invalid placeholder values to missing values.

    Args:
        df (pd.DataFrame): Dataset to clean.

    Returns:
        pd.DataFrame: Dataset with cleaned categorical variables.
    """

    df = df.copy()

    categorical_columns = [
        "artist_name",
        "auction_house",
        "materials"
    ]

    invalid_values = [
        "",
        "nan",
        "none",
        "null",
        "unknown",
        "n/a"
    ]

    for col in categorical_columns:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
        )

        df.loc[
            df[col].str.lower().isin(invalid_values).fillna(False),
            col
        ] = pd.NA

    return df


# Filter invalid prices
# --------------------

def filter_invalid_prices(df):
    """
    Remove observations with missing or non-positive real prices.

    Args:
        df (pd.DataFrame): Dataset to filter.

    Returns:
        pd.DataFrame: Dataset containing valid sale prices.
    """

    df = df[
        df["real_price_usd"].notna()
        & (df["real_price_usd"] > 0)
    ].copy()

    return df


# Create log price
# --------------------

def create_log_price(df):
    """
    Construct the natural logarithm of real sale price.

    Args:
        df (pd.DataFrame): Dataset containing real sale prices.

    Returns:
        pd.DataFrame: Dataset with the ln_real_price variable.
    """

    df = df.copy()

    df["ln_real_price"] = np.log(df["real_price_usd"])

    return df


# Create artwork size
# --------------------

def create_artwork_size(df):
    """
    Construct artwork size using available dimensions.

    Uses height multiplied by width when both dimensions are
    positive. If depth is also available and positive, volume
    (height multiplied by width multiplied by depth) is used.

    The natural logarithm of size is also calculated.

    Args:
        df (pd.DataFrame): Dataset containing artwork dimensions.

    Returns:
        pd.DataFrame: Dataset with size and log_size variables.
    """

    df = df.copy()

    df["size"] = df["height"] * df["width"]

    volume_mask = (
        df["height"].gt(0)
        & df["width"].gt(0)
        & df["depth"].gt(0)
    )

    df.loc[volume_mask, "size"] = (
        df.loc[volume_mask, "height"]
        * df.loc[volume_mask, "width"]
        * df.loc[volume_mask, "depth"]
    )

    df.loc[df["size"] <= 0, "size"] = np.nan

    df["log_size"] = np.log(df["size"])

    return df


# Prepare country-pair dataset
# --------------------

def prepare_country_pair_data(df):
    """
    Perform the complete data preparation workflow for the
    country-pair regression analysis.

    1. Convert numeric columns.
    2. Clean country names and categorical variables.
    3. Remove observations with invalid prices.
    4. Construct log real price.
    5. Construct artwork size and log size.
    6. Remove observations with missing model variables.

    Args:
        df (pd.DataFrame): Loaded auction transaction dataset.

    Returns:
        pd.DataFrame: Prepared dataset for country-pair regressions.
    """

    df = convert_numeric_columns(df)

    # Convert country-pair numeric variables explicitly
    numeric_columns = [
        "real_price_usd",
        "height",
        "width",
        "depth",
        "sale_y"
    ]

    for col in numeric_columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = clean_country_names(df)
    df = clean_categorical_columns(df)
    df = filter_invalid_prices(df)
    df = create_log_price(df)
    df = create_artwork_size(df)

    required_variables = [
        "artist_country",
        "sale_country",
        "ln_real_price",
        "log_size",
        "artist_name",
        "auction_house",
        "sale_y",
        "materials"
    ]

    df = df.dropna(subset=required_variables)

    return df
