"""
Main execution script for the country-pair analysis.

Runs the complete country-pair regression workflow.
"""

import datetime

from src.shared.data_loader import load_data, validate_columns
from src.country_pairs.data_preparation import prepare_country_pair_data
from src.country_pairs.regression import run_country_pair_regressions
from src.country_pairs.results import (
    save_results,
    print_summary,
    inspect_country_pairs,
    sort_results
)

from src.country_pairs.config import (
    REQUIRED_COLUMNS,
    INSPECT_PAIRS
)


def main():
    """
    Execute the complete country-pair analysis.

    Workflow:
        1. Load and validate the dataset.
        2. Prepare the observations.
        3. Estimate country-pair regressions.
        4. Create artist-level descriptive statistics.
        5. Save and display results.

    Returns:
        None
    """

    # Start programme
    # --------------------

    print("-" * 20)
    print(f"Programme started at: {datetime.datetime.now()}")
    print("-" * 20)

    # Load data

    df = load_data()
    validate_columns(df, REQUIRED_COLUMNS)

    print(f"\nLoaded {len(df):,} observations.")

    # Prepare data

    df = prepare_country_pair_data(df)

    print(f"Usable observations: {len(df):,}")

    # Run regressions

    results_df, artist_breakdown_df, exclusions_df = (
        run_country_pair_regressions(df)
    )

    # Sort and save results

    results_df, artist_breakdown_df = sort_results(
        results_df,
        artist_breakdown_df
    )

    save_results(
        results_df,
        artist_breakdown_df,
        exclusions_df
    )

    # Display results

    print_summary(
        results_df,
        exclusions_df
    )

    inspect_country_pairs(
        artist_breakdown_df,
        INSPECT_PAIRS
    )

    # Finish programme

    print("\nAnalysis completed.")
    print(f"Programme finished at: {datetime.datetime.now()}")


if __name__ == "__main__":
    main()