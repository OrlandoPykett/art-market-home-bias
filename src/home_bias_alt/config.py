"""
Project configuration

Contains file paths, variable definitions and model specifications.
"""

# File paths
# --------------------

DATASET_FILE = "data/cleaned/dataset2_regression_ready.csv"

OUTPUT_FILE = "results/home_bias_regression_alt.csv"


# Regression
# --------------------

REGRESSION_FORMULA = """
log_price ~
home_bias
+ log_size
+ C(artist_name)
+ C(auction_house)
+ C(sale_y)
+ C(medium)
+ C(signed)
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
    "height",
    "width",
    "diameter",
    "price",
    "price_usd",
    "real_price_usd",
    "sale_y",
    "artwork_y",
    "CNV_RATE",
    "uscpi"
]

NUMERIC_PREDICTORS = [
    "height",
    "width",
    "diameter",
    "artwork_y",
    "CNV_RATE"
]

CATEGORICAL_PREDICTORS = [
    "shape",
    "signed",
    "medium",
    "illustration",
    "auction_house",
    "artist_name",
    "sale_country"
]
