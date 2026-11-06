import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.iolib.summary2 import summary_col

from src.shared.extras import EXTRAS

FIXED_EFFECTS = ["C(artist_name)", "C(auction_house)", "C(sale_y)", "C(materials)"]
BASE_NUMERIC = ["home_bias", "log_size"]
REQUIRED_COLS = ["log_price", "artist_name", "auction_house", "sale_y", "materials"]


def add_extras(df, extras):
    """Merge every requested extra once, onto the base data."""
    for name in extras:
        df = EXTRAS[name].add(df)
    return df


def build_formula(extras=()):
    extra_cols = [c for e in extras for c in EXTRAS[e].columns]
    terms = ["home_bias", *extra_cols, "log_size", *FIXED_EFFECTS]
    return "log_price ~ " + " + ".join(terms)


def estimate(df, extras=()):
    extra_cols = [c for e in extras for c in EXTRAS[e].columns]
    numeric = BASE_NUMERIC + extra_cols

    d = df.dropna(subset=REQUIRED_COLS + numeric).copy()
    d = d[np.isfinite(d[["log_price", *numeric]]).all(axis=1)]

    return smf.ols(build_formula(extras), data=d).fit(cov_type="HC1")


def run_combinations(df, combinations, common_sample=True):
    """
    Fit one model per combination of extras and return them side by side.

    common_sample=True restricts every model to rows where ALL extras used
    in ANY combination are available, so coefficient changes reflect the
    added variables rather than a shrinking sample.
    """
    all_extras = sorted({e for combo in combinations for e in combo})
    df = add_extras(df, all_extras)

    if common_sample:
        cols = [c for e in all_extras for c in EXTRAS[e].columns]
        df = df.dropna(subset=cols)
        print(f"Common sample: {len(df):,} observations")

    models, names = [], []
    for combo in combinations:
        models.append(estimate(df, combo))
        names.append("+".join(combo) if combo else "baseline")

    shown = ["home_bias", "log_size"] + [
        c for e in all_extras for c in EXTRAS[e].columns
    ]
    table = summary_col(
        models, model_names=names, stars=True,
        regressor_order=shown, drop_omitted=True,
        info_dict={"N": lambda m: f"{int(m.nobs)}"},
    )
    return models, table