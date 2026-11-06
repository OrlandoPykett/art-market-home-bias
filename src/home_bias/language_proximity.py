"""Bilateral language proximity (CEPII): prepare and merge only."""

import pandas as pd

from src.shared.country_mapping import convert_country
from src.shared.non_destructive_merge import merge_on_keys


def add_language_proximity(df, language_file):
    lang = pd.read_csv(language_file)

    # CEPII names -> your canonical names
    for col in ["country_o", "country_d"]:
        lang[col] = lang[col].apply(convert_country)

    lang = lang.rename(columns={
        "country_o": "artist_country",
        "country_d": "sale_country",
        "prox2": "language_proximity",
    })
    lang["language_proximity"] = pd.to_numeric(
        lang["language_proximity"], errors="coerce"
    )

    df = merge_on_keys(
        df, lang,
        keys=["artist_country", "sale_country"],
        value_cols=["language_proximity"],
        label="language_proximity",
    )

    # Domestic pairs: proximity defined as 0
    domestic = (
        df["artist_country"].notna()
        & (df["artist_country"] == df["sale_country"])
    )
    df.loc[domestic, "language_proximity"] = 0
    print(f"Domestic observations set to 0: {domestic.sum():,}")

    return df