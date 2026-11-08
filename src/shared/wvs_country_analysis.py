import pandas as pd

SURVEY_WAVE_NUMBER = 7

# Interesting questions
# --------------------
# Q21: On this list are arous groups of people. Could you please mention any that
# you would not like to have as neighbours? -> Q21 Immigrants/foreign workers
#   1. Mentioned, 2. Not mentioned
# --> Corresponds to Q6 V54 in EVS
#
# Q254: How prowd are you to be [country's nationality]?
#   1. Very proud, 2. Quite proud, 3. Not very proud, 4. Not at all proud, 5. I am not [country's nationality]
# --> Corresponds to Q72 V256 in EVS

QUESTION_OF_INTEREST = 254
QUESTION_EVS = 256
TARGET_RESPONSE = 1


WVS_FILE = "data/raw/WVS_Cross-National_Wave_7_csv_v6_0.csv"
EVS_FILE = "data/raw/EVS_2008.csv"

OUTPUT_FILE = "results/hello.csv"


# --------------------

COLUMN_WVS = "Q" + str(QUESTION_OF_INTEREST)
COLUMN_EVS = "v" + str(QUESTION_EVS)

df_wvs = pd.read_csv(WVS_FILE)
df_evs = pd.read_csv(EVS_FILE)

# Group by country
countries_wvs = {
    country: group
    for country, group in df_wvs.groupby("B_COUNTRY")
}

countries_evs = {
    country : group
    for country, group in df_evs.groupby("country")
}


def response_proportion(response, column, df):
    """
    Calculate the proportion of observations in which a given
    question has one specified response.
    
    
    Args:
        response (int): The target response value
        df (pandas.DataFrame): DataFrame containing the observations
    
    Returns:
        float: proportion of non-missing responses equal to target response
    """

    total_responses = 0
    total_hits = 0

    for observation in df[column]:
        if pd.notna(observation) and observation > 0:
            total_responses += 1

            if observation == response:
                total_hits += 1
    

    if total_responses == 0:
        return 0

    return total_hits / total_responses

# Print output
for country, country_df in countries_wvs.items():
    proportion = response_proportion(TARGET_RESPONSE, COLUMN_WVS, country_df)
    print(country)
    print(proportion)

for country, country_df in countries_evs.items():
    proportion = response_proportion(TARGET_RESPONSE, COLUMN_EVS, country_df)
    print(country)
    print(proportion)
