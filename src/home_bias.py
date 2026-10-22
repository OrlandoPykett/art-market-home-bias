import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

# Data
# DF1 has 114283 observations
# DF2 has 16226 observations
# See -- for each dataset's variable list

df1 = pd.read_csv("data/cleaned/dataset1_cleaned.csv",
                  encoding="latin1",
                  low_memory=False
                  )
df2 = pd.read_csv("data/cleaned/dataset2_cleaned.csv",
                  encoding="latin1",
                  low_memory=False
                  )

# ------
# Variables
# ------

