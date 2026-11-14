from pathlib import Path

import numpy as np
import pandas as pd


RESULTS_FILE = Path("src/home_bias_test_data/results/random_split_results.csv")


def summarise_results():
    df = pd.read_csv(RESULTS_FILE)

    columns = ["baseline_coef", "adjusted_coef"]

    print("\n========== RANDOM SPLIT SUMMARY ==========")
    print(f"Number of splits: {len(df)}")
    print(f"Average test observations: {df['observations'].mean():.0f}")

    for column in columns:
        results = df[column]

        print(f"\n{column.replace('_', ' ').title()}")
        print(f"Mean:   {results.mean():.4f}")
        print(f"Median: {results.median():.4f}")
        print(f"Std:    {results.std():.4f}")
        print(f"Min:    {results.min():.4f}")
        print(f"Max:    {results.max():.4f}")
        print(f"Mean implied price difference: {np.expm1(results.mean()) * 100:.2f}%")

    print("\n========== STATISTICAL SIGNIFICANCE ==========")

    for model in ["baseline", "adjusted"]:
        pvalues = df[f"{model}_pvalue"]

        significant = (pvalues < 0.05).mean() * 100

        print(
            f"{model.title()}: "
            f"{significant:.1f}% of splits significant at the 5% level"
        )

    print("\n========== COEFFICIENT REDUCTION ==========")

    reductions = (
        (df["baseline_coef"] - df["adjusted_coef"])
        / df["baseline_coef"].abs()
        * 100
    )

    print(f"Mean reduction: {reductions.mean():.2f}%")
    print(f"Median reduction: {reductions.median():.2f}%")


if __name__ == "__main__":
    summarise_results()