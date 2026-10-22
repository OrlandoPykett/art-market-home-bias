import pandas as pd

df1 = pd.read_csv("data/raw/transactions.csv",
                  encoding="latin1",
                  low_memory=False)
df2 = pd.read_csv("data/raw/impressionist_art.csv",
                  encoding="latin1",
                  low_memory=False)

df1.columns = df1.columns.str.strip()
df2.columns = df2.columns.str.strip()

df1_keep_columns = [
    #"alive_id", every value is NA
    "artist_name", # Format: Forename Surname
    "nationality",
    "Year of Birth",
    "year_of_artwork",
    "genre",
    "auction_house",
    "country",
    "price_usd",
    "real_price_usd",
    "event_year",
    "Ham_Prem",
    "materials",
    "height",
    "width",
    "depth",
    #"size (inch by inch)"
]

df2_keep_columns = [
    "DIM_A", # Dimension A
    "S_PRICE",
    "CNV_RATE", # Local currency to dollars
    "DATE_PTG", # Date of artwork creation
    "SHAPE",
    "DIM_B", # Dimension B
    "DIAM", # Diameter
    "SIGNED",
    "ART_MED",
    "ILLUS", # Illustration boolean
    "HOUSE",
    "AUCT_LOC",
    #"AUCT_DAT" # Auction date format: ddMONTHyy
    "ANAME", # Artist name format: SURNAMEFORENAME
    "ydate", # Year
    #"newdate" # Date format: yyyy-mm-dd
]


df1 = df1[
    [col for col in df1_keep_columns if col in df1.columns]
].copy()

df2 = df2[
    [col for col in df2_keep_columns if col in df2.columns]
].copy()


# Standardise column names
df1 = df1.rename(columns={
    "artist_name": "artist_name",
    "nationality": "artist_country",
    "Year of Birth": "artist_birth_y",
    "year_of_artwork": "artwork_y",
    "genre": "genre",
    "auction_house": "auction_house",
    "country": "sale_country",
    "price_usd": "price_usd",
    "real_price_usd": "real_price_usd",
    "event_year": "sale_y",
    "Ham_Prem": "Ham_Prem",
    "materials": "materials",
    "height": "height",
    "width": "width",
    "depth": "depth",
    #"size (inch by inch)": "size"
})

df2 = df2.rename(columns={
        "DIM_A": "height",
        "S_PRICE": "price",
        "DATE_PTG": "artwork_y", 
        "SHAPE": "shape",
        "DIM_B": "width", 
        "DIAM": "diameter",
        "SIGNED": "signed",
        "ART_MED": "medium",
        "ILLUS": "illustration",
        "HOUSE": "auction_house",
        "AUCT_LOC": "auction_location",
        "ANAME": "artist_name", 
        "ydate": "sale_y", 
})

# Standardise text fields
for col in [
    "artist_name",
    "auction_house",
    "auction_location",
    "materials",
    "medium"
]:
    if col in df1.columns:
        df1[col] = df1[col].astype("string").str.strip()
    if col in df2.columns:
        df2[col] = df2[col].astype("string").str.strip()


# Standardise name format
# Convert from df1 to format SURNAMEFORENAME
def format_artist(name):

    if pd.isna(name):
        return pd.NA

    name = str(name).strip()

    if not name:
        return pd.NA

    parts = name.split()

    surname_particles = {
        "VAN", "VON", "DE", "DEL", "DELLA", "DA", "DI", "DU", "LE", "LA", "DES"
    }

    surname_start = len(parts) - 1

    while surname_start > 0 and parts[surname_start - 1] in surname_particles:
        surname_start -= 1

    surname = "".join(parts[surname_start:])
    forename = "".join(parts[:surname_start])

    return (surname + forename).upper()


df1["artist_name"] = df1["artist_name"].apply(format_artist)


# Save cleaned datasets
df1.to_csv("data/cleaned/dataset1_cleaned.csv", index=False)
df2.to_csv("data/cleaned/dataset2_cleaned.csv", index=False)