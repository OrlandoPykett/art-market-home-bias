import datetime
from itertools import combinations as _combos

from src.shared.data_loader import load_and_validate_data
from src.shared.data_preparation import prepare_dataset, create_artwork_size
from src.home_bias.regression import create_home_bias
from src.shared.modular_regression import run_combinations

# Choose which extras to include. Edit freely.
EXTRAS_TO_USE = ["language_proximity"]

# Every subset: baseline, each alone, both together
SPECS = [
    c for r in range(len(EXTRAS_TO_USE) + 1)
    for c in _combos(EXTRAS_TO_USE, r)
]
# Or specify manually, e.g.: SPECS = [(), ("national_pride",)]


def prepare_analysis_data():
    df = load_and_validate_data()
    df = prepare_dataset(df)
    df = create_home_bias(df)
    df = create_artwork_size(df)
    return df


def main():
    print(f"Started: {datetime.datetime.now()}")
    df = prepare_analysis_data()

    models, table = run_combinations(df, SPECS, common_sample=True)
    print(table)

    print(f"Finished: {datetime.datetime.now()}")


if __name__ == "__main__":
    main()