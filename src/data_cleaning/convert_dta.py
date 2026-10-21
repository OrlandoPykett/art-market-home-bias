import pandas as pd

df = pd.read_stata("data/raw/dataset")
df.to_csv("dataset.csv", index=False)

print("Conversion complete.")