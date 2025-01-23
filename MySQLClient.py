import pymysql


class MysqlClient:
    def __init__(self, host, port, user, password, db_name):
        try:
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                cursorclass=pymysql.cursors.DictCursor
            )

            self.cursor = self.connection.cursor()
            self.create_db(db_name)
            self.create_table()

        except Exception as exception_message:
            print(exception_message)
            raise

    def create_db(self, db):
        """
        Creates database if it doesn't exist.
        :rtype: None
        """

        try:
            create_db_query = f"CREATE DATABASE IF NOT EXISTS {db}"
            self.cursor.execute(create_db_query)
            self.connection.select_db(db)

        except Exception as exception_message:
            print(exception_message)
            raise

    def create_table(self):
        """
        Creates 'trainings' table if it doesn't exist.
        :rtype: None
        """

        try:
            create_table_query = """CREATE TABLE IF NOT EXISTS trainings_data (
                                        id INT AUTO_INCREMENT PRIMARY KEY,
                                        date DATE,
                                        week_num INT,
                                        weekday INT,
                                        distance FLOAT,
                                        avg_hr INT,
                                        start_time TIME,
                                        stop_time TIME,
                                        kilocalories INT)"""
            self.cursor.execute(create_table_query)
            self.connection.commit()

        except Exception as exception_message:
            print(exception_message)
            raise

    def fill_table(self, data):
        """
        Inserts summary data of training into table 'trainings_data'.
        :param data: list of date, week number, weekday number, start and stop times,
                     distance, average heartrate, kilocalories.
        :rtype: None
        """

        try:
            insert_data_query = """INSERT INTO trainings_data (date,
                                                               week_num,
                                                               weekday,
                                                               distance,
                                                               avg_hr,
                                                               start_time,
                                                               stop_time,
                                                               kilocalories
                                                               ) VALUES {}""".format(", ".join(data))

            self.cursor.execute(insert_data_query)
            self.connection.commit()

        except Exception as exception_message:
            print(exception_message)
            raise

    def delete(self, id_):
        """
        Deletes row from 'trainings_data' table by its id
        :rtype: None
        """

        try:
            delete_data_query = f"""DELETE FROM trainings_data WHERE id={id_}"""
            self.cursor.execute(delete_data_query)
            self.connection.commit()

        except Exception as exception_message:
            print(exception_message)
            raise

    def select(self, *args, is_distinct=False, group_args=None):
        """
        Executes selection query
        :param args: columns' name to select
        :param is_distinct: if True selects unique values
        :param group_args: if is_distinct, columns to group by
        :return:
        """
        if is_distinct:
            if group_args:
                date_selection_query = f"SELECT DISTINCT {','.join(args)} FROM trainings_data" \
                                       f"GROUP BY {','.join(group_args)}"
            else:
                date_selection_query = f"SELECT DISTINCT {','.join(args)} FROM trainings_data"
        else:
            date_selection_query = f"SELECT {','.join(args)} FROM trainings_data"
        self.cursor.execute(date_selection_query)
        result = self.cursor.fetchall()
        return result
