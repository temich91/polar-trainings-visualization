import os
import pandas as pd
from pprint import pprint

SUMMARY_COLUMNS = ['Date', 'Duration', 'Total distance (km)', 'Average heart rate (bpm)', 'Average pace (min/km)', ]
COLUMNS_TO_USE = ["Date", "Time", "HR (bpm)", "Cadence", "Altitude (m)"]

def split_csv():
    for csv in os.listdir("csv_output"):
        r_df = pd.read_csv("csv_output/" + csv)
        r_df.loc[0:0, SUMMARY_COLUMNS].to_csv(f"resumes/{csv}", index=False)

        date = r_df.loc[0:0, SUMMARY_COLUMNS]["Date"].values[0]

        t_df = pd.read_csv("csv_output/" + csv, skiprows=2)
        t_df["Date"] = date
        t_df.loc[:, COLUMNS_TO_USE].to_csv(f"total/{csv}", index=False)

def combine_csv(directory):
    with open(f"{directory}_out.csv", "ab") as fout:
        csv_list = os.listdir(directory)
        with open(f"{directory}/{csv_list[0]}", "rb") as f:
            fout.writelines(f)

        for csv in csv_list:
            if csv != csv_list[0]:
                with open(f"{directory}/" + csv, "rb") as f:
                    next(f)
                    fout.writelines(f)

split_csv()
combine_csv("resumes")
combine_csv("total")
