import os

import pandas as pd
import matplotlib.pyplot as plt
from pprint import pprint

SUMMARY_COLUMNS = ['Date', 'Duration', 'Total distance (km)', 'Average heart rate (bpm)', 'Average pace (min/km)', ]
COLUMNS_TO_USE = ["Time", "HR (bpm)", "Pace (min/km)", "Cadence", "Altitude (m)", "Distances (m)"]

COLUMN_NUMS = {idx: item for idx, item in enumerate(COLUMNS_TO_USE)}
COLORS = {
    "HR (bpm)": "red",
    "Pace (min/km)": "orange",
    "Cadence": "green",
    "Altitude (m)": "gray"
}


# pprint(df.columns)
# pprint(df.head())

def get_summary_from_csv(csv):
    df = pd.read_csv(csv, nrows=1, usecols=SUMMARY_COLUMNS)
    print(tuple(map(tuple, df[SUMMARY_COLUMNS].values.astype("str")))[0])

def get_details_from_csv(csv):
    df = pd.read_csv(csv, skiprows=2, usecols=COLUMNS_TO_USE)

def collect_data():
    data = []
    for csv in os.listdir("csv_output"):
        summary = get_summary_from_csv()
        if summary:
            data.append(summary)
    return data

def convert_mm_ss_to_ss(time_string):
    mm, ss = map(int, time_string.split(":"))
    return mm * 60 + ss


def plot_data(csv_path, type_, ticks_period=300):
    df = pd.read_csv(csv_path, skiprows=2, usecols=["Time", type_])
    x = range(len(df["Time"]))
    x_labels = df["Time"]
    y_labels = None

    if type_ == "Pace (min/km)":
        y = df["Pace (min/km)"].apply(convert_mm_ss_to_ss)
        y_labels = df[type_]

    elif type_ in ["HR (bpm)", "Altitude (m)", "Cadence"]:
        y = df[type_]

    else:
        print(f"No such type {type_}")

    plt.plot(x, y, color=COLORS[type_])
    plt.xticks(x[::ticks_period], x_labels[::ticks_period], rotation=45)
    if y_labels is not None:
        plt.yticks(y[::ticks_period], y_labels[::ticks_period])
    plt.title(type_)


# plotting test
# file = "csv_output/8079344501.csv"
# while True:
#     info = input("hr, pace, altitude or cadence (q for quit)")
#     if info == 'q':
#         break
#     if info == "hr":
#         plot_data(file, "HR (bpm)")
#     elif info == "pace":
#         plot_data(file, "Pace (min/km)")
#     elif info == "altitude":
#         plot_data(file, "Altitude (m)")
#     elif info == "cadence":
#         plot_data(file, "Cadence")
#     plt.show()
# get_summary_from_csv(file)
