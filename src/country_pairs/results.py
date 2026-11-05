
"""
Results handling for the country-pair analysis.

Sorts, exports and displays regression results,
artist-level statistics and exclusion diagnostics.
"""

import os
import pandas as pd

from .config import (
    OUTPUT_FILE,
    ARTIST_BREAKDOWN_FILE,
    EXCLUSIONS_FILE
)


# Sort results
# --------------------

def sort_results(results_df, artist_df):
    """
    Sort regression results and artist-level statistics.

    Args:
        results_df: DataFrame containing regression results.
        artist_df: DataFrame containing artist-level statistics.

    Returns:
        Tuple containing the sorted DataFrames.
    """

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

    return results_df, artist_df


# Save results
# --------------------

def save_results(results_df, artist_df, exclusions_df):
    """
    Export all country-pair analysis results to CSV files.

    Creates output directories if they do not already exist.

    Args:
        results_df: Regression results.
        artist_df: Artist-level descriptive statistics.
        exclusions_df: Excluded country pairs and reasons.

    Returns:
        None
    """

    output_files = [
        OUTPUT_FILE,
        ARTIST_BREAKDOWN_FILE,
        EXCLUSIONS_FILE
    ]

    # Create directories when necessary.
    for file in output_files:

        directory = os.path.dirname(file)

        if directory:
            os.makedirs(directory, exist_ok=True)

    results_df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    artist_df.to_csv(
        ARTIST_BREAKDOWN_FILE,
        index=False
    )

    exclusions_df.to_csv(
        EXCLUSIONS_FILE,
        index=False
    )


# Print summary
# --------------------

def print_summary(results_df, exclusions_df):
    """
    Display a summary of the country-pair analysis.

    Args:
        results_df: Regression results.
        exclusions_df: Excluded country pairs and reasons.

    Returns:
        None
    """

    print("\n" + "-" * 20)
    print("COUNTRY-PAIR ANALYSIS COMPLETE")
    print("-" * 20)

    print(
        f"Regressions completed: {len(results_df):,}"
    )

    print(
        f"Pairs excluded / failed: {len(exclusions_df):,}"
    )

    print(f"Regression results: {OUTPUT_FILE}")
    print(f"Artist breakdown: {ARTIST_BREAKDOWN_FILE}")
    print(f"Exclusion diagnostics: {EXCLUSIONS_FILE}")

    if not results_df.empty:

        print("\nLargest country-pair samples:")

        print(
            results_df.nlargest(
                20,
                "pair_observations"
            )[
                [
                    "artist_country",
                    "foreign_sale_country",
                    "qualifying_artists",
                    "pair_observations",
                    "foreign_effect_percentage",
                    "effect_ci_95_lower_pct",
                    "effect_ci_95_upper_pct",
                    "p_value"
                ]
            ].to_string(index=False)
        )


# Inspect selected country pairs

def inspect_country_pairs(artist_df, inspect_pairs):
    """
    Display artist-level statistics for selected country pairs.

    Args:
        artist_df: Artist-level descriptive statistics.
        inspect_pairs: List of home and foreign country tuples.

    Returns:
        None
    """

    if artist_df.empty:
        return

    for home, foreign in inspect_pairs:

        subset = artist_df[
            (
                artist_df["artist_country"] == home
            )
            & (
                artist_df["foreign_sale_country"] == foreign
            )
        ]

        if not subset.empty:

            print(f"\nArtist breakdown: {home} -> {foreign}")

            print(
                subset[
                    [
                        "artist_name",
                        "home_observations",
                        "foreign_observations",
                        "home_median_price",
                        "foreign_median_price"
                    ]
                ].to_string(index=False)
            )
