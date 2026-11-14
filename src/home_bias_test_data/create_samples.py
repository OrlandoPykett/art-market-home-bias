from pathlib import Path

import pandas as pd


DATA_FILE = Path("data/cleaned/dataset1_cleaned.csv")
OUTPUT_DIR = Path("data/random_samples")

N_SPLITS = 30
TRAIN_SIZE = 0.8
RANDOM_SEED = 42


def create_random_samples():
    df = pd.read_csv(DATA_FILE)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sample_files = []

    for i in range(N_SPLITS):
        seed = RANDOM_SEED + i

        train_df = df.sample(frac=TRAIN_SIZE, random_state=seed)
        test_df = df.drop(train_df.index)

        split_dir = OUTPUT_DIR / f"split_{i + 1:02d}"
        split_dir.mkdir(parents=True, exist_ok=True)

        train_file = split_dir / "train_dataset.csv"
        test_file = split_dir / "test_dataset.csv"

        train_df.to_csv(train_file, index=False)
        test_df.to_csv(test_file, index=False)

        sample_files.append((train_file, test_file))

    return sample_files


if __name__ == "__main__":
    create_random_samples()