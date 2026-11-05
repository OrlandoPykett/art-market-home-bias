
"""
Main execution script.

Runs the complete home-bias analysis workflow, from loading
the auction dataset to estimating and presenting the OLS model.
"""

import datetime

from src.shared.data_loader import load_and_validate_data
from src.shared.data_preparation import prepare_dataset, create_artwork_size
from src.home_bias.regression import (
    create_home_bias,
    estimate_home_bias_model,
    print_regression_results
)

def main():
    """
    Execute the complete home-bias analysis.

    Workflow:
        1. Load and validate the auction dataset.
        2. Prepare observations and handle missing values.
        3. Construct home-bias and artwork-size variables.
        4. Estimate the OLS regression.
        5. Print the regression results.

    Returns:
        None
    """

    # Start programme
    # --------------------

    time_now = datetime.datetime.now()

    print("-" * 20)
    print(f"Programme started at: {time_now}")
    print("-" * 20)

    # Load data

    df = load_and_validate_data()

    print(f"\nLoaded {len(df):,} observations.")

    # Prepare data

    df = prepare_dataset(df)

    print(
        f"Observations after essential-variable filtering: "
        f"{len(df):,}"
    )

    # Construct variables

    df = create_home_bias(df)

    df = create_artwork_size(df)

    # OLS regression

    model = estimate_home_bias_model(df)

    # Display results

    print_regression_results(model)

    # Finish programme

    print("\nAnalysis completed.")
    print(f"Programme finished at: {datetime.datetime.now()}")


if __name__ == "__main__":
    main()
