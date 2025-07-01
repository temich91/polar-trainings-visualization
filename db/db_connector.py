import os
from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
import pandas as pd
from models import Base, Account, Summary, Telemetry

DB_NAME = "trainings.db"
DEFAULT_CSV_DIR = "../csv_export"

SUMMARY_COLS = ["Date",
                "Start time",
                "Duration",
                "Total distance (km)",
                "Average heart rate (bpm)",
                "Average pace (min/km)",
                "Max pace (min/km)",
                "Ascent (m)",
                "Descent (m)",
                "Calories",
                "Average cadence (rpm)"]

TELEMETRY_COLS = ["Time",
                  "HR (bpm)",
                  "Pace (min/km)",
                  "Cadence",
                  "Altitude (m)"]

NEW_SUMMARY_COLS = {"Start time": "start_datetime",
                    "Duration": "duration",
                    "Total distance (km)": "distance",
                    "Average heart rate (bpm)": "hr_avg",
                    "Average pace (min/km)": "pace_avg",
                    "Max pace (min/km)": "pace_max",
                    "Ascent (m)": "ascent",
                    "Descent (m)": "descent",
                    "Calories": "calories",
                    "Average cadence (rpm)": "cadence_avg"}

NEW_TELEMETRY_COLS = {"Time": "time",
                      "HR (bpm)": "hr",
                      "Pace (min/km)": "pace",
                      "Cadence": "cadence",
                      "Altitude (m)": "altitude"}

def timestamp_to_seconds(timestamp):
    try:
        if timestamp.count(":") == 1:
            timestamp = f"00:{timestamp}"
        hh, mm, ss = map(int, timestamp.split(":"))
        return hh * 3600 + mm * 60 + ss
    except Exception as e:
        print(timestamp)

def split_csv(user_id, file_path):
    session_id = file_path.split("/")[-1][:-4]
    summary = transform_summary(user_id, session_id, file_path)
    telemetry = transform_telemetry(user_id, session_id, file_path)
    return summary, telemetry

def transform_summary(user_id, session_id, file_path):
    summ_df = pd.read_csv(file_path, nrows=1, usecols=SUMMARY_COLS)
    summ_df.rename(columns=NEW_SUMMARY_COLS, inplace=True)
    summ_df.insert(loc=0, column="user_id", value=user_id)
    summ_df.insert(loc=1, column="session_id", value=session_id)
    summ_df["start_datetime"] = summ_df["Date"].str.replace(".", "-") + "T" + summ_df["start_datetime"]
    summ_df["duration"] = summ_df["duration"].apply(lambda time: timestamp_to_seconds(time))
    summ_df["pace_avg"] = summ_df["pace_avg"].apply(lambda time: timestamp_to_seconds(time))
    summ_df["pace_max"] = summ_df["pace_max"].apply(lambda time: timestamp_to_seconds(time))
    summ_df = summ_df.drop(columns=["Date"])
    return summ_df

def transform_telemetry(user_id, session_id, file_path):
    tel_df = pd.read_csv(file_path, skiprows=2, usecols=TELEMETRY_COLS)
    tel_df.rename(columns=NEW_TELEMETRY_COLS, inplace=True)
    tel_df.insert(loc=0, column="user_id", value=user_id)
    tel_df.insert(loc=1, column="session_id", value=session_id)
    tel_df["time"] = tel_df["time"].apply(lambda time: timestamp_to_seconds(time))
    tel_df["pace"] = tel_df["pace"].apply(lambda time: timestamp_to_seconds(time))
    return tel_df

class DatabaseConnector:
    def __init__(self, db_name):
        db_url = f"sqlite:///{db_name}"
        self.engine = create_engine(db_url)
        Base.metadata.create_all(bind=self.engine)
        Session = sessionmaker(bind=self.engine) # add session factory
        self.session = Session()

    def load_from_csv(self, user_id, csv_dir=DEFAULT_CSV_DIR):
        for csv in os.listdir(csv_dir):
            summary_df, telemetry_df = split_csv(user_id, csv_dir + "/" + csv)
            self.session.execute(insert(Summary), summary_df.to_dict(orient="records"))
            self.session.execute(insert(Telemetry), telemetry_df.to_dict(orient="records"))


if __name__ == "__main__":
    connector = DatabaseConnector(DB_NAME)
    connector.load_from_csv("../test")