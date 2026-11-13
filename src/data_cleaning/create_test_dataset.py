import pandas as pd

df = pd.read_csv("data.csv")

# 80% training, 20% testing
train_df = df.sample(frac=0.8, random_state=42)
test_df = df.drop(train_df.index)

train_df.to_csv("train_dataset.csv", index=False)
test_df.to_csv("test_dataset.csv", index=False)