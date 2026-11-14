
import datetime
from pathlib import Path

import pandas as pd

from src.shared.data_loader import load_and_validate_data
from src.shared.data_preparation import prepare_dataset, create_artwork_size

from src.country_pairs.regression import run_country_pair_regressions

from src.home_bias_test_data.regression import (
    create_home_bias,
    add_pair_adjustment,
    estimate_home_bias_models,
    print_regression_comparison
)

from src.home_bias_test_data.config import (
    TEST_FILE,
    PAIR_DATA_FILE,
    PAIR_ARTIST_FILE,
    REQUIRED_COLUMNS
)

from src.home_bias_test_data.create_samples import create_random_samples
from src.home_bias_test_data.summarise_samples import summarise_results


RESULTS_DIR = Path("src/home_bias_test_data/results")


def prepare_analysis_data(data_file):
    df = load_and_validate_data(data_file, REQUIRED_COLUMNS)
    df = prepare_dataset(df)
    df = create_home_bias(df)
    df = create_artwork_size(df)

    return df


def estimate_pair_coefficients(train_file, split_dir):
    # Prepare training data.
    train_df = prepare_analysis_data(train_file)

    # Estimate country-pair regressions.
    pair_results, artist_df, exclusions_df = (
        run_country_pair_regressions(train_df)
    )

    # Save pair coefficients, qualifying artists and exclusions.
    split_dir.mkdir(parents=True, exist_ok=True)

    pair_data_file = split_dir / "pair_results.csv"
    artist_data_file = split_dir / "qualifying_artists.csv"

    pair_results.to_csv(pair_data_file, index=False)
    artist_df.to_csv(artist_data_file, index=False)

    exclusions_df.to_csv(
        split_dir / "pair_exclusions.csv",
        index=False
    )

    return pair_data_file, artist_data_file


def run_regression(
    test_file,
    pair_data_file,
    artist_data_file,
    label,
    print_details=True
):
    # Prepare test data.
    df = prepare_analysis_data(test_file)

    # Apply training-sample country-pair coefficients
    # only to qualifying artists.
    df = add_pair_adjustment(
        df,
        pair_data_file,
        artist_data_file
    )

    # Estimate baseline and adjusted regressions.
    baseline_model, adjusted_model, analysis_df = (
        estimate_home_bias_models(df)
    )

    if print_details:
        print(f"\n========== {label} ==========")

        print("\n========== BASELINE MODEL ==========")
        print(baseline_model.summary())

        print("\n========== PAIR-ADJUSTED MODEL ==========")
        print(adjusted_model.summary())

        print("\n========== COMPARISON ==========")
        print_regression_comparison(
            baseline_model,
            adjusted_model
        )

    return {
        "baseline_coef": baseline_model.params["home_bias"],
        "baseline_pvalue": baseline_model.pvalues["home_bias"],
        "adjusted_coef": adjusted_model.params["home_bias"],
        "adjusted_pvalue": adjusted_model.pvalues["home_bias"],
        "observations": len(analysis_df)
    }


def run_split(train_file, test_file, split_number):
    print(f"\n========== RANDOM SPLIT {split_number} ==========")

    split_dir = RESULTS_DIR / f"split_{split_number:02d}"

    # Estimate pair coefficients and qualifying artists
    # using this split's training data.
    pair_data_file, artist_data_file = estimate_pair_coefficients(
        train_file,
        split_dir
    )

    # Run both home-bias regressions on the test data.
    result = run_regression(
        test_file,
        pair_data_file,
        artist_data_file,
        label=f"RANDOM SPLIT {split_number}",
        print_details=False
    )

    result["split"] = split_number

    print(
        f"Baseline coefficient: {result['baseline_coef']:.4f}, "
        f"p={result['baseline_pvalue']:.4f}"
    )

    print(
        f"Adjusted coefficient: {result['adjusted_coef']:.4f}, "
        f"p={result['adjusted_pvalue']:.4f}"
    )

    return result


def main():
    print(f"Started at: {datetime.datetime.now()}")

    # Generate qualifying artists for the original pair coefficients.
    original_df = prepare_analysis_data(TEST_FILE)

    _, original_artist_df, _ = run_country_pair_regressions(original_df)

    PAIR_ARTIST_FILE.parent.mkdir(parents=True, exist_ok=True)

    original_artist_df.to_csv(
        PAIR_ARTIST_FILE,
        index=False
    )

    # Run original regression.
    run_regression(
        TEST_FILE,
        PAIR_DATA_FILE,
        PAIR_ARTIST_FILE,
        label="ORIGINAL TEST SAMPLE"
    )

    # Generate random training and test samples.
    sample_files = create_random_samples()

    results = []

    # Run the full experiment for each split.
    for i, (train_file, test_file) in enumerate(sample_files, start=1):
        result = run_split(train_file, test_file, i)
        results.append(result)

    # Save all random-split results.
    results_df = pd.DataFrame(results)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    results_df.to_csv(
        RESULTS_DIR / "random_split_results.csv",
        index=False
    )

    # Print summary.
    print("\n========== RANDOM SPLIT SUMMARY ==========")
    summarise_results()

    print(f"\nFinished at: {datetime.datetime.now()}")


if __name__ == "__main__":
    main()
