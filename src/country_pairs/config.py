import os

# File paths
# --------------------

INPUT_FILE = "data/cleaned/dataset1_cleaned.csv"

OUTPUT_FILE = "results/country_pair_regressions.csv"
ARTIST_BREAKDOWN_FILE = "results/pair_artist_breakdown.csv"
EXCLUSIONS_FILE = "results/country_pair_exclusions.csv"


# Regression parameters
# --------------------

MIN_ARTIST_MARKET_OBSERVATIONS = 3

MIN_PAIR_OBSERVATIONS = 50
MIN_HOME_OBSERVATIONS = 20
MIN_FOREIGN_OBSERVATIONS = 20
MIN_COMMON_ARTISTS = 5


# Required columns
# --------------------

REQUIRED_COLUMNS = [
    "artist_country",
    "sale_country",
    "real_price_usd",
    "height",
    "width",
    "depth",
    "artist_name",
    "auction_house",
    "sale_y",
    "materials"
]


# Columns to clean
# --------------------

CATEGORICAL_COLUMNS = [
    "artist_country",
    "sale_country",
    "artist_name",
    "auction_house",
    "materials"
]

NUMERIC_COLUMNS = [
    "real_price_usd",
    "height",
    "width",
    "depth",
    "sale_y"
]


# Country pairs for inspection
# --------------------

INSPECT_PAIRS = [
    ("United States", "United Kingdom"),
    ("United States", "Germany"),
    ("Germany", "Switzerland"),
    ("France", "Germany")
]