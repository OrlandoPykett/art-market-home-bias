
import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

INPUT_FILE = "data/cleaned/transactions_merged.csv"

OUTPUT_FILE = "results/country_pair_regressions.csv"
ARTIST_BREAKDOWN_FILE = "results/pair_artist_breakdown.csv"
EXCLUSIONS_FILE = "results/country_pair_exclusions.csv"

# Main robustness parameter:
# Small difference between 1, 3, and 5. 10 produces significantly differentresult
MIN_ARTIST_MARKET_OBSERVATIONS = 3

MIN_PAIR_OBSERVATIONS = 50
MIN_HOME_OBSERVATIONS = 20
MIN_FOREIGN_OBSERVATIONS = 20
MIN_COMMON_ARTISTS = 5

# Pairs for quickly checking results
INSPECT_PAIRS = [
    ("United States", "United Kingdom"),
    ("United States", "Germany"),
    ("Germany", "Switzerland"),
    ("France", "Germany"),
]


df = pd.read_csv(
    INPUT_FILE,
    encoding="latin1",
    low_memory=False
)

print(f"Loaded {len(df):,} observations.")

required_columns = [
    "artist_country", "sale_country",
    "real_price_usd", "ln_real_price",
    "height", "width", "depth",
    "artist_name", "auction_house",
    "event_year", "materials"
]

missing_columns = sorted(
    set(required_columns) - set(df.columns)
)

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Normalize categorical fields without converting missing
# values into the literal string "nan".
categorical_columns = [
    "artist_country", "sale_country",
    "artist_name", "auction_house", "materials"
]

for column in categorical_columns:
    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

for column in [
    "real_price_usd", "ln_real_price",
    "height", "width", "depth", "event_year"
]:
    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

# Remove invalid prices and reconstruct log price from
# real_price_usd to keep the outcome definition consistent.
df = df[
    df["real_price_usd"].gt(0)
    & df["real_price_usd"].notna()
].copy()

df["ln_real_price"] = np.log(df["real_price_usd"])



# Calculate artwork size
'''
Preserve the original size convention:
use volume when all three dimensions are available;
otherwise use height x width.
'''

valid_height_width = (
    df["height"].gt(0) & df["width"].gt(0)
)

valid_volume = (
    valid_height_width & df["depth"].gt(0)
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
        "artist_country", "sale_country",
        "ln_real_price", "log_size",
        "artist_name", "auction_house",
        "event_year", "materials"
    ]
).copy()

# Exclude empty categories and placeholder strings.
for column in categorical_columns:
    df = df[
        ~df[column].str.lower().isin(
            ["nan", "none", "null", "unknown", "n/a"]
        )
    ].copy()

print(f"Usable observations: {len(df):,}")


# ------
# Regressions
# ------

results = []
artist_breakdown = []
exclusions = []

artist_countries = sorted(
    df["artist_country"].unique()
)

