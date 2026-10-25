
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

from pathlib import Path
from country_mapping import convert_country


# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_FILE = "data/cleaned/dataset1_cleaned.csv"

OUTPUT_FILE = "results/country_pair_regressions_simple.csv"
EXCLUSIONS_FILE = "results/country_pair_regressions_exclusions.csv"

# Robustness parameters
MIN_ARTIST_MARKET_OBSERVATIONS = 5
MIN_PAIR_OBSERVATIONS = 50
MIN_HOME_OBSERVATIONS = 20
MIN_FOREIGN_OBSERVATIONS = 20
MIN_COMMON_ARTISTS = 5

# Ensure the output directory exists.
Path("results").mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Load data and standardise country names
# --------------------------------------------------

df = pd.read_csv(
    INPUT_FILE,
    encoding="latin1",
    low_memory=False
)

print(f"Loaded {len(df):,} observations.")

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
        + "\n".join(f"  - {col}" for col in missing_columns)
    )

# IMPORTANT:
# Apply the existing mapping function BEFORE comparing countries.
# This converts country identifiers and city names according
# to the rules already implemented in country_mapping.py.

for col in ["artist_country", "sale_country"]:
    df[col] = df[col].apply(convert_country)

# Normalise categorical fields without converting missing values
# into the literal string "nan".
categorical_columns = [
    "artist_country",
    "sale_country",
    "artist_name",
    "auction_house",
    "materials",
]

for column in categorical_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

# Remove placeholders from categorical variables.
invalid_categories = [
    "nan", "none", "null", "unknown", "n/a"
]

for column in categorical_columns:
    df = df[
        ~df[column].str.lower().isin(invalid_categories)
    ].copy()

# Convert numeric variables.
for column in [
    "real_price_usd",
    "height",
    "width",
    "depth",
    "sale_y",
]:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# --------------------------------------------------
# Dependent variable: log real price
# --------------------------------------------------

df = df[
    df["real_price_usd"].gt(0)
    & df["real_price_usd"].notna()
].copy()

df["log_price"] = np.log(df["real_price_usd"])


# --------------------------------------------------
# Calculate artwork size
# Volume when all three dimensions are available;
# otherwise use height x width.
# --------------------------------------------------

valid_height_width = (
    df["height"].gt(0)
    & df["width"].gt(0)
)

valid_volume = (
    valid_height_width
    & df["depth"].gt(0)
)

df["size"] = np.nan

df.loc[valid_height_width, "size"] = (
    df.loc[valid_height_width, "height"]
    * df.loc[valid_height_width, "width"]
)

df.loc[valid_volume, "size"] = (
    df.loc[valid_volume, "height"]
    * df.loc[valid_volume, "width"]
    * df.loc[valid_volume, "depth"]
)

df["log_size"] = np.log(df["size"])

# Keep observations with all model variables.
df = df.dropna(
    subset=[
        "artist_country",
        "sale_country",
        "log_price",
        "log_size",
        "artist_name",
        "auction_house",
        "sale_y",
        "materials",
    ]
).copy()

# Exclude infinite values.
df = df[
    np.isfinite(df["log_price"])
    & np.isfinite(df["log_size"])
].copy()


# --------------------------------------------------
# Diagnostics: verify country mapping
# --------------------------------------------------

home_mask = (
    df["artist_country"].notna()
    & df["sale_country"].notna()
    & (
        df["artist_country"]
        == df["sale_country"]
    )
)

print(f"Usable observations: {len(df):,}")
print(f"Artist countries: {df['artist_country'].nunique()}")
print(f"Sale countries: {df['sale_country'].nunique()}")
print(f"Home-market observations: {int(home_mask.sum()):,}")
print(f"Foreign-market observations: {int((~home_mask).sum()):,}")

print("\nMost common mapped sale countries:")
print(df["sale_country"].value_counts().head(15).to_string())

if home_mask.sum() == 0:
    raise ValueError(
        "No home-market observations found after convert_country(). "
        "Inspect the outputs of convert_country() for artist_country "
        "and sale_country before running the regressions."
    )


# --------------------------------------------------
# Country-pair regressions
# --------------------------------------------------

results = []
exclusions = []

pairs_considered = 0
pairs_with_common_artists = 0
pairs_passing_filters = 0

artist_countries = sorted(
    df["artist_country"].unique()
)

