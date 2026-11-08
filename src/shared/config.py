"""
Project configuration

Contains file paths, variable efinitions and model specifications
"""

# File paths
# --------------------

DATASET1_FILE = "data/cleaned/dataset1_cleaned.csv"
DATASET2_FILE = "data/cleaned/dataset2_cleaned.csv"

OUTPUT_FILE = "results/home_bias_regression.csv"

# extras
LANGUAGE_FILE = "data/raw/language_proximity.csv"
WVS_FILE = "data/raw/WVS_Cross-National_Wave_7_csv_v6_0.csv"
EVS_FILE = "data/raw/EVS_2008.csv"


# Regression
# --------------------

REGRESSION_FORMULA = """
log_price ~
home_bias
+ log_size
+ C(artist_name)
+ C(auction_house)
+ C(sale_y)
+ C(materials)
"""

REGRESSION_VARIABLES = [
    "home_bias",
    "log_size"
]


# Variables
# --------------------

# Minimum columns necessary to estimate a price associated with
# an artist-country and sale-country combination.
REQUIRED_COLUMNS = [
    "artist_name",
    "artist_country",
    "sale_country",
    "sale_y",
    "real_price_usd"
]

NUMERIC_COLUMNS = [
    "artist_birth_y",
    "price_usd",
    "real_price_usd",
    "sale_y",
    "artwork_y",
    "height",
    "width",
    "weight",
    "depth"
]

NUMERIC_PREDICTORS = [
    "height",
    "width",
    "artwork_y"
]

CATEGORICAL_PREDICTORS = [
    "materials",
    "genre",
    "auction_house",
    "shape",
    "illustration",
    "auction_location",
    "artist_name",
    "artist_country",
    "sale_country"
]