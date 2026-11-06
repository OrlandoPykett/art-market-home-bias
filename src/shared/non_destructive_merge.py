"""Generic merge helper with key checks and diagnostics."""

import pandas as pd


def merge_on_keys(df, other, keys, value_cols, label):
    """
    Left-merge `value_cols` from `other` onto `df` using `keys`.

    Raises if `other` has duplicate keys, and prints which
    auction-side keys found no match.
    """
    keys = list(keys)
    value_cols = list(value_cols)

    other = other[keys + value_cols].dropna(subset=keys)

    if other.duplicated(subset=keys).any():
        raise ValueError(f"[{label}] duplicate keys in supplementary data.")

    merged = df.merge(other, on=keys, how="left", validate="many_to_one")

    matched = merged[value_cols[0]].notna().sum()
    print(f"\n[{label}] matched: {matched:,} | "
          f"unmatched: {len(merged) - matched:,}")

    # Show the most common keys that failed to match
    missing = merged.loc[merged[value_cols[0]].isna(), keys].dropna()
    if len(missing):
        print(missing.value_counts().head(10).to_string())

    return merged