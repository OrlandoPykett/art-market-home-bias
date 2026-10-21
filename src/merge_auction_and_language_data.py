
import pandas as pd
import numpy as np
from pathlib import Path

from country_mapping import (
    convert_country,
    NATIONALITY_COUNTRY_MAP,
    ARTIST_NATIONALITY_MAP,
    COUNTRY_ABBREVIATION_MAP,
    CEPII_COUNTRY_MAP
)

# ------
# Data
# ------

# Input
transactions = pd.read_csv("data/cleaned/transactions_merged.csv")
languages = pd.read_csv("data/raw/language_proximity.csv")

# Output
OUTPUT_FILE = "data/cleaned/regresions_language_proximity.csv"


# ------
# Apply name maps
# ------

def standardise_cepii_country(country):
    if pd.isna(country):
        return pd.NA

    country = str(country).strip()

    # Countries not represented in CEPII
    if country in {"Palestine", "Yugoslavia"}:
        return pd.NA

    country = convert_country(country)

    if pd.isna(country):
        return pd.NA

    country = str(country).strip()

    # Apply the mapping; retain the original if no mapping exists
    return CEPII_COUNTRY_MAP.get(country, country)


for column in ["artist_country", "sale_country"]:
    transactions[column] = transactions[column].map(
        standardise_cepii_country
    ).astype("string")


# Standardise CEPII country columns too
for column in ["country_o", "country_d"]:
    languages[column] = (
        languages[column]
        .astype("string")
        .str.strip()
        .replace(CEPII_COUNTRY_MAP)
    )


# ------
# Merge
# ------

languages = languages[
    ["country_o", "country_d", "prox1", "prox2", "cl", "col"]
].copy()

# Check uniqueness of country pairs
assert not languages.duplicated(
    ["country_o", "country_d"]
).any()

# Identify domestic transactions before merging
domestic = (
    transactions["artist_country"].fillna("").eq(
        transactions["sale_country"].fillna("!")
    )
    & transactions["artist_country"].notna()
    & transactions["sale_country"].notna()
)

transactions = transactions.merge(
    languages,
    left_on=["artist_country", "sale_country"],
    right_on=["country_o", "country_d"],
    how="left",
    validate="many_to_one",
    indicator=True
)

# Set values for domestic transactions
transactions.loc[domestic, "cl"] = 1

# Domestic transactions have no CEPII self-pair, so they are expected
# to appear as left_only in the original merge.
matched = transactions["_merge"].eq("both")
international = ~domestic

print("\nMerge results:")
print(transactions["_merge"].value_counts())

print("\nDomestic transactions:")
print("Count:", int(domestic.sum()))
print("cl = 1:", int(transactions.loc[domestic, "cl"].eq(1).sum()))

print("\nInternational transactions:")
print("Count:", int(international.sum()))
print("Matched:", int((matched & international).sum()))
print("Unmatched:", int((~matched & international).sum()))

international_count = int(international.sum())

if international_count > 0:
    print(
        "International match rate:",
        (matched & international).sum() / international_count
    )

print(
    "Overall match rate excluding domestic transactions:",
    (matched & international).sum() / international_count
    if international_count > 0
    else np.nan
)


# Show the most common unmatched international country pairs
print("\nMost common unmatched international pairs:")
print(
    transactions.loc[
        (~matched) & international,
        ["artist_country", "sale_country"]
    ]
    .value_counts()
    .head(20)
)

# ------
# Save
# ------

transactions.drop(
    columns=["country_o", "country_d", "_merge"],
    inplace=True
)

Path(OUTPUT_FILE).parent.mkdir(parents=True, exist_ok=True)

transactions.to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved to {OUTPUT_FILE}")
