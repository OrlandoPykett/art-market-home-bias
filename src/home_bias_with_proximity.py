import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import datetime

from country_mapping import (
    convert_country,
    map_sale_country,
    CITY_COUNTRY_MAP,
    NATIONALITY_COUNTRY_MAP,
    ARTIST_NATIONALITY_MAP,
    CEPII_COUNTRY_MAP
)

# Data
# DF1 has 114283 observations
# DF2 has 16226 observations
# See -- for each dataset's variable list

df1 = pd.read_csv("data/cleaned/dataset1_cleaned_proximity.csv",
                  encoding="latin1",
                  low_memory=False
                  )
df2 = pd.read_csv("data/cleaned/dataset2_cleaned.csv",
                  encoding="latin1",
                  low_memory=False
                  )

print("Rows loaded:", len(df1))

# Standardise contry names
for data in [df1]:
    for col in ["artist_country", "sale_country"]:
        if col not in data.columns:
            raise ValueError(
                f"Missing column '{col}'. Available columns: "
                f"{data.columns.tolist()}"
            )

        data[col] = data[col].apply(convert_country)


# ------
# Concat datasets | Currently only uses dataset 1
# ------
# TODO check for duplicates
df = pd.concat([df1], ignore_index=True)

time_now = datetime.datetime.now()

print("-" * 20)
print(f"Programme started at: {time_now}")
print("-" * 20)

print(f"\nLoaded {len(df):,} observations.")


# ------
# Variables
# ------

# Minimum columns necessary to estimate a price associated with a country-pair
required_columns = [
    "artist_name",
    "artist_country",
    "sale_country",
    "sale_y",
    "real_price_usd"
]

# Check that all necessary columns exist
missing_columns = [
    col for col in required_columns if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}. "
        "Standardise the column names in both datasets first."
    )

# Drop observations only if an essential variable is missing
df = df.dropna(subset=required_columns).copy()

# Convert numeric columns
numeric_columns = [
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

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Dependent variable: log real price
df = df[df["real_price_usd"] > 0].copy()
df["ln_real_price"] = np.log(df["real_price_usd"])

print(f"Observations after essential-variable filtering: {len(df):,}")

# ------
# Handle missing predictors
# ------

# Numeric predictors: median imputation + missingness indicators
numeric_predictors = [
    "height",
    "width",
    "artwork_y"
]

for col in numeric_predictors:
    if col in df.columns:
        missing_col = f"{col}_missing"
        df[missing_col] = df[col].isna().astype(int)

        median_value = df[col].median()

        if pd.notna(median_value):
            df[col] = df[col].fillna(median_value)

# Categorical predictors: give missing values their own category
categorical_predictors = [
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

for col in categorical_predictors:
    if col in df.columns:
        df[col] = df[col].fillna("Unknown").astype(str)

# Do not impute sale_y: it is an essential variable.
# Treat it as a categorical year in the regression.


# ------
# Home bias variable
# ------

# Normalise country strings consistently.
for col in ["artist_country", "sale_country"]:
    df[col] = (
        df[col]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

# Exclude placeholders that should not count as known countries.
invalid_countries = ["nan", "none", "null", "unknown", "n/a"]

for col in ["artist_country", "sale_country"]:
    df.loc[
        df[col].str.lower().isin(invalid_countries).fillna(False),
        col
    ] = pd.NA

# 1 = home sale; 0 = foreign sale.
valid_location = (
    df["artist_country"].notna()
    & df["sale_country"].notna()
)

df["home_bias"] = np.nan

df.loc[valid_location, "home_bias"] = (
    df.loc[valid_location, "artist_country"]
    == df.loc[valid_location, "sale_country"]
).astype(int)

# Equivalent indicator used by the country-pair model.
df["foreign_market"] = np.nan

df.loc[valid_location, "foreign_market"] = (
    1 - df.loc[valid_location, "home_bias"]
)


# ------
# OLS model
# ------

# Construct log price and log size
df["log_price"] = np.log(df["real_price_usd"])

valid_area = df["height"].gt(0) & df["width"].gt(0)
valid_volume = valid_area & df["depth"].gt(0)

df["artwork_area"] = np.nan
df.loc[valid_area, "artwork_area"] = (
    df.loc[valid_area, "height"] * df.loc[valid_area, "width"]
)

df["artwork_volume"] = np.nan
df.loc[valid_volume, "artwork_volume"] = (
    df.loc[valid_volume, "height"]
    * df.loc[valid_volume, "width"]
    * df.loc[valid_volume, "depth"]
)

df["size_measure"] = df["artwork_volume"].fillna(df["artwork_area"])
df["log_size"] = np.log(df["size_measure"])


# ------
# Formula
# ------
# Uses prox2 as for language proximity
# TODO test with prox1 and cl
formula = """
log_price ~
home_bias
+ prox2
+ log_size
+ C(artist_name)
+ C(auction_house)
+ C(sale_y)
+ C(materials)
"""

# Use only observations with complete model variables
analysis_df = df.dropna(
    subset=[
        "log_price",
        "home_bias",
        "log_size",
        "artist_name",
        "auction_house",
        "sale_y",
        "materials"
    ]
).copy()

analysis_df = analysis_df[
    np.isfinite(analysis_df["log_price"])
    & np.isfinite(analysis_df["log_size"])
].copy()

model = smf.ols(
    formula=formula,
    data=analysis_df
).fit(cov_type="HC1")



print("Observations used:", int(model.nobs))
print("Home-bias coefficient:", model.params["home_bias"])
print("Language proximity coefficient:", model.params["prox2"])
print("Implied price difference:",
      f"{(np.exp(model.params['home_bias']) - 1) * 100:.2f}%")
print("P-value:", model.pvalues["home_bias"])

variables = ["home_bias", "prox2","log_size"]

results_table = pd.DataFrame({
    "Coefficient": model.params[variables],
    "Std. Error": model.bse[variables],
    "P-value": model.pvalues[variables]
})

print("\nRegression results:")
print(results_table.round(4).to_string())
print("\nArtist, auction-house, year and materials fixed effects included.")