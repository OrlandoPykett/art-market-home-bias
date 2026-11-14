"""
Project configuration

Contains file paths, variable efinitions and model specifications
"""

from pathlib import Path

# File paths
# --------------------

TEST_FILE = "data/cleaned/test_dataset.csv"
TRAIN_FILE = "data/cleaned/train_dataset.csv"
PAIR_DATA_FILE = "results/training_regressions.csv"
PAIR_ARTIST_FILE = Path(PAIR_DATA_FILE).with_name("qualifying_artists.csv")

OUTPUT_FILE = "results/home_bias_regression_train_test_split.csv"


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