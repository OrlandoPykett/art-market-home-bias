import pandas as pd

from src.shared.config import DATASET1_FILE
from src.shared.country_mapping import convert_country

df = pd.read_csv(DATASET1_FILE)

# Print the dataset summary for the given dataset file.
print(f"Dataset summary for {DATASET1_FILE}:")
print(f"File path: {DATASET1_FILE}")

print("Summary statistics:")
print(f" - Number of observations: {df.shape[0]}")
print(f" - Number of unique artists: {df['artist_name'].nunique()}")
print(f" - Median price (USD): {df['real_price_usd'].median()}")
print(f" - First observation year: {df['sale_y'].min()}")
print(f" - Last observation year: {df['sale_y'].max()}")
print(f" - Number of unique auction houses: {df['auction_house'].nunique()}")

print("Country distribution:")
# Convert country names to standardized format
for col in df.columns:
    df[col] = df[col].apply(lambda x: convert_country(x) if isinstance(x, str) else x)

print(f" - Number of unique nationalities: {df['artist_country'].nunique()}")
print(f" - Top 25 countries by number of artists:")
for country in df['artist_country'].value_counts().head(25).index:
    count = df[df['artist_country'] == country].shape[0]
    print(f"   {country}: {count}")

# Convert sales country names to standardized format
for col in df.columns:
    df[col] = df[col].apply(lambda x: convert_country(x) if isinstance(x, str) else x)

print(f" Number of unique sales countries: {df['sale_country'].nunique()}")
print(f" Top 25 sales countries by number of sales:")
for country in df['sale_country'].value_counts().head(25).index:
    count = df[df['sale_country'] == country].shape[0]
    print(f"   {country}: {count}")