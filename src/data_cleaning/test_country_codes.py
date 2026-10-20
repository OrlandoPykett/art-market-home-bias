import pandas as pd

# ============================================================
# TEST COUNTRY CODES IN THE ART AUCTION DATASET
# ============================================================

DATA_FILE = "transactions.csv"

print("Loading dataset...")
df = pd.read_csv(DATA_FILE, encoding="latin1", low_memory=False)

print(f"Loaded {len(df):,} rows.")
print(f"Columns: {len(df.columns)}")
print()


# ------------------------------------------------------------
# TEST 1: Show all values in the country column
# ------------------------------------------------------------

print("=" * 80)
print("TEST 1: COUNTRY VALUES")
print("=" * 80)

country_counts = (
    df["country"]
    .astype(str)
    .str.strip()
    .value_counts()
)

print(country_counts.to_string())
print()


# ------------------------------------------------------------
# TEST 2: Separate numeric country codes from text locations
# ------------------------------------------------------------

print("=" * 80)
print("TEST 2: NUMERIC COUNTRY CODES")
print("=" * 80)

country_numeric = pd.to_numeric(df["country"], errors="coerce")

numeric_codes = sorted(country_numeric.dropna().unique())

print(f"Found {len(numeric_codes)} numeric country codes:")
print([int(x) for x in numeric_codes])
print()

print("Frequency of each numeric code:")
print(
    country_numeric.dropna()
    .astype(int)
    .value_counts()
    .sort_index()
    .to_string()
)
print()


# ------------------------------------------------------------
# TEST 3: Examine what is associated with each numeric code
# ------------------------------------------------------------

print("=" * 80)
print("TEST 3: WHAT DOES EACH COUNTRY CODE REPRESENT?")
print("=" * 80)

for code in numeric_codes:
    code = int(code)
    subset = df[country_numeric == code]

    print()
    print("-" * 80)
    print(f"COUNTRY CODE: {code}")
    print(f"OBSERVATIONS: {len(subset):,}")
    print("-" * 80)

    print("\nAuction houses:")
    print(
        subset["auction_house"]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(10)
        .to_string()
    )

    print("\nEvent names:")
    print(
        subset["event name"]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(10)
        .to_string()
    )

    print("\nArtist nationalities:")
    print(
        subset["nationality"]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(10)
        .to_string()
    )

    print("\nExample artists:")
    print(
        subset["artist_name"]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(10)
        .to_string()
    )

    print("\nExample rows:")
    example_columns = [
        "country",
        "auction_house",
        "event name",
        "event date",
        "nationality",
        "artist_name",
    ]

    print(
        subset[example_columns]
        .head(5)
        .to_string(index=False)
    )


# ------------------------------------------------------------
# TEST 4: Examine text-based country/location values
# ------------------------------------------------------------

print()
print("=" * 80)
print("TEST 4: TEXT-BASED COUNTRY / LOCATION VALUES")
print("=" * 80)

text_locations = df.loc[
    country_numeric.isna(),
    "country"
].fillna("Missing").astype(str).str.strip()

print(
    text_locations.value_counts().head(100).to_string()
)
print()


# ------------------------------------------------------------
# TEST 5: Country code + event name examples
# ------------------------------------------------------------

print("=" * 80)
print("TEST 5: COUNTRY CODE + EVENT NAME EXAMPLES")
print("=" * 80)

for code in numeric_codes:
    code = int(code)
    subset = df[country_numeric == code]

    print()
    print(f"CODE {code} — {len(subset):,} observations")

    events = (
        subset["event name"]
        .fillna("Missing")
        .astype(str)
        .value_counts()
        .head(15)
    )

    for event, count in events.items():
        print(f"  {count:5,} | {event}")


# ------------------------------------------------------------
# TEST 6: Save a compact investigation file
# ------------------------------------------------------------

print()
print("=" * 80)
print("TEST 6: SAVING RESULTS")
print("=" * 80)

summary_rows = []

for country_value, group in df.groupby(
    df["country"].astype(str).str.strip(),
    dropna=False
):
    summary_rows.append({
        "country_value": country_value,
        "observations": len(group),

        "most_common_auction_house": (
            group["auction_house"]
            .dropna()
            .astype(str)
            .value_counts()
            .index[0]
            if group["auction_house"].notna().any()
            else ""
        ),

        "most_common_nationality": (
            group["nationality"]
            .dropna()
            .astype(str)
            .value_counts()
            .index[0]
            if group["nationality"].notna().any()
            else ""
        ),

        "most_common_event": (
            group["event name"]
            .dropna()
            .astype(str)
            .value_counts()
            .index[0]
            if group["event name"].notna().any()
            else ""
        ),
    })

summary = pd.DataFrame(summary_rows)
summary = summary.sort_values("observations", ascending=False)

summary.to_csv(
    "country_code_investigation.csv",
    index=False,
    encoding="utf-8-sig"
)

print("Saved: country_code_investigation.csv")
print()
print("DONE.")
print()
print("IMPORTANT:")
print("Do NOT create the HomeBias variable yet.")
print("We first need to establish exactly what the numeric")
print("country codes mean.")