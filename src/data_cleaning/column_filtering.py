import pandas as pd

def filter_df(file_name, columns_to_keep):
    file_path = "data/raw/" + file_name

    df = pd.read_csv(file_path, sep=";")
    df_filtered = df[columns_to_keep]

    output = "data/raw/wvs_and_evs_data/" + file_name
    df_filtered.to_csv(output, index=False)

# EVS
# --------------------

evs_2008 = "EVS_2008.csv"
columns_2008 = ["country", "v54", "v256"]
#filter_df(evs_2008, columns_2008)

evs_1999 = "EVS_1999.csv"
columns_1999 = ["country", "v60", "v255"]
#filter_df(evs_1999, columns_1999)

evs_1990 = "EVS_1990.csv"
columns_1990 = ["country", "q224i", "q650"]
#filter_df(evs_1990, columns_1990)

evs_1981 = "EVS_1981.csv"
columns_1981 = ["country", "v155", "v536"]
#filter_df(evs_1981, columns_1981)

# WVS
# --------------------
wvs_wave1 = "WVS_wave_1.csv"
columns_wvs_1 = ["V2", "V57", "V205"] 
filter_df(wvs_wave1, columns_wvs_1)

wvs_wave2 = "WVS_wave_2.csv"
columns_wvs_2 = ["V2", "V77", "V322"]
filter_df(wvs_wave2, columns_wvs_2)

wvs_wave3 = "WVS_wave_3.csv"
columns_wvs_3 = ["V2", "V57", "V205"]
filter_df(wvs_wave3, columns_wvs_3)

wvs_wave4 = "WVS_wave_4.csv"
columns_wvs_4 = ["V2", "V73", "V216"]
filter_df(wvs_wave4, columns_wvs_4)

wvs_wave5 = "WVS_wave_5.csv"
columns_wvs_5 = ["V2", "V37", "V209"]
filter_df(wvs_wave5, columns_wvs_5)

wvs_wave6 = "WVS_wave_6.csv"
columns_wvs_6 = ["V2", "V39", "V211"]
filter_df(wvs_wave6, columns_wvs_6)