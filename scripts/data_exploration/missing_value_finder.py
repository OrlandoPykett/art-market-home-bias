import pandas as pd

df = pd.read_csv(
    "data/transactions.csv",
    encoding="latin1",
    low_memory=False
)


''' 
Create a list of known artists and their nationality
If another observation has a known artist and unknown nationality append nationality

'''

artist_nationality = (
    df.dropna(subset=["nationality"])
      .groupby("artist_name")["nationality"]
      .agg(lambda x: x.dropna().unique())
)

# Only keep artists with exactly one known nationality
artist_nationality = artist_nationality[
    artist_nationality.apply(len) == 1
].apply(lambda x: x[0])

missing_before = df["nationality"].isna().sum()

mask = (
    df["nationality"].isna()
    & df["artist_name"].isin(artist_nationality.index)
)

df.loc[mask, "nationality"] = (
    df.loc[mask, "artist_name"]
      .map(artist_nationality)
)


missing_after = df["nationality"].isna().sum()

print("Missing nationality before:", missing_before)
print("Filled:", missing_before - missing_after)
print("Missing nationality after:", missing_after)


filled = df.loc[
    mask,
    ["artist_name", "nationality"]
].drop_duplicates()

print("\nARTISTS FILLED:")
print(filled.to_string(index=False))


df.to_csv(
    "data/transactions_cleaned.csv",
    index=False,
    encoding="utf-8-sig"
)