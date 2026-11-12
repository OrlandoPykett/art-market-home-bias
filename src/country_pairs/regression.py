
"""
Regression estimation for the country-pair analysis.

Identifies qualifying artists, constructs country-pair samples
and estimates separate OLS regressions for each qualifying pair.
"""

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf

from .config import (
    MIN_ARTIST_MARKET_OBSERVATIONS,
    MIN_PAIR_OBSERVATIONS,
    MIN_HOME_OBSERVATIONS,
    MIN_FOREIGN_OBSERVATIONS,
    MIN_COMMON_ARTISTS
)


# Identify qualifying artists
# --------------------

def identify_qualifying_artists(
    candidate_df,
    artist_country,
    foreign_country
):
    """
    Identify artists with sufficient observations in both markets.

    An artist must have at least the minimum number of sales
    in both their home market and the selected foreign market.

    Args:
        candidate_df: Observations from the two selected markets.
        artist_country: Artist's home country.
        foreign_country: Selected foreign sale country.

    Returns:
        Index containing qualifying artist names.
    """

    counts = (
        candidate_df
        .groupby(["artist_name", "sale_country"])
        .size()
        .unstack(fill_value=0)
    )

    # Ensure both market columns exist.
    counts = counts.reindex(
        columns=[artist_country, foreign_country],
        fill_value=0
    )

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

    return qualifying


# Prepare country-pair sample
# --------------------

def prepare_country_pair_sample(
    df,
    artist_country,
    foreign_country
):
    """
    Construct the regression sample for one country pair.

    Keeps only observations from the artist's home market
    and the selected foreign market. Only artists with
    sufficient observations in both markets are retained.

    Args:
        df: Prepared auction dataset.
        artist_country: Artist's home country.
        foreign_country: Selected foreign sale country.

    Returns:
        Tuple containing:
            pair_df: Filtered regression sample.
            common_n: Number of qualifying artists.
            home_n: Number of home-market observations.
            foreign_n: Number of foreign-market observations.
            reason: Exclusion reason, or None if the sample qualifies.
    """

    # Keep only the two selected markets.
    candidate_df = df[
        (
            df["artist_country"] == artist_country
        )
        & (
            df["sale_country"].isin(
                [artist_country, foreign_country]
            )
        )
    ].copy()

    # Identify artists with observations in both markets.
    qualifying = identify_qualifying_artists(
        candidate_df,
        artist_country,
        foreign_country
    )

    common_n = len(qualifying)

    pair_df = candidate_df[
        candidate_df["artist_name"].isin(qualifying)
    ].copy()

    # Count observations in each market.
    home_n = int(
        (pair_df["sale_country"] == artist_country).sum()
    )

    foreign_n = int(
        (pair_df["sale_country"] == foreign_country).sum()
    )

    pair_n = len(pair_df)

    # Check whether the pair meets the sample requirements.
    reason = None

    if common_n < MIN_COMMON_ARTISTS:
        reason = "Too few qualifying artists"

    elif pair_n < MIN_PAIR_OBSERVATIONS:
        reason = "Too few total observations"

    elif home_n < MIN_HOME_OBSERVATIONS:
        reason = "Too few home-market observations"

    elif foreign_n < MIN_FOREIGN_OBSERVATIONS:
        reason = "Too few foreign-market observations"

    return pair_df, common_n, home_n, foreign_n, reason


# Estimate one country-pair regression
# --------------------

