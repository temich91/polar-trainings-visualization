from config import *
import pymysql


class MysqlClient:
    def __init__(self, host, port, user, password, db_name):
        try:
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=db_name,
                cursorclass=pymysql.cursors.DictCursor
            )

            self.cursor = self.connection.cursor()
            self.create_db(db_name)
            self.create_table()

        except Exception as exception_message:
            print(exception_message)
            raise

    def create_db(self, db):
        """Creates database if it doesn't exist."""
        try:
            create_db_query = f"CREATE DATABASE IF NOT EXISTS {db}"
            self.cursor.execute(create_db_query)

        except Exception as exception_message:
            print(exception_message)
            raise

    def create_table(self):
        """Creates 'trainings' table if it doesn't exist."""
        try:
            create_table_query = """CREATE TABLE IF NOT EXISTS trainings_data (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        date DATE,
                                        week_num INT,
                                        distance FLOAT,
                                        avg_hr INT,
                                        start_time TIME,
                                        stop_time TIME,
                                        kilocalories INT                                        
            )"""
            self.cursor.execute(create_table_query)
            self.connection.commit()

        except Exception as exception_message:
            print(exception_message)
            raise

    def insert(self, date, week_num, distance, avg_hr, start_time, stop_time, kilocalories):
        """Inserts summary data of training into table 'trainings_data'."""
        try:
            insert_data_query = f"""INSERT INTO trainings_data (date, week_num, distance, avg_hr, start_time, stop_time, kilocalories)
                                   VALUES ("{date}", {week_num}, {distance}, {avg_hr},
                                           "{start_time}", "{stop_time}", {kilocalories})                     
                                """
            self.cursor.execute(insert_data_query)
            self.connection.commit()

        except Exception as exception_message:
            print(exception_message)
            raise

    def delete(self, id_):
        """Deletes row from 'trainings_data' table by its id"""
        try:
            delete_data_query = f"""DELETE FROM trainings_data WHERE id={id_}
                                """
            self.cursor.execute(delete_data_query)
            self.connection.commit()

        except Exception as exception_message:
            print(exception_message)
            raise
