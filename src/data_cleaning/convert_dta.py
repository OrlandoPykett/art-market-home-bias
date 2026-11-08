import pandas as pd

df = pd.read_stata(
    "data/raw/EVS_2008.dta",
    convert_categoricals=False
)

df.to_csv(
    "data/raw/EVS_2008.csv",
    index=False
)

print("Conversion complete.")