for artist_country in artist_countries:

    # Restrict to artists of this nationality.
    artist_df = df[
        df["artist_country"] == artist_country
    ]

    # Every sale country other than the artist's home country.
    foreign_countries = sorted(
        artist_df.loc[
            artist_df["sale_country"] != artist_country,
            "sale_country"
        ].unique()
    )

    for foreign_country in foreign_countries:

        pairs_considered += 1

        # Retain only home and the selected foreign market.
        candidate_df = artist_df[
            artist_df["sale_country"].isin(
                [artist_country, foreign_country]
            )
        ].copy()

        # Count sales by artist in each market.
        counts = (
            candidate_df
            .groupby(["artist_name", "sale_country"])
            .size()
            .unstack(fill_value=0)
        )

        if (
            artist_country not in counts.columns
            or foreign_country not in counts.columns
        ):
            continue

        # An artist must have sufficient observations in BOTH markets.
        qualifying = counts[
            (
                counts[artist_country]
                >= MIN_ARTIST_MARKET_OBSERVATIONS
            )
            & (
                counts[foreign_country]
                >= MIN_ARTIST_MARKET_OBSERVATIONS
            )
        ].index

        common_n = len(qualifying)

        if common_n > 0:
            pairs_with_common_artists += 1

        pair_df = candidate_df[
            candidate_df["artist_name"].isin(qualifying)
        ].copy()

        home_n = int(
            (pair_df["sale_country"] == artist_country).sum()
        )

        foreign_n = int(
            (pair_df["sale_country"] == foreign_country).sum()
        )

        pair_n = len(pair_df)

        # Apply the pair-level eligibility requirements.
        reason = None

        if common_n < MIN_COMMON_ARTISTS:
            reason = "Too few qualifying artists"

        elif pair_n < MIN_PAIR_OBSERVATIONS:
            reason = "Too few total observations"

        elif home_n < MIN_HOME_OBSERVATIONS:
            reason = "Too few home-market observations"

        elif foreign_n < MIN_FOREIGN_OBSERVATIONS:
            reason = "Too few foreign-market observations"

        if reason:
            exclusions.append({
                "artist_country": artist_country,
                "foreign_sale_country": foreign_country,
                "qualifying_artists": common_n,
                "pair_observations": pair_n,
                "home_observations": home_n,
                "foreign_observations": foreign_n,
                "exclusion_reason": reason,
            })
            continue

        pairs_passing_filters += 1

        # 0 = home market; 1 = foreign market.
        pair_df["foreign_market"] = (
            pair_df["sale_country"] == foreign_country
        ).astype(int)

        # Regression:
        # Artist, auction-house, year and materials fixed effects.
        formula = (
            "log_price ~ foreign_market "
            "+ log_size "
            "+ C(artist_name) "
            "+ C(auction_house) "
            "+ C(sale_y) "
            "+ C(materials)"
        )

        try:
            model = smf.ols(
                formula=formula,
                data=pair_df
            ).fit(
                cov_type="cluster",
                cov_kwds={
                    "groups": pair_df["artist_name"]
                }
            )

            # Extract the foreign-market effect.
            coefficient = model.params["foreign_market"]
            std_error = model.bse["foreign_market"]
            p_value = model.pvalues["foreign_market"]

            ci_low, ci_high = model.conf_int().loc[
                "foreign_market"
            ].tolist()

            # Convert log-point estimates into percentage changes.
            effect_pct = 100 * np.expm1(coefficient)
            effect_ci_low = 100 * np.expm1(ci_low)
            effect_ci_high = 100 * np.expm1(ci_high)

            results.append({
                "artist_country": artist_country,
                "foreign_sale_country": foreign_country,
                "foreign_effect_percentage": effect_pct,
                "std_error": std_error,
                "p_value": p_value,
                "ci_lower_percentage": effect_ci_low,
                "ci_upper_percentage": effect_ci_high,
                "pair_observations": pair_n,
                "home_observations": home_n,
                "foreign_observations": foreign_n,
                "qualifying_artists": common_n,
                "r_squared": model.rsquared,
            })

        except Exception as e:
            exclusions.append({
                "artist_country": artist_country,
                "foreign_sale_country": foreign_country,
                "qualifying_artists": common_n,
                "pair_observations": pair_n,
                "home_observations": home_n,
                "foreign_observations": foreign_n,
                "exclusion_reason": f"Regression error: {e}",
            })


# --------------------------------------------------
# Save results and exclusions
# --------------------------------------------------

results_columns = [
    "artist_country",
    "foreign_sale_country",
    "foreign_effect_percentage",
    #"std_error",
    "p_value",
    #"ci_lower_percentage",
    #"ci_upper_percentage",
    #"pair_observations",
    #"home_observations",
    #"foreign_observations",
    #"qualifying_artists",
    #"r_squared",
]

exclusion_columns = [
    "artist_country",
    "foreign_sale_country",
    "qualifying_artists",
    "pair_observations",
    "home_observations",
    "foreign_observations",
    "exclusion_reason",
]

results_df = pd.DataFrame(
    results,
    columns=results_columns
)

exclusions_df = pd.DataFrame(
    exclusions,
    columns=exclusion_columns
)

results_df.to_csv(
    OUTPUT_FILE,
    index=False
)

exclusions_df.to_csv(
    EXCLUSIONS_FILE,
    index=False
)


# --------------------------------------------------
# Final diagnostics
# --------------------------------------------------

print("\n--- PAIR DIAGNOSTICS ---")
print("Pairs considered:", pairs_considered)
print("Pairs with common qualifying artists:",
      pairs_with_common_artists)
print("Pairs passing all filters:", pairs_passing_filters)
print("Successful regressions:", len(results_df))
print("Excluded pairs:", len(exclusions_df))

print("\n--- OUTPUT FILES ---")
print("Results:", Path(OUTPUT_FILE).resolve())
print("Exclusions:", Path(EXCLUSIONS_FILE).resolve())
