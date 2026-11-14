
"""
Home-bias regression with country-pair adjustments.

1. Construct the home-bias indicator.
2. Merge foreign-market coefficients estimated on training data.
3. Adjust foreign transaction prices.
4. Estimate baseline and adjusted OLS regressions.
5. Compare the home-bias coefficients.
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf


# Construct home-bias variable
# --------------------

def create_home_bias(df):
    """
    Construct the home-bias indicator.

    home_bias = 1 for domestic sales.
    home_bias = 0 for foreign sales.
    """

    df = df.copy()

    for col in ["artist_country", "sale_country"]:
        df[col] = (
            df[col]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    invalid_countries = ["nan", "none", "null", "unknown", "n/a"]

    for col in ["artist_country", "sale_country"]:
        df.loc[
            df[col].str.lower().isin(invalid_countries).fillna(False),
            col
        ] = pd.NA

    valid_location = (
        df["artist_country"].notna()
        & df["sale_country"].notna()
    )

    df["home_bias"] = np.nan

    df.loc[valid_location, "home_bias"] = (
        df.loc[valid_location, "artist_country"]
        == df.loc[valid_location, "sale_country"]
    ).astype(int)

    df["foreign_market"] = np.nan

    df.loc[valid_location, "foreign_market"] = (
        1 - df.loc[valid_location, "home_bias"]
    )

    return df


# Merge country-pair coefficients
# --------------------


def add_pair_adjustment(df, pair_data_file, artist_data_file):
    """
    Apply country-pair coefficients only to artists who qualified
    for the corresponding country-pair regression in the training data.

    Domestic observations and foreign observations belonging to
    non-qualifying artists receive an adjustment of zero.
    """

    df = df.copy()

    pair_df = pd.read_csv(pair_data_file)
    artist_df = pd.read_csv(artist_data_file)

    pair_columns = [
        "artist_country",
        "foreign_sale_country",
        "foreign_effect_coefficient"
    ]

    artist_columns = [
        "artist_country",
        "foreign_sale_country",
        "artist_name"
    ]

    pair_df = pair_df[pair_columns].copy()
    artist_df = artist_df[artist_columns].copy()

    # Normalise country names and artist names before merging.
    for data in [df, pair_df, artist_df]:
        for col in ["artist_country"]:
            data[col] = (
                data[col]
                .astype("string")
                .str.strip()
                .replace("", pd.NA)
            )

    df["sale_country"] = (
        df["sale_country"]
        .astype("string")
        .str.strip()
        .replace("", pd.NA)
    )

    for data in [pair_df, artist_df]:
        data["foreign_sale_country"] = (
            data["foreign_sale_country"]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    for data in [df, artist_df]:
        data["artist_name"] = (
            data["artist_name"]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    pair_df["foreign_effect_coefficient"] = pd.to_numeric(
        pair_df["foreign_effect_coefficient"],
        errors="coerce"
    )

    # Remove unusable coefficients and artist records.
    pair_df = pair_df.dropna(
        subset=[
            "artist_country",
            "foreign_sale_country",
            "foreign_effect_coefficient"
        ]
    )

    pair_df = pair_df[
        np.isfinite(pair_df["foreign_effect_coefficient"])
    ].copy()

    artist_df = artist_df.dropna(
        subset=[
            "artist_country",
            "foreign_sale_country",
            "artist_name"
        ]
    )

    # Each country pair must have exactly one coefficient.
    if pair_df.duplicated(
        subset=["artist_country", "foreign_sale_country"]
    ).any():
        raise ValueError("Duplicate country pairs found in pair dataset.")

    # Each artist must qualify only once within a country pair.
    if artist_df.duplicated(
        subset=[
            "artist_country",
            "foreign_sale_country",
            "artist_name"
        ]
    ).any():
        raise ValueError("Duplicate qualifying artists found in artist dataset.")

    # Attach each pair coefficient to its qualifying artists.
    adjustment_df = artist_df.merge(
        pair_df,
        on=["artist_country", "foreign_sale_country"],
        how="inner",
        validate="many_to_one"
    )

    # Match transactions to both their country pair and qualifying artist.
    df = df.merge(
        adjustment_df,
        left_on=[
            "artist_country",
            "sale_country",
            "artist_name"
        ],
        right_on=[
            "artist_country",
            "foreign_sale_country",
            "artist_name"
        ],
        how="left",
        validate="many_to_one"
    )

    # Only matched qualifying foreign observations receive an adjustment.
    matched = (
        df["home_bias"].eq(0)
        & df["foreign_effect_coefficient"].notna()
    )

    foreign_count = int(df["home_bias"].eq(0).sum())
    adjusted_count = int(matched.sum())
    unadjusted_foreign_count = foreign_count - adjusted_count

    df["foreign_effect_adjustment"] = np.where(
        matched,
        df["foreign_effect_coefficient"],
        0.0
    )

    # Remove the estimated foreign-market effect from qualifying artists'
    # foreign transaction prices.
    df["adjusted_log_price"] = (
        df["log_price"] - df["foreign_effect_adjustment"]
    )

    print("\nCountry-pair adjustment:")
    print("Foreign observations:", foreign_count)
    print("Adjusted foreign observations:", adjusted_count)
    print("Unadjusted foreign observations:", unadjusted_foreign_count)
    print("Domestic observations retained:", int(df["home_bias"].eq(1).sum()))

    return df



# Estimate baseline and adjusted regressions
# --------------------

def estimate_home_bias_models(df):
    """
    Estimate baseline and pair-adjusted home-bias regressions.

    Both models use exactly the same observations and controls.

    Returns:
        baseline_model
        adjusted_model
        analysis_df
    """

    baseline_formula = """
    log_price ~
    home_bias
    + log_size
    + C(artist_name)
    + C(auction_house)
    + C(sale_y)
    + C(materials)
    """

    adjusted_formula = """
    adjusted_log_price ~
    home_bias
    + log_size
    + C(artist_name)
    + C(auction_house)
    + C(sale_y)
    + C(materials)
    """

    required_columns = [
        "log_price",
        "adjusted_log_price",
        "home_bias",
        "log_size",
        "artist_name",
        "auction_house",
        "sale_y",
        "materials"
    ]

    # Use a common sample for both regressions.
    analysis_df = df.dropna(
        subset=required_columns
    ).copy()

    analysis_df = analysis_df[
        np.isfinite(analysis_df["log_price"])
        & np.isfinite(analysis_df["adjusted_log_price"])
        & np.isfinite(analysis_df["log_size"])
    ].copy()

    baseline_model = smf.ols(
        formula=baseline_formula,
        data=analysis_df
    ).fit(cov_type="HC1")

    adjusted_model = smf.ols(
        formula=adjusted_formula,
        data=analysis_df
    ).fit(cov_type="HC1")

    return baseline_model, adjusted_model, analysis_df


# Compare regression results
# --------------------

def print_regression_comparison(baseline_model, adjusted_model):
    """
    Compare baseline and adjusted home-bias coefficients.
    """

    baseline_coef = baseline_model.params["home_bias"]
    adjusted_coef = adjusted_model.params["home_bias"]

    baseline_percentage = np.expm1(baseline_coef) * 100
    adjusted_percentage = np.expm1(adjusted_coef) * 100

    if np.isclose(baseline_coef, 0):
        reduction = np.nan
    else:
        reduction = (
            (baseline_coef - adjusted_coef)
            / baseline_coef
            * 100
        )

    comparison = pd.DataFrame(
        {
            "Baseline": [
                baseline_coef,
                baseline_percentage,
                baseline_model.bse["home_bias"],
                baseline_model.pvalues["home_bias"]
            ],
            "Pair-adjusted": [
                adjusted_coef,
                adjusted_percentage,
                adjusted_model.bse["home_bias"],
                adjusted_model.pvalues["home_bias"]
            ]
        },
        index=[
            "Home-bias coefficient",
            "Implied price difference (%)",
            "Standard error",
            "P-value"
        ]
    )

    print("\nHome-bias regression comparison:")
    print(comparison.round(4).to_string())

    print(
        f"\nReduction in home-bias coefficient: {reduction:.2f}%"
    )

    print(
        "\nObservations:",
        int(baseline_model.nobs)
    )

    print(
        "Baseline R-squared:",
        round(baseline_model.rsquared, 4)
    )

    print(
        "Adjusted R-squared:",
        round(adjusted_model.rsquared, 4)
    )

    return comparison
