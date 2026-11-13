import datetime
from itertools import combinations as _combos

from src.shared.data_loader import load_and_validate_data

from src.home_bias_alt.alt_data_preparation import prepare_dataset, create_artwork_size
from src.home_bias_alt.alt_modular_regression import run_combinations

from src.home_bias_alt.regression import create_home_bias
from src.home_bias_alt.config import DATASET_FILE, REQUIRED_COLUMNS


# Choose extras to inclide
EXTRAS_TO_USE =[]

# Run every extras subset: baseline, each alone, both together
SPECS = [
    c for r in range(len(EXTRAS_TO_USE) + 1)
    for c in _combos(EXTRAS_TO_USE, r)
]

def prepare_analysis_data():
    df = load_and_validate_data(DATASET_FILE, REQUIRED_COLUMNS)
    df = prepare_dataset(df)
    df = create_home_bias(df)
    df = create_artwork_size(df)

    return df


def main():
    print(f"Started at: {datetime.datetime.now()}")
    df = prepare_analysis_data()

    models, table = run_combinations(df, SPECS, common_sample=True)
    print(models[0].summary())
    print(table)

    print(f"Finished at: {datetime.datetime.now()}")

if __name__ == "__main__":
    main()