def estimate_country_pair_regression(
    pair_df,
    artist_country,
    foreign_country,
    common_n,
    home_n,
    foreign_n
):
    """
    Estimate the OLS regression for one country pair.

    Uses artist, auction house, event year and materials
    fixed effects, with standard errors clustered by artist.

    Args:
        pair_df: Qualifying observations for the country pair.
        artist_country: Artist's home country.
        foreign_country: Selected foreign sale country.
        common_n: Number of qualifying artists.
        home_n: Number of home-market observations.
        foreign_n: Number of foreign-market observations.

    Returns:
        Tuple containing:
            result: Dictionary of regression results.
            artist_records: List of artist-level statistics.
    """

    # 0 = home market; 1 = selected foreign market.
    pair_df = pair_df.copy()

    pair_df["foreign_market"] = (
        pair_df["sale_country"] == foreign_country
    ).astype(int)

    pair_n = len(pair_df)


    # Regression formula
    # --------------------

    formula = (
        "log_price ~ foreign_market "
        "+ log_size "
        "+ C(artist_name) "
        "+ C(auction_house) "
        "+ C(sale_y) "
        "+ C(materials)"
    )

    # Use only observations with complete model variables.
    analysis_df = pair_df.dropna(
        subset=[
            "log_price",
            "foreign_market",
            "log_size",
            "artist_name",
            "auction_house",
            "sale_y",
            "materials"
        ]
    ).copy()

    # Exclude infinite values from continuous variables.
    analysis_df = analysis_df[
        np.isfinite(analysis_df["log_price"])
        & np.isfinite(analysis_df["log_size"])
    ].copy()

    # Update regression sample counts.
    pair_n = len(analysis_df)

    home_n = int(
        (analysis_df["foreign_market"] == 0).sum()
    )

    foreign_n = int(
        (analysis_df["foreign_market"] == 1).sum()
    )

    common_n = analysis_df["artist_name"].nunique()

    # Estimate model using the cleaned sample.
    model = smf.ols(
        formula=formula,
        data=analysis_df
    ).fit(
        cov_type="cluster",
        cov_kwds={
            "groups": analysis_df["artist_name"]
        }
    )

    # Use the regression sample for subsequent statistics.
    pair_df = analysis_df


    # Estimate model
    # --------------------
    model = smf.ols(
        formula=formula,
        data=pair_df
    ).fit(
        cov_type="cluster",
        cov_kwds={
            "groups": pair_df["artist_name"]
        }
    )

    # Extract regression results

    coefficient = model.params["foreign_market"]
    std_error = model.bse["foreign_market"]
    p_value = model.pvalues["foreign_market"]

    ci_low, ci_high = model.conf_int().loc[
        "foreign_market"
    ].tolist()

    # Convert log coefficients into percentage changes.
    effect_pct = 100 * np.expm1(coefficient)

    effect_ci_low = 100 * np.expm1(ci_low)
    effect_ci_high = 100 * np.expm1(ci_high)

    home_artists = pair_df.loc[
        pair_df["foreign_market"] == 0,
        "artist_name"
    ].nunique()

    foreign_artists = pair_df.loc[
        pair_df["foreign_market"] == 1,
        "artist_name"
    ].nunique()

    result = {
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
    }

    # Artist-level descriptive statistics

    artist_records = []

    for artist in sorted(pair_df["artist_name"].unique()):

        artist_df = pair_df[
            pair_df["artist_name"] == artist
        ]

        home = artist_df[
            artist_df["foreign_market"] == 0
        ]

        foreign = artist_df[
            artist_df["foreign_market"] == 1
        ]

        artist_records.append({
            "artist_country": artist_country,
            "foreign_sale_country": foreign_country,
            "artist_name": artist,
            "home_observations": len(home),
            "foreign_observations": len(foreign),
            "total_observations": len(artist_df),
            "home_median_price": home["real_price_usd"].median(),
            "foreign_median_price": foreign["real_price_usd"].median(),
            "home_mean_price": home["real_price_usd"].mean(),
            "foreign_mean_price": foreign["real_price_usd"].mean(),
            "home_total_value": home["real_price_usd"].sum(),
            "foreign_total_value": foreign["real_price_usd"].sum()
        })

    return result, artist_records


# Run all country-pair regressions
# --------------------

def run_country_pair_regressions(df):
    """
    Estimate regressions for all qualifying country pairs.

    Iterates over artist countries and their foreign sale markets.
    Records successful regressions, artist-level statistics and
    exclusions.

    Args:
        df: Prepared auction dataset.

    Returns:
        Tuple containing:
            results_df: Regression results for qualifying pairs.
            artist_df: Artist-level descriptive statistics.
            exclusions_df: Excluded pairs and their reasons.
    """

    results = []
    artist_breakdown = []
    exclusions = []

    artist_countries = sorted(
        df["artist_country"].unique()
    )

    # Iterate over artist countries

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

        # Iterate over foreign sale countries

        for foreign_country in foreign_countries:

            (
                pair_df,
                common_n,
                home_n,
                foreign_n,
                reason
            ) = prepare_country_pair_sample(
                df,
                artist_country,
                foreign_country
            )

            pair_n = len(pair_df)

            # Record pairs that do not meet sample requirements.
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

            # Estimate regression

            try:

                result, artist_records = (
                    estimate_country_pair_regression(
                        pair_df,
                        artist_country,
                        foreign_country,
                        common_n,
                        home_n,
                        foreign_n
                    )
                )

                results.append(result)
                artist_breakdown.extend(artist_records)

                print(
                    f"{artist_country:20s} -> "
                    f"{foreign_country:20s} | "
                    f"Artists={common_n:3d} | "
                    f"N={pair_n:5d} | "
                    f"Foreign effect="
                    f"{result['foreign_effect_percentage']:8.2f}% | "
                    f"p={result['p_value']:.4g}"
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

    # Convert results to DataFrames

    results_df = pd.DataFrame(results)
    artist_df = pd.DataFrame(artist_breakdown)
    exclusions_df = pd.DataFrame(exclusions)

    return results_df, artist_df, exclusions_df
