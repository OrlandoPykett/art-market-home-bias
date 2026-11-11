"""Interaction between home bias and national pride."""

def add_national_pride_interaction(df):
    df = df.copy()

    df["home_bias_national_pride"] = (
        df["home_bias"] * df["national_pride"]
    )

    return df