for artist_country in artist_countries:

    artist_df = df[
        df["artist_country"] == artist_country
    ]

    foreign_countries = sorted(
        artist_df.loc[
            artist_df["sale_country"] != artist_country,
            "sale_country"
        ].unique()
    )

    for foreign_country in foreign_countries:

        # Only home and the selected foreign market.
        candidate_df = artist_df[
            artist_df["sale_country"].isin(
                [artist_country, foreign_country]
            )
        ].copy()

        # Count each artist's sales in both markets.
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

        qualifying = counts[
            (counts[artist_country]
             >= MIN_ARTIST_MARKET_OBSERVATIONS)
            & (counts[foreign_country]
               >= MIN_ARTIST_MARKET_OBSERVATIONS)
        ].index

        common_n = len(qualifying)

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

        # Record why the pair did not qualify.
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
                "exclusion_reason": reason
            })
            continue

        # 0 = home; 1 = foreign.
        pair_df["foreign_market"] = (
            pair_df["sale_country"] == foreign_country
        ).astype(int)

        formula = (
            "ln_real_price ~ foreign_market "
            "+ log_size "
            "+ C(artist_name) "
            "+ C(auction_house) "
            "+ C(event_year) "
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

            coefficient = model.params["foreign_market"]
            std_error = model.bse["foreign_market"]
            p_value = model.pvalues["foreign_market"]

            ci_low, ci_high = model.conf_int().loc[
                "foreign_market"
            ].tolist()

            # Percentage change in expected price associated
            # with foreign rather than home sales.
            effect_pct = 100 * np.expm1(coefficient)
            effect_ci_low = 100 * np.expm1(ci_low)
            effect_ci_high = 100 * np.expm1(ci_high)

            home_prices = pair_df.loc[
                pair_df["foreign_market"] == 0,
                "real_price_usd"
            ]
            foreign_prices = pair_df.loc[
                pair_df["foreign_market"] == 1,
                "real_price_usd"
            ]

            home_artists = pair_df.loc[
                pair_df["foreign_market"] == 0,
                "artist_name"
            ].nunique()

            foreign_artists = pair_df.loc[
                pair_df["foreign_market"] == 1,
                "artist_name"
            ].nunique()

            results.append({
                "artist_country": artist_country,
                "foreign_sale_country": foreign_country,
                "qualifying_artists": common_n,
                "home_artists": home_artists,
                "foreign_artists": foreign_artists,
                "pair_observations": pair_n,
                "home_observations": home_n,
                "foreign_observations": foreign_n,
                "foreign_effect_coefficient": coefficient,
                "foreign_effect_std_error": std_error,
                "foreign_effect_percentage": effect_pct,
                "effect_ci_95_lower_pct": effect_ci_low,
                "effect_ci_95_upper_pct": effect_ci_high,
                "p_value": p_value,
                "significant_5pct": bool(p_value < 0.05),
                "r_squared": model.rsquared,
                "adjusted_r_squared": model.rsquared_adj
            })

            # Artist-level descriptive statistics.
            for artist in sorted(qualifying):
                a = pair_df[
                    pair_df["artist_name"] == artist
                ]

                h = a[a["foreign_market"] == 0]
                f = a[a["foreign_market"] == 1]

                artist_breakdown.append({
                    "artist_country": artist_country,
                    "foreign_sale_country": foreign_country,
                    "artist_name": artist,
                    "home_observations": len(h),
                    "foreign_observations": len(f),
                    "total_observations": len(a),
                    "home_median_price": h["real_price_usd"].median(),
                    "foreign_median_price": f["real_price_usd"].median(),
                    "home_mean_price": h["real_price_usd"].mean(),
                    "foreign_mean_price": f["real_price_usd"].mean(),
                    "home_total_value": h["real_price_usd"].sum(),
                    "foreign_total_value": f["real_price_usd"].sum()
                })

            print(
                f"{artist_country:20s} -> "
                f"{foreign_country:20s} | "
                f"Artists={common_n:3d} | "
                f"N={pair_n:5d} | "
                f"Foreign effect={effect_pct:8.2f}% | "
                f"p={p_value:.4g}"
            )

        except Exception as e:
            exclusions.append({
                "artist_country": artist_country,
                "foreign_sale_country": foreign_country,
                "qualifying_artists": common_n,
                "pair_observations": pair_n,
                "home_observations": home_n,
                "foreign_observations": foreign_n,
                "exclusion_reason": f"Regression error: {e}"
            })

# ------
# Outputs
# ------

results_df = pd.DataFrame(results)
artist_df = pd.DataFrame(artist_breakdown)
exclusions_df = pd.DataFrame(exclusions)

if not results_df.empty:
    results_df = results_df.sort_values(
        ["artist_country", "pair_observations"],
        ascending=[True, False]
    )

if not artist_df.empty:
    artist_df = artist_df.sort_values(
        [
            "artist_country",
            "foreign_sale_country",
            "total_observations"
        ],
        ascending=[True, True, False]
    )

results_df.to_csv(OUTPUT_FILE, index=False)
artist_df.to_csv(ARTIST_BREAKDOWN_FILE, index=False)
exclusions_df.to_csv(EXCLUSIONS_FILE, index=False)

print("\n" + "-" * 20)
print("COUNTRY-PAIR ANALYSIS COMPLETE")
print("-" * 20)
print(f"Artist threshold per market: {MIN_ARTIST_MARKET_OBSERVATIONS}")
print(f"Minimum qualifying artists: {MIN_COMMON_ARTISTS}")
print(f"Regressions completed: {len(results_df):,}")
print(f"Pairs excluded / failed: {len(exclusions_df):,}")
print(f"Regression results: {OUTPUT_FILE}")
print(f"Artist breakdown: {ARTIST_BREAKDOWN_FILE}")
print(f"Exclusion diagnostics: {EXCLUSIONS_FILE}")

if not results_df.empty:
    print("\nLargest country-pair samples:")
    print(
        results_df.nlargest(20, "pair_observations")[
            [
                "artist_country", "foreign_sale_country",
                "qualifying_artists", "pair_observations",
                "foreign_effect_percentage",
                "effect_ci_95_lower_pct",
                "effect_ci_95_upper_pct", "p_value"
            ]
        ].to_string(index=False)
    )

if not artist_df.empty:
    for home, foreign in INSPECT_PAIRS:
        subset = artist_df[
            (artist_df["artist_country"] == home)
            & (artist_df["foreign_sale_country"] == foreign)
        ]

        if not subset.empty:
            print(f"\nArtist breakdown: {home} -> {foreign}")
            print(
                subset[
                    [
                        "artist_name", "home_observations",
                        "foreign_observations",
                        "home_median_price",
                        "foreign_median_price"
                    ]
                ].to_string(index=False)
            )

print("\nDone.")