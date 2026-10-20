import pandas as pd

# Contemporary Art
df = pd.read_stata("data/raw/contempp.dta")
df.to_csv("contemporary_art.csv", index=False)

# Impressionist Art
df = pd.read_stata("data/raw/impresss.dta")
df.to_csv("impressionist_art.csv", index=False)

print("Conversion complete.")