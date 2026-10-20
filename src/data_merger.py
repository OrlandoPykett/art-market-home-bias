import pandas as pd
import numpy as np

from country_mapping import (
    convert_country,
    NATIONALITY_COUNTRY_MAPPING,
    ARTIST_NATIONALITY_MAPPING,
    country_abbreviation_map
)

# ------
# Data
# ------

# Input
TRANSACTIONS_FILE = "data/raw/transactions.csv"
IMPRESSIONIST_FILE = "data/impressionist_art.csv"

# Output
OUTPUT_FILE = "data/transactions_merged.csv"


# ------
# Load data
# ------

old = pd.read_csv(TRANSACTIONS_FILE, encoding="latin1")
impress = pd.read_csv(IMPRESSIONIST_FILE, encoding="latin1")


import pandas as pd

df = pd.read_csv("transactions_merged.csv")

print("TOTAL OBSERVATIONS:", len(df))

print("\n--- MISSING VALUES ---")
print(df.isna().sum().sort_values(ascending=False))

print("\n--- ARTIST COUNTRY ---")
print(df["artist_country"].isna().sum(), "missing")

print("\n--- SALE COUNTRY ---")
print(df["sale_country"].isna().sum(), "missing")

print("\n--- AUCTION HOUSE ---")
print(df["auction_house"].isna().sum(), "missing")

print("\n--- EVENT YEAR ---")
print(df["event_year"].isna().sum(), "missing")

print("\n--- PRICE ---")
print(df["real_price_usd"].isna().sum(), "missing")

print("\n--- SIZE ---")
print(df["size"].isna().sum(), "missing")

# ------
# Standardise data
# ------

# transctions.csv

old["artist_name"] = old["artist_name"].astype(str).str.strip()

# Artist nationality -> artist country
old["artist_country"] = (
    old["nationality"]
    .map(NATIONALITY_COUNTRY_MAPPING)
)

# Auction country -> sale country
old["sale_country"] = (
    old["country"]
    .apply(convert_country)
)

# Clean numeric variables
for col in ["height", "width", "depth", "real_price_usd"]:
    old[col] = pd.to_numeric(old[col], errors="coerce")

# Recalculate size
old["size"] = old["height"] * old["width"]

# Recalculate log size
old["log_size"] = np.log(old["size"].replace(0, np.nan))

# Recalculate log price
old["ln_real_price"] = np.log(
    old["real_price_usd"].replace(0, np.nan)
)

old["data_source"] = "transactions"

# impressionst_art.csv

# Artist name
impress["artist_name"] = (
    impress["ANAME"]
    .astype(str)
    .str.strip()
)

# Artist name -> artist country
impress["artist_country"] = (
    impress["artist_name"]
    .map(ARTIST_NATIONALITY_MAPPING)
)

# LO / NY -> country using existing mapping
impress["sale_country"] = (
    impress["AUCT_LOC"]
    .astype(str)
    .str.strip()
    .map(country_abbreviation_map)
)

# Auction house
impress["auction_house"] = (
    impress["HOUSE"]
    .astype(str)
    .str.strip()
    .map({
        "SO": "Sotheby's",
        "CH": "Christie's"
    })
)

# Sale price
impress["real_price_usd"] = pd.to_numeric(
    impress["S_PRICE"],
    errors="coerce"
)

# Dimensions
impress["height"] = pd.to_numeric(
    impress["DIM_A"],
    errors="coerce"
)

impress["width"] = pd.to_numeric(
    impress["DIM_B"],
    errors="coerce"
)

impress["depth"] = pd.to_numeric(
    impress["DIAM"],
    errors="coerce"
)

# Size
impress["size"] = impress["height"] * impress["width"]

# Log size
impress["log_size"] = np.log(
    impress["size"].replace(0, np.nan)
)

# Log price
impress["ln_real_price"] = np.log(
    impress["real_price_usd"].replace(0, np.nan)
)

# Materials
impress["materials"] = (
    impress["ART_MED"]
    .astype(str)
    .str.strip()
)

# Auction year
impress["event_year"] = pd.to_datetime(
    impress["AUCT_DAT"],
    errors="coerce"
).dt.year

# If AUCT_DAT wasn't interpreted as a date, try ydate
missing_year = impress["event_year"].isna()

impress.loc[missing_year, "event_year"] = pd.to_numeric(
    impress.loc[missing_year, "ydate"],
    errors="coerce"
)

impress["data_source"] = "impressionist"

# ------
# Common variables
# ------

columns = [
    "artist_name",
    "artist_country",
    "sale_country",
    "auction_house",
    "event_year",
    "materials",
    "height",
    "width",
    "depth",
    "size",
    "log_size",
    "real_price_usd",
    "ln_real_price",
    "data_source"
]


old_final = old[columns].copy()
impress_final = impress[columns].copy()

merged = pd.concat(
    [old_final, impress_final],
    ignore_index=True
)


# ------
# Clean
# ------

# Do NOT remove observations during the merge.
# Missing values in individual fields are retained.

merged["event_year"] = pd.to_numeric(
    merged["event_year"],
    errors="coerce"
)

merged = merged.sort_values(
    ["event_year", "artist_name"],
    na_position="last"
).reset_index(drop=True)

merged.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"Saved: {OUTPUT_FILE}")
print(f"Rows: {len(merged):,}")

print("\nRows by source:")
print(merged["data_source"].value_counts())

print("\nMissing values:")
print(merged.isna().sum())

print("\nArtist country:")
print(merged["artist_country"].value_counts(dropna=False).head(20))

print("\nSale country:")
print(merged["sale_country"].value_counts(dropna=False))

print("\nAuction house:")
print(merged["auction_house"].value_counts(dropna=False))

print("\nFirst 10 rows:")
print(merged.head(10).to_string(index=False))