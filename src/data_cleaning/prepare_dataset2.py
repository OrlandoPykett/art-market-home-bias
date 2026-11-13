
"""
Prepare dataset 2 for regression.

1. Export unique artists for manual country mapping.
2. Calculate real prices using CPI.
3. Merge artist-country information.
4. Create regression variables.
"""

import os
import numpy as np
import pandas as pd


# File paths
# --------------------

DATASET_FILE = "data/cleaned/dataset2_cleaned.csv"

ARTIST_MAPPING_FILE = "data/artist_country_mapping.csv"

OUTPUT_FILE = "data/cleaned/dataset2_regression_ready.csv"


def main():

    # Load dataset
    df = pd.read_csv(DATASET_FILE)

    # Convert relevant columns to numeric
    numeric_columns = [
        "price_usd",
        "uscpi",
        "sale_y",
        "height",
        "width"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------
    # 1. Export unique artists for manual country mapping
    # --------------------------------------------------

    if not os.path.exists(ARTIST_MAPPING_FILE):

        artists = (
            df["artist_name"]
            .dropna()
            .drop_duplicates()
            .sort_values()
        )

        artist_mapping = pd.DataFrame({
            "artist_name": artists,
            "artist_country": ""
        })

        os.makedirs(
            os.path.dirname(ARTIST_MAPPING_FILE),
            exist_ok=True
        )

        artist_mapping.to_csv(
            ARTIST_MAPPING_FILE,
            index=False
        )

        print(
            f"Created artist mapping file: "
            f"{ARTIST_MAPPING_FILE}"
        )

        print(
            f"Number of unique artists: {len(artists)}"
        )

        print(
            "Fill in artist_country and rerun this script."
        )

        return

    # --------------------------------------------------
    # 2. Calculate real prices using CPI
    # --------------------------------------------------

    df["real_price_usd"] = (
        df["price_usd"]
        / df["uscpi"]
    )

    # Remove invalid real prices
    df.loc[
        ~np.isfinite(df["real_price_usd"])
        | (df["real_price_usd"] <= 0),
        "real_price_usd"
    ] = np.nan

    # --------------------------------------------------
    # 3. Load and prepare artist-country mapping
    # --------------------------------------------------

    artist_mapping = pd.read_csv(
        ARTIST_MAPPING_FILE
    )

    # Ensure required columns exist
    required_columns = [
        "artist_name",
        "artist_country"
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in artist_mapping.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in artist mapping: {missing_columns}"
        )

    # Create normalised artist names for matching
    df["_artist_key"] = (
        df["artist_name"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    artist_mapping["_artist_key"] = (
        artist_mapping["artist_name"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

    # Remove rows without artist names
    artist_mapping = artist_mapping[
        artist_mapping["_artist_key"].notna()
        & (artist_mapping["_artist_key"] != "")
    ].copy()

    # Remove exact duplicate mapping rows
    artist_mapping = artist_mapping.drop_duplicates()

    # Check for conflicting country assignments
    country_counts = (
        artist_mapping
        .groupby("_artist_key")["artist_country"]
        .nunique()
    )

    conflicting_artists = country_counts[
        country_counts > 1
    ]

    if not conflicting_artists.empty:
        raise ValueError(
            "Some artists have conflicting country assignments: "
            + ", ".join(conflicting_artists.index.tolist()[:10])
        )

    # Keep one row per artist
    artist_mapping = artist_mapping.drop_duplicates(
        subset="_artist_key",
        keep="first"
    )

    # --------------------------------------------------
    # 4. Merge artist-country information
    # --------------------------------------------------

    df = df.merge(
        artist_mapping.drop(
            columns=["artist_name"]
        ),
        on="_artist_key",
        how="left",
        validate="many_to_one"
    )

    # Remove temporary matching column
    df = df.drop(
        columns=["_artist_key"]
    )

    # --------------------------------------------------
    # 5. Create regression variables
    # --------------------------------------------------

    df["log_price"] = np.log(
        df["real_price_usd"]
    )

    df["log_size"] = np.where(
        (df["height"] > 0)
        & (df["width"] > 0),
        np.log(df["height"] * df["width"]),
        np.nan
    )

    # --------------------------------------------------
    # 6. Print diagnostics
    # --------------------------------------------------

    print("\n========== DATASET DIAGNOSTICS ==========")

    print("Total observations:", len(df))

    print(
        "Missing real prices:",
        df["real_price_usd"].isna().sum()
    )

    print(
        "Missing artist countries:",
        df["artist_country"].isna().sum()
    )

    print(
        "Valid regression prices:",
        df["log_price"].notna().sum()
    )

    print(
        "Valid artist countries:",
        df["artist_country"].notna().sum()
    )

    # Save prepared dataset
    os.makedirs(
        os.path.dirname(OUTPUT_FILE),
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print(f"\nSaved prepared dataset to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
