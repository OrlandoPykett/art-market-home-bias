"""
Main execution script for the country-pair analysis.

Runs the complete country-pair regression workflow.
"""

import datetime
from itertools import combinations as _combos

from src.shared.data_loader import load_and_validate_data
from src.shared.data_preparation import prepare_dataset, create_artwork_size
from src.shared.modular_regression import run_combinations
from src.country_pairs.regression import run_country_pair_regressions
from src.country_pairs.results import (
    save_results,
    print_summary,
    inspect_country_pairs,
    sort_results
)

from src.country_pairs.config import (
    INPUT_FILE,
    REQUIRED_COLUMNS,
    INSPECT_PAIRS
)

# Choose which extras to include
EXTRAS_TO_USE = []

# Every subset: baseline, each alone, both together
SPECS = [ 
    c for r in range(len(EXTRAS_TO_USE) + 1)
    for c in _combos(EXTRAS_TO_USE, r)
]
# Or specify manually, e.g.: SPECS = [(), ("national_pride",)]


def prepare_analysis_data():
    df = load_and_validate_data(INPUT_FILE, REQUIRED_COLUMNS)
    df = prepare_dataset(df)
    df = create_artwork_size(df)

    return df


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

    df = prepare_analysis_data()

    print(f"\nLoaded {len(df):,} observations.")
    

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