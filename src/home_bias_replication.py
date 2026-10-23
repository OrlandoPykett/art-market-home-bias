import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from pathlib import Path
import datetime


df = pd.read_csv("data/cleaned/dataset1_cleaned.csv", encoding="latin1", low_memory=False)

OUTPUT_CLEAN = "results/home_bias_cleaned.csv"
OUTPUT_RESULTS = "results/home_bias_results.txt"

# Minimum number of observations an artist needs to be retained.
# Vosilov uses 1
MIN_ARTIST_OBS = 1

time_now = datetime.datetime.now()

print("-" * 20)
print(f"Programme started at: {time_now}")
print("-" * 20)
print(f"\nLoaded {len(df):,} observations.")
print(f"Number of columns: {len(df.columns)}")

print("\nColumns:")
for col in df.columns:
    print(f"  {col}")

# Check that dataset has the required columns

required_columns = [
    "artist_name",
    "artist_country",
    "sale_country",
    "auction_house",
    "sale_y",
    "materials",
    "height",
    "width",
    "depth",
    "real_price_usd",
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        "\nMissing required columns:\n"
        + "\n".join(f"  - {x}" for x in missing_columns)
    )


string_columns = [
    "artist_name",
    "artist_country",
    "sale_country",
    "auction_house",
    "sale_y",
    "materials",
    "height",
    "width",
    "depth",
    "size",
    "log_size",
    "real_price_usd",
    "ln_real_price",
    "data_source",
]

for col in string_columns:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip()


# Convert numeric variables
numeric_columns = [
    "real_price_usd",
    "ln_real_price",
    "sale_y",
    "Year of Birth",
    "year_of_artwork",
    "height",
    "width",
    "depth",
    "estimate_min",
    "estimate_max",
]

for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").astype("float64")


# ------
# Construct log real price
# ------

df["analysis_price"] = pd.to_numeric(
    df["real_price_usd"],
    errors="coerce"
)

if "price_usd" in df.columns:
    df["analysis_price"] = df["analysis_price"].fillna(
        pd.to_numeric(df["price_usd"], errors="coerce")
    )

# Remove zero/negative prices
df.loc[df["analysis_price"] <= 0, "analysis_price"] = np.nan

df["log_price"] = np.log(df["analysis_price"])


# ------
# Construct artwork size
# ------

'''
When depth exists:
    volume = height × width × depth

Otherwise:
    area = height × width
'''

valid_area = (
    df["height"].gt(0)
    & df["width"].gt(0)
)

valid_volume = (
    valid_area
    & df["depth"].gt(0)
)

df["artwork_area"] = np.nan
df.loc[valid_area, "artwork_area"] = (
    df.loc[valid_area, "height"]
    * df.loc[valid_area, "width"]
)

df["artwork_volume"] = np.nan
df.loc[valid_volume, "artwork_volume"] = (
    df.loc[valid_volume, "height"]
    * df.loc[valid_volume, "width"]
    * df.loc[valid_volume, "depth"]
)

df["size_measure"] = df["artwork_volume"].fillna(
    df["artwork_area"]
)

df["log_size"] = np.log(df["size_measure"])


# ------
# Artist age and alive dummy
# ------

'''
Vosilov uses a dummy variable for the artist being alive
The current dataset does not contain any suitable variable for alive/dead
The absence of such a dummy makes the pricing model less accurate
For this study the absence of such a variable should not be of too much importance
Accurate price differences are more important than accurate prices
'''

# ------
# Home bias variable
# ------

'''
HomeBias = 1 if:
    artist's nationality == auction country

HomeBias = 0 if:
    artist nationality != auction country

Variables are only assigned where both countries are known.
'''

df["home_bias"] = np.nan

valid_location = (
    df["sale_country"].notna()
    & df["artist_country"].notna()
)

df.loc[
    valid_location,
    "home_bias"
] = (
    df.loc[
        valid_location,
        "artist_country"
    ]
    ==
    df.loc[
        valid_location,
        "sale_country"
    ]
).astype(int)


print("\nHome-bias observations:")

print(
    df["home_bias"]
    .value_counts(dropna=False)
)

print("\nHome-bias percentage among observations with both")
print("artist nationality and auction country:")

if valid_location.sum() > 0:

    print(
        df.loc[
            valid_location,
            "home_bias"
        ].mean() * 100,
        "%"
    )


# ------
# Unmapped locations
# ------

if "country" in df.columns:
    unmapped = (
        df.loc[
            df["sale_country"].isna()
            & df["artist_country"].notna(),
            "country"
        ]
        .value_counts()
    )

    if len(unmapped) > 0:
        print("\nUnmapped sale-country values:")
        print(unmapped.head(100))
else:
    print("\nNo raw 'country' column available for unmapped-location check.")


# ------
# Create regression sample
# ------

analysis_vars = [
    "log_price",
    "home_bias",
    "artist_name",
    "auction_house",
    "sale_y",
    "materials",
    "log_size",
]

analysis_df = df.dropna(
    subset=analysis_vars
).copy()


# Remove extremely unusual values
analysis_df = analysis_df[
    np.isfinite(analysis_df["log_price"])
    & np.isfinite(analysis_df["log_size"])
]


# Optional artist-frequency restriction
if MIN_ARTIST_OBS > 1:

    artist_counts = (
        analysis_df["artist_name"]
        .value_counts()
    )

    valid_artists = artist_counts[
        artist_counts >= MIN_ARTIST_OBS
    ].index

    analysis_df = analysis_df[
        analysis_df["artist_name"].isin(valid_artists)
    ]


print("\n" + "-" * 20)
print("REGRESSION SAMPLE")
print("-" * 20)

print(
    f"\nFull dataset:       {len(df):,}"
)

