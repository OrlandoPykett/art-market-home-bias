import pandas as pd

DATA_FILE = "transactions.csv"

df = pd.read_csv(
    DATA_FILE,
    encoding="latin1",
    low_memory=False
)

# Convert country to string
df["country"] = df["country"].astype(str).str.strip()

# Numeric codes
country_numeric = pd.to_numeric(df["country"], errors="coerce")

numeric_codes = sorted(
    country_numeric.dropna().unique()
)

print("=" * 80)
print("VALIDATING NUMERIC COUNTRY CODES")
print("=" * 80)

# Known city -> country relationships
city_country = {
    # USA
    "New York": "USA",
    "Chicago": "USA",
    "Los Angeles": "USA",
    "San Francisco": "USA",
    "Boston": "USA",
    "Philadelphia": "USA",
    "Dallas": "USA",
    "Miami": "USA",
    "Detroit": "USA",
    "Washington": "USA",
    "Van Nuys": "USA",
    "Lambertville": "USA",
    "East": "USA",
    "S.F. & L.A.": "USA",

    # UK
    "London": "UK",
    "South Kensington": "UK",
    "Olympia": "UK",
    "Knightsbridge": "UK",
    "Kensington": "UK",
    "Edinburgh": "UK",

    # France
    "Paris": "France",
    "Paris - Drouot": "France",
    "Marseille": "France",
    "Versailles": "France",
    "Deauville": "France",
    "Lyon Cedex 06": "France",
    "Rennes": "France",
    "Vannes": "France",
    "Cannes": "France",
    "Fontainebleau": "France",

    # Germany
    "Cologne": "Germany",
    "Munich": "Germany",
    "Berlin": "Germany",
    "Hamburg": "Germany",
    "Stuttgart": "Germany",
    "Frankfurt": "Germany",
    "Heidelberg": "Germany",
    "Bremen": "Germany",
    "Bielefeld": "Germany",
    "Duesseldorf": "Germany",
    "Dusseldorf": "Germany",
    "Heilbronn": "Germany",
    "Essen-Ruetenscheid": "Germany",
    "Saarbrucken/Scheidt": "Germany",
    "Ahlden": "Germany",
    "Staufen": "Germany",
    "Lindau": "Germany",

    # Italy
    "Milan": "Italy",
    "Vercelli": "Italy",
    "Prato": "Italy",
    "Florence": "Italy",
    "Naples": "Italy",
    "Rome": "Italy",
    "Turin": "Italy",
    "Genoa": "Italy",
    "Brescia": "Italy",
    "Torino": "Italy",
    "Trieste": "Italy",
    "Venice": "Italy",

    # Austria
    "Vienna": "Austria",
    "Graz": "Austria",

    # Switzerland
    "Zurich": "Switzerland",
    "Lucerne": "Switzerland",
    "Bern": "Switzerland",
    "Geneva": "Switzerland",
    "Geneve": "Switzerland",
    "St. Gallen": "Switzerland",

    # Belgium
    "Brussels": "Belgium",
    "Brussells": "Belgium",
    "Antwerp": "Belgium",
    "Antwerp-Berchem": "Belgium",
    "Lokeren": "Belgium",

    # Sweden
    "Stockholm": "Sweden",
    "Uppsala": "Sweden",
    "Lund": "Sweden",

    # Denmark
    "Copenhagen": "Denmark",
    "Bredgade": "Denmark",

    # Norway
    "Oslo": "Norway",

    # Spain
    "Madrid": "Spain",

    # Portugal
    "Lisbon": "Portugal",

    # Brazil
    "Sao Paulo": "Brazil",
    "Rio de Janeiro": "Brazil",

    # Venezuela
    "Caracas": "Venezuela",

    # China
    "Shanghai": "China",
    "Beijing": "China",

    # Japan
    "Tokyo": "Japan",

    # South Korea
    "Seoul": "South Korea",

    # India
    "Mumbai": "India",

    # South Africa
    "Johannesburg": "South Africa",
    "Cape Town": "South Africa",

    # Argentina
    "Buenos Aires": "Argentina",

    # Canada
    "Toronto": "Canada",
    "Vancouver": "Canada",
    "Calgary": "Canada",

    # Australia
    "Melbourne": "Australia",
    "Sydney": "Australia",
    "South Yarra": "Australia",
    "South Yarra - Melbourne": "Australia",

    # Brazil
    "Sao Paulo": "Brazil",
    "Rio de Janeiro": "Brazil",
}


# ------------------------------------------------------------
# For each numeric code, find text locations associated
# with the same auction house.
# ------------------------------------------------------------

for code in numeric_codes:

    code = int(code)

    numeric_subset = df[country_numeric == code]

    print()
    print("=" * 80)
    print(f"CODE {code}")
    print(f"Numeric observations: {len(numeric_subset):,}")
    print("=" * 80)

    # Most common auction houses for this code
    auction_houses = (
        numeric_subset["auction_house"]
        .dropna()
        .astype(str)
        .value_counts()
        .head(5)
    )

    print("\nMost common auction houses:")
    print(auction_houses.to_string())

    # Find text locations using those auction houses
    top_houses = auction_houses.index.tolist()

    matching_text = df[
        df["auction_house"].isin(top_houses)
        & country_numeric.isna()
    ]

    print("\nText locations associated with these auction houses:")

    locations = (
        matching_text["country"]
        .value_counts()
        .head(15)
    )

    if len(locations) == 0:
        print("  No text locations found.")
    else:
        print(locations.to_string())

    # Try to identify known countries from those locations
    identified = []

    for location in locations.index:
        if location in city_country:
            identified.append(
                (location, city_country[location])
            )

    if identified:
        print("\nKnown city -> country matches:")
        for location, country in identified:
            print(f"  {location} -> {country}")
    else:
        print("\nNo known city matches found.")


print()
print("=" * 80)
print("DONE")
print("=" * 80)
print()