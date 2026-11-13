"""
Home-bias regression using alternative dataset.

Contains functions for constructing the home-bias indicator,
calculating artwork size, estimating the OLS regression and
presenting the regression results.
"""

import pandas as pd
import numpy as np
import statsmodels.formula.api as smf


# Construct home-bias variable
# --------------------

def create_home_bias(df):
    """
    Construct the home-bias indicator.

    Home bias equals 1 when an artwork is sold in the artist's
    home country and 0 when it is sold in a foreign country.

    Observations without a valid artist or sale country receive
    a missing value.

    Also constructs the equivalent foreign-market indicator,
    where 1 represents a foreign sale and 0 represents a home sale.

    Returns:
        DataFrame with home_bias and foreign_market columns.
    """
    df = df.copy()

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

    return df


# Estimate OLS regression
# --------------------

def estimate_home_bias_model(df):
    """
    Estimate the OLS home-bias regression.

    The dependent variable is the logarithm of real artwork price.
    The model includes home bias, artwork size and fixed effects
    for artist, auction house, sale year and materials.

    Heteroskedasticity-robust standard errors (HC1) are used.

    Returns:
        Fitted statsmodels OLS regression result.
    """

    formula = """
    log_price ~
    home_bias
    + log_size
    + C(artist_name)
    + C(auction_house)
    + C(sale_y)
    + C(materials)
    """

    # Use only observations with complete model variables.
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

    return model


# Print regression results
# --------------------

def print_regression_results(model):
    """
    Display the main home-bias regression results.

    Reports the number of observations, home-bias coefficient,
    implied percentage price difference and p-value.

    Also displays a table containing the coefficients,
    standard errors and p-values for the main explanatory
    variables.
    """

    print("Observations used:", int(model.nobs))
    print("Home-bias coefficient:", model.params["home_bias"])
    print(
        "Implied price difference:",
        f"{np.expm1(model.params['home_bias']) * 100:.2f}%"
    )
    print("P-value:", model.pvalues["home_bias"])

    variables = ["home_bias", "log_size"]

    results_table = pd.DataFrame({
        "Coefficient": model.params[variables],
        "Std. Error": model.bse[variables],
        "P-value": model.pvalues[variables]
    })

    print("\nRegression results:")
    print(results_table.round(4).to_string())

    print(
        "\nArtist, auction-house, year and materials "
        "fixed effects included."
    )