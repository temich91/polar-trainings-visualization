from sqlalchemy import select
from models import *
from base_db_connector import BaseDBConnector
import pandas as pd


class DBExporter(BaseDBConnector):
    def __init__(self, db_path):
        super().__init__(db_path)

    def export_to_df(self, fields, user_id):
        with self.session_scope() as session:
            result_values = session.execute(select(*fields).where(Summary.user_id == user_id))
            return pd.DataFrame(result_values.fetchall(), columns=result_values.keys())

dbe = DBExporter("test.db")
cols = [Summary.duration, Summary.hr_avg, Summary.calories]
df = dbe.export_to_df(cols, 1)
print(df)
