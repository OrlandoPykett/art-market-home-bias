import pandas as pd

SURVEY_WAVE_NUMBER = 7

# Interesting questions
# --------------------
# Q21: On this list are arous groups of people. Could you please mention any that
# you would not like to have as neighbours? -> Q21 Immigrants/foreign workers
#   1. Mentioned, 2. Not mentioned
#
# Q254: How prowd are you to be [country's nationality]?
#   1. Very proud, 2. Quite proud, 3. Not very proud, 4. Not at all proud, 5. I am not [country's nationality]

QUESTION_OF_INTEREST = 254
TARGET_RESPONSE = 4

INPUT_FILE = "data/raw/WVS_Cross-National_Wave_7_csv_v6_0.csv"
OUTPUT_FILE = "results/hello.csv"


# --------------------

COLUMN = "Q" + str(QUESTION_OF_INTEREST)

df = pd.read_csv(INPUT_FILE)

# Group by country
countries = {
    country: group
    for country, group in df.groupby("B_COUNTRY")
}


def response_proportion(response, df):
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

    for observation in df[COLUMN]:
        if pd.notna(observation) and observation > 0:
            total_responses += 1

            if observation == response:
                total_hits += 1
    

    if total_responses == 0:
        return 0

    return total_hits / total_responses

# Print output
for country, country_df in countries.items():
    proportion = response_proportion(TARGET_RESPONSE, country_df)
    print(country)
    print(proportion)



