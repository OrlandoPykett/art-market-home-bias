import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
from statsmodels.regression.linear_model import OLS
from statsmodels.tools import add_constant
from pathlib import Path


# ============================================================
# 1. SETTINGS
# ============================================================

DATA_FILE = "transactions.csv"

OUTPUT_CLEAN = "home_bias_cleaned.csv"
OUTPUT_RESULTS = "home_bias_results.txt"

# Minimum number of observations an artist needs to be retained.
# Set to 1 to follow the paper more closely.
MIN_ARTIST_OBS = 1


# ============================================================
# 2. LOAD DATA
# ============================================================

print("=" * 70)
print("ART AUCTION HOME-BIAS ANALYSIS")
print("=" * 70)

print("\nLoading data...")

df = pd.read_csv(DATA_FILE, encoding="latin1", low_memory=False)

print(f"Loaded {len(df):,} observations.")
print(f"Number of columns: {len(df.columns)}")

print("\nColumns:")
for col in df.columns:
    print(f"  {col}")


# ============================================================
# 3. CHECK REQUIRED COLUMNS
# ============================================================

required_columns = [
    "artist_name",
    "nationality",
    "auction_house",
    "country",
    "price_usd",
    "real_price_usd",
    "ln_real_price",
    "event_year",
    "materials",
    "height",
    "width",
    "depth",
    "Year of Birth",
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


# ============================================================
# 4. BASIC CLEANING
# ============================================================

# Strip whitespace from string variables
string_columns = [
    "artist_name",
    "nationality",
    "auction_house",
    "country",
    "materials",
    "genre",
    "event name",
    "currency",
]

for col in string_columns:
    if col in df.columns:
        df[col] = df[col].astype("string").str.strip()


# Convert numeric variables
numeric_columns = [
    "price_usd",
    "real_price_usd",
    "ln_real_price",
    "event_year",
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
        df[col] = pd.to_numeric(df[col], errors="coerce")


# ============================================================
# 5. CONSTRUCT LOG REAL PRICE
# ============================================================

# Prefer the dataset's real_price_usd.
# If it is missing, fall back to price_usd.

df["analysis_price"] = df["real_price_usd"]

df.loc[
    df["analysis_price"].isna(),
    "analysis_price"
] = df.loc[
    df["analysis_price"].isna(),
    "price_usd"
]

# Remove zero/negative prices
df.loc[df["analysis_price"] <= 0, "analysis_price"] = np.nan

df["log_price"] = np.log(df["analysis_price"])


# ============================================================
# 6. CONSTRUCT ARTWORK SIZE
# ============================================================

# Vosilov uses sculpture size as a control.
#
# Your dataset has height, width and depth.
#
# We construct:
#
#     volume = height × width × depth
#
# when depth exists.
#
# Otherwise:
#
#     area = height × width
#
# and use the available measure.

df["artwork_area"] = (
    df["height"] * df["width"]
)

df["artwork_volume"] = (
    df["height"] *
    df["width"] *
    df["depth"]
)

# Main size variable:
# volume where possible, otherwise area.

df["size_measure"] = df["artwork_volume"]

df.loc[
    df["size_measure"].isna(),
    "size_measure"
] = df.loc[
    df["size_measure"].isna(),
    "artwork_area"
]

df.loc[df["size_measure"] <= 0, "size_measure"] = np.nan

df["log_size"] = np.log(df["size_measure"])


# ============================================================
# 7. ARTIST AGE / LIFE STATUS
# ============================================================

# Year of birth is available in your dataset.
#
# We use event_year - birth_year to construct age.
#
# The original Vosilov study controls for whether the artist
# was deceased at the time of sale.
#
# We need year of death for an exact replication, but your
# dataset does not appear to contain it.
#
# Therefore we use "alive_id" if it contains useful information.
#
# If alive_id is unavailable/useless, this variable is omitted.

if "alive_id" in df.columns:

    print("\nUnique alive_id values:")
    print(df["alive_id"].value_counts(dropna=False).head(20))

    # We deliberately do not assume what the coding means.
    # The program will create an indicator only if it is clearly
    # binary.

    unique_alive = df["alive_id"].dropna().unique()

    if len(unique_alive) <= 3:
        print(
            "\nalive_id appears to be a low-cardinality variable."
        )
        print(
            "You should inspect the values above before interpreting it."
        )


# ============================================================
# 8. AUCTION LOCATION → COUNTRY
# ============================================================

print("\n" + "=" * 70)
print("AUCTION LOCATION")
print("=" * 70)

print("\nMost common values in the dataset's 'country' column:")

print(
    df["country"]
    .value_counts(dropna=False)
    .head(50)
)


# ------------------------------------------------------------
# IMPORTANT
# ------------------------------------------------------------
#
# Your example shows:
#
#     Sotheby | New York
#
# so "country" appears to contain an auction LOCATION,
# not necessarily a country.
#
# We therefore map common auction cities to countries.
#
# Unknown locations are NOT silently classified.
# They become NaN and are excluded from the home-bias regression.
# ------------------------------------------------------------

location_to_country = {

    # United States
    "New York": "United States",
    "New York City": "United States",
    "Los Angeles": "United States",
    "Chicago": "United States",
    "San Francisco": "United States",
    "Boston": "United States",
    "Miami": "United States",
    "Dallas": "United States",
    "Houston": "United States",
    "Las Vegas": "United States",
    "Washington": "United States",

    # United Kingdom
    "London": "United Kingdom",
    "Edinburgh": "United Kingdom",
    "Glasgow": "United Kingdom",
    "Manchester": "United Kingdom",

    # France
    "Paris": "France",
    "Lyon": "France",
    "Nice": "France",
    "Cannes": "France",
    "Toulouse": "France",

    # Germany
    "Berlin": "Germany",
    "Munich": "Germany",
    "Cologne": "Germany",
    "Frankfurt": "Germany",
    "Hamburg": "Germany",
    "Dusseldorf": "Germany",
    "Düsseldorf": "Germany",

    # Italy
    "Milan": "Italy",
    "Rome": "Italy",
    "Florence": "Italy",
    "Turin": "Italy",
    "Venice": "Italy",
    "Naples": "Italy",

    # Switzerland
    "Geneva": "Switzerland",
    "Zurich": "Switzerland",
    "Basel": "Switzerland",
    "Bern": "Switzerland",

    # Austria
    "Vienna": "Austria",
    "Salzburg": "Austria",

    # Netherlands
    "Amsterdam": "Netherlands",
    "Rotterdam": "Netherlands",

    # Belgium
    "Brussels": "Belgium",
    "Antwerp": "Belgium",

    # Spain
    "Madrid": "Spain",
    "Barcelona": "Spain",
    "Valencia": "Spain",
    "Bilbao": "Spain",

    # Portugal
    "Lisbon": "Portugal",
    "Porto": "Portugal",

    # Denmark
    "Copenhagen": "Denmark",

    # Sweden
    "Stockholm": "Sweden",
    "Gothenburg": "Sweden",
    "Malmö": "Sweden",
    "Malmo": "Sweden",

    # Norway
    "Oslo": "Norway",

    # Finland
    "Helsinki": "Finland",

    # Ireland
    "Dublin": "Ireland",

    # China
    "Beijing": "China",
    "Shanghai": "China",
    "Guangzhou": "China",
    "Shenzhen": "China",
    "Hangzhou": "China",

    # Hong Kong
    "Hong Kong": "Hong Kong",

    # Japan
    "Tokyo": "Japan",
    "Osaka": "Japan",
    "Kyoto": "Japan",

    # South Korea
    "Seoul": "South Korea",

    # Singapore
    "Singapore": "Singapore",

    # Australia
    "Sydney": "Australia",
    "Melbourne": "Australia",
    "Brisbane": "Australia",

    # Canada
    "Toronto": "Canada",
    "Montreal": "Canada",
    "Vancouver": "Canada",

    # Brazil
    "Sao Paulo": "Brazil",
    "São Paulo": "Brazil",
    "Rio de Janeiro": "Brazil",

    # Mexico
    "Mexico City": "Mexico",

    # Russia
    "Moscow": "Russia",
    "St Petersburg": "Russia",
    "Saint Petersburg": "Russia",

    # UAE
    "Dubai": "United Arab Emirates",
    "Abu Dhabi": "United Arab Emirates",

    # Israel
    "Tel Aviv": "Israel",

    # India
    "Mumbai": "India",
    "New Delhi": "India",

    # South Africa
    "Johannesburg": "South Africa",
    "Cape Town": "South Africa",
}


def normalize_location(value):

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if value in location_to_country:
        return location_to_country[value]

    # Sometimes a location might contain additional text.
    value_lower = value.lower()

    for city, country in location_to_country.items():

        if city.lower() in value_lower:
            return country

    return np.nan


df["auction_country"] = df["country"].apply(
    normalize_location
)


# ============================================================
# 9. NORMALIZE ARTIST NATIONALITY
# ============================================================

print("\n" + "=" * 70)
print("ARTIST NATIONALITY")
print("=" * 70)

print(
    "\nMost common nationality values:"
)

print(
    df["nationality"]
    .value_counts(dropna=False)
    .head(50)
)


# Map nationality labels to standardized countries.

nationality_map = {

    "American": "United States",
    "USA": "United States",
    "US": "United States",

    "British": "United Kingdom",
    "English": "United Kingdom",
    "Scottish": "United Kingdom",
    "Welsh": "United Kingdom",

    "French": "France",

    "German": "Germany",

    "Italian": "Italy",

    "Spanish": "Spain",

    "Swiss": "Switzerland",

    "Austrian": "Austria",

    "Dutch": "Netherlands",
    "Netherlandish": "Netherlands",

    "Belgian": "Belgium",

    "Danish": "Denmark",

    "Swedish": "Sweden",

    "Norwegian": "Norway",

    "Finnish": "Finland",

    "Irish": "Ireland",

    "Portuguese": "Portugal",

    "Chinese": "China",

    "Japanese": "Japan",

    "Korean": "South Korea",
    "South Korean": "South Korea",

    "Canadian": "Canada",

    "Australian": "Australia",

    "Brazilian": "Brazil",

    "Mexican": "Mexico",

    "Indian": "India",

    "Russian": "Russia",

    "Israeli": "Israel",

    "South African": "South Africa",

    "Singaporean": "Singapore",
}


def normalize_nationality(value):

    if pd.isna(value):
        return np.nan

    value = str(value).strip()

    if value in nationality_map:
        return nationality_map[value]

    return value


df["artist_country"] = df["nationality"].apply(
    normalize_nationality
)


# ============================================================
# 10. HOME BIAS VARIABLE
# ============================================================

# HomeBias = 1 if:
#
#     artist's nationality == auction country
#
# HomeBias = 0 if:
#
#     artist nationality != auction country
#
# We only assign the variable where BOTH countries are known.

df["home_bias"] = np.nan

valid_location = (
    df["artist_country"].notna()
    & df["auction_country"].notna()
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
        "auction_country"
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


# ============================================================
# 11. SHOW UNMAPPED AUCTION LOCATIONS
# ============================================================

print("\n" + "=" * 70)
print("UNMAPPED AUCTION LOCATIONS")
print("=" * 70)

unmapped = (
    df.loc[
        df["auction_country"].isna()
        & df["country"].notna(),
        "country"
    ]
    .value_counts()
)

print(
    f"\nThere are {len(unmapped)} unique auction-location values "
    "that could not be mapped."
)

print(
    "\nTop unmapped values:"
)

print(unmapped.head(100))


# ============================================================
# 12. CREATE REGRESSION SAMPLE
# ============================================================

analysis_vars = [
    "log_price",
    "home_bias",
    "artist_name",
    "auction_house",
    "event_year",
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


print("\n" + "=" * 70)
print("REGRESSION SAMPLE")
print("=" * 70)

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
    f"{analysis_df['event_year'].min():.0f}–"
    f"{analysis_df['event_year'].max():.0f}"
)


# ============================================================
# 13. MAIN OLS REGRESSION
# ============================================================

print("\n" + "=" * 70)
print("OLS HOME-BIAS REGRESSION")
print("=" * 70)

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
# Artist fixed effects are particularly useful here because
# different artists have enormously different price levels.
#

formula = """
log_price ~
home_bias
+ log_size
+ C(artist_name)
+ C(auction_house)
+ C(event_year)
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


# ============================================================
# 14. 10TH QUANTILE REGRESSION
# ============================================================

print("\n" + "=" * 70)
print("10TH QUANTILE REGRESSION")
print("=" * 70)

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


# ============================================================
# 15. 90TH QUANTILE REGRESSION
# ============================================================

print("\n" + "=" * 70)
print("90TH QUANTILE REGRESSION")
print("=" * 70)

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


# ============================================================
# 16. COMPARE QUANTILES
# ============================================================

q10_beta = quantile_10.params["home_bias"]
q90_beta = quantile_90.params["home_bias"]

q10_effect = (
    np.exp(q10_beta) - 1
) * 100

q90_effect = (
    np.exp(q90_beta) - 1
) * 100

print("\n" + "=" * 70)
print("QUANTILE COMPARISON")
print("=" * 70)

print(
    f"""
                    10th percentile     90th percentile

HomeBias coefficient      {q10_beta:8.4f}          {q90_beta:8.4f}

Implied price effect      {q10_effect:8.2f}%          {q90_effect:8.2f}%
"""
)


# ============================================================
# 17. DESCRIPTIVE STATISTICS
# ============================================================

print("\n" + "=" * 70)
print("DESCRIPTIVE STATISTICS")
print("=" * 70)

print(
    analysis_df[
        [
            "analysis_price",
            "log_price",
            "home_bias",
            "log_size",
            "event_year",
        ]
    ].describe()
)


# ============================================================
# 18. HOME VS FOREIGN MEAN PRICES
# ============================================================

print("\n" + "=" * 70)
print("HOME VS FOREIGN SALES")
print("=" * 70)

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


# ============================================================
# 19. HOME-BIAS BY ARTIST COUNTRY
# ============================================================

print("\n" + "=" * 70)
print("HOME BIAS BY ARTIST COUNTRY")
print("=" * 70)

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


# ============================================================
# 20. SAVE CLEAN DATA
# ============================================================

analysis_df.to_csv(
    OUTPUT_CLEAN,
    index=False
)

print(
    f"\nCleaned regression dataset saved to:"
    f"\n  {OUTPUT_CLEAN}"
)


# ============================================================
# 21. SAVE REGRESSION RESULTS
# ============================================================

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