import os
from sqlalchemy import insert
import pandas as pd
from models import Summary, Telemetry
from src.utils import constants as c
from tqdm import tqdm
from src.utils.paths import *
from base_db_connector import BaseDBConnector


def timestamp_to_seconds(timestamp):
    if timestamp.count(":") == 1:
        timestamp = f"00:{timestamp}"
    hh, mm, ss = map(int, timestamp.split(":"))
    return hh * 3600 + mm * 60 + ss

def date_to_isoformat(date):
    dd, mm, yyyy = date.split(".")
    return f"{yyyy}-{mm}-{dd}"

def split_csv(user_id, file_path):
    session_id = os.fspath(file_path).split("\\")[-1][:-4]
    summary = transform_summary(user_id, session_id, file_path)
    telemetry = transform_telemetry(user_id, session_id, file_path)
    return summary, telemetry

def transform_summary(user_id, session_id, file_path):
    summ_df = pd.read_csv(file_path, nrows=1, usecols=c.SUMMARY_COLS)
    summ_df.rename(columns=c.NEW_SUMMARY_COLS, inplace=True)
    summ_df = summ_df.fillna(value=c.SUMMARY_FILL_VALUES)
    summ_df.insert(loc=0, column="user_id", value=user_id)
    summ_df.insert(loc=1, column="session_id", value=session_id)
    summ_df["start_datetime"] = summ_df["Date"].apply(lambda date: date_to_isoformat(date)) + "T" + summ_df["start_datetime"]
    summ_df["duration"] = summ_df["duration"].apply(lambda time: timestamp_to_seconds(time))
    summ_df["pace_avg"] = summ_df["pace_avg"].apply(lambda time: timestamp_to_seconds(time))
    summ_df["pace_max"] = summ_df["pace_max"].apply(lambda time: timestamp_to_seconds(time))
    summ_df = summ_df.drop(columns=["Date"])
    return summ_df

def transform_telemetry(user_id, session_id, file_path):
    tel_df = pd.read_csv(file_path, skiprows=2, usecols=c.TELEMETRY_COLS)
    tel_df.rename(columns=c.NEW_TELEMETRY_COLS, inplace=True)
    tel_df = tel_df.fillna(value=c.TELEMETRY_FILL_VALUES)
    tel_df.insert(loc=0, column="user_id", value=user_id)
    tel_df.insert(loc=1, column="session_id", value=session_id)
    tel_df["time"] = tel_df["time"].apply(lambda time: timestamp_to_seconds(time))
    tel_df["pace"] = tel_df["pace"].apply(lambda time: timestamp_to_seconds(time))
    return tel_df

class DBImporter(BaseDBConnector):
    def __init__(self, db_path):
        super().__init__(db_path)

    def import_csv(self, user_id, csv_dir=BASE_DIR / "csv_export"):
        for csv in tqdm(os.listdir(csv_dir), desc="csv processed"):
            summary_df, telemetry_df = split_csv(user_id, csv_dir / csv)
            with self.session_scope() as session:
                session.execute(insert(Summary), summary_df.to_dict(orient="records"))
                session.execute(insert(Telemetry), telemetry_df.to_dict(orient="records"))


if __name__ == "__main__":
    connector = DBImporter("test.db")
    connector.import_csv(1)
    connector.close()