print(
    f"Regression sample:  {len(analysis_df):,}"
)

print(
    f"Artists:            "
    f"{analysis_df['artist_name'].nunique():,}"
)

print(
    f"Auction houses:     "
    f"{analysis_df['auction_house'].nunique():,}"
)

print(
    f"Years:              "
    f"{analysis_df['sale_y'].min():.0f}–"
    f"{analysis_df['sale_y'].max():.0f}"
)


# ------
# OLS Regression
# ------

print("\n" + "-" * 20)
print("OLS HOME-BIAS REGRESSION")
print("-" * 20)

#
# The specification follows Vosilov's basic hedonic structure:
#
# log(price)
#     = HomeBias
#     + artist controls
#     + auction-house controls
#     + year controls
#     + medium controls
#     + size
#
# 
#

formula = """
log_price ~
home_bias
+ log_size
+ C(artist_name)
+ C(auction_house)
+ C(sale_y)
+ C(materials)
"""


ols_model = smf.ols(
    formula=formula,
    data=analysis_df
).fit(
    cov_type="HC1"
)


print(
    ols_model.summary()
)


# Home-bias coefficient
beta = ols_model.params["home_bias"]

percentage_effect = (
    np.exp(beta) - 1
) * 100

print("\n" + "-" * 70)

print(
    f"HomeBias coefficient: {beta:.4f}"
)

print(
    f"Implied price difference: "
    f"{percentage_effect:.2f}%"
)

print(
    f"p-value: "
    f"{ols_model.pvalues['home_bias']:.6f}"
)

print("-" * 70)


# ------
# 10th quantile regression
# ------

print("\n" + "-" * 20)
print("10TH QUANTILE REGRESSION")
print("-" * 20)

quantile_10 = smf.quantreg(
    formula,
    analysis_df
).fit(
    q=0.10,
    max_iter=5000
)

print(
    quantile_10.summary()
)


# ------
# 90th quantile regression
# ------

print("\n" + "-" * 20)
print("90TH QUANTILE REGRESSION")
print("-" * 20)

quantile_90 = smf.quantreg(
    formula,
    analysis_df
).fit(
    q=0.90,
    max_iter=5000
)

print(
    quantile_90.summary()
)


# ------
# Compare quantiles
# ------

q10_beta = quantile_10.params["home_bias"]
q90_beta = quantile_90.params["home_bias"]

q10_effect = (
    np.exp(q10_beta) - 1
) * 100

q90_effect = (
    np.exp(q90_beta) - 1
) * 100

print("\n" + "-" * 20)
print("QUANTILE COMPARISON")
print("-" * 20)

print(
    f"""
                    10th percentile     90th percentile

HomeBias coefficient      {q10_beta:8.4f}          {q90_beta:8.4f}

Implied price effect      {q10_effect:8.2f}%          {q90_effect:8.2f}%
"""
)


# ------
# Descriptive statistics
# ------

print("\n" + "-" * 20)
print("DESCRIPTIVE STATISTICS")
print("-" * 20)

print(
    analysis_df[
        [
            "analysis_price",
            "log_price",
            "home_bias",
            "log_size",
            "sale_y",
        ]
    ].describe()
)


# ------
# Home vs Foreign mean prices
# ------

print("\n" + "-" * 20)
print("HOME VS FOREIGN SALES")
print("-" * 20)

comparison = (
    analysis_df
    .groupby("home_bias")["analysis_price"]
    .agg(
        [
            "count",
            "mean",
            "median",
        ]
    )
)

comparison.index = [
    "Foreign sale",
    "Home sale",
]

print(comparison)


# ------
# Home-bias by artist country
# ------

print("\n" + "-" * 20)
print("HOME BIAS BY ARTIST COUNTRY")
print("-" * 20)

country_summary = (
    analysis_df
    .groupby("artist_country", dropna=False)
    .agg(
        observations=("home_bias", "size"),
        home_sales=("home_bias", "sum"),
        home_share=("home_bias", "mean"),
        median_price=("analysis_price", "median"),
    )
    .sort_values(
        "observations",
        ascending=False
    )
)

print(
    country_summary.head(30)
)


# ------
# Save clean data
# ------

analysis_df.to_csv(
    OUTPUT_CLEAN,
    index=False
)

print(
    f"\nCleaned regression dataset saved to:"
    f"\n  {OUTPUT_CLEAN}"
)


# ------
# Save results
# ------

with open(
    OUTPUT_RESULTS,
    "w",
    encoding="utf-8"
) as f:

    f.write(
        "ART AUCTION HOME-BIAS ANALYSIS\n"
    )

    f.write(
        "=" * 70 + "\n\n"
    )

    f.write(
        "Main OLS regression\n"
    )

    f.write(
        str(ols_model.summary())
    )

    f.write(
        "\n\n"
        "HomeBias coefficient: "
        f"{beta:.6f}\n"
    )

    f.write(
        "Implied price effect: "
        f"{percentage_effect:.4f}%\n"
    )

    f.write(
        "\n\n10th quantile regression\n"
    )

    f.write(
        str(quantile_10.summary())
    )

    f.write(
        "\n\n90th quantile regression\n"
    )

    f.write(
        str(quantile_90.summary())
    )

    f.write(
        "\n\nQUANTILE COMPARISON\n"
    )

    f.write(
        f"\n10th percentile HomeBias: {q10_beta:.6f}"
    )

    f.write(
        f"\n90th percentile HomeBias: {q90_beta:.6f}"
    )

    f.write(
        f"\n10th percentile effect: {q10_effect:.4f}%"
    )

    f.write(
        f"\n90th percentile effect: {q90_effect:.4f}%"
    )


print(
    f"Regression results saved to:"
    f"\n  {OUTPUT_RESULTS}"
)

print("\nAnalysis complete.")