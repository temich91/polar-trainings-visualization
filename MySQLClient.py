import pymysql


class MysqlClient:
    def __init__(self, host, port, user, password, db_name, year, data):
        try:
            self.connection = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                cursorclass=pymysql.cursors.DictCursor
            )

            self.year = year
            self.cursor = self.connection.cursor()
            self.create_db(db_name)
            self.create_table(data)

        except Exception as exception_message:
            print(exception_message)
            raise

    def check_table(self, table):
        """Checks if db exists
        :rtype bool
        """

        try:
            check_table_query = f"CHECK TABLE {table}"
            self.cursor.execute(check_table_query)
            return self.cursor.fetchall()[0]["Msg_text"] == "OK"

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

    def create_table(self, data):
        """
        Creates 'trainings' table if it doesn't exist.
        :rtype: None
        """

        try:
            if self.check_table(f"trainings_data_{self.year}"):
                return
            create_table_query = f"""CREATE TABLE IF NOT EXISTS trainings_data_{self.year} (
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
            self.fill_table(data)

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
            insert_data_query = """INSERT INTO trainings_data_{} (date,
                                                               week_num,
                                                               weekday,
                                                               distance,
                                                               avg_hr,
                                                               start_time,
                                                               stop_time,
                                                               kilocalories
                                                               ) VALUES {}""".format(self.year, ", ".join(data))

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
            delete_data_query = f"""DELETE FROM trainings_data_{self.year} WHERE id={id_}"""
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
                date_selection_query = f"SELECT DISTINCT {','.join(args)} FROM trainings_data_{self.year} " \
                                       f"GROUP BY {','.join(group_args)}"
            else:
                date_selection_query = f"SELECT DISTINCT {','.join(args)} FROM trainings_data_{self.year}"
        else:
            date_selection_query = f"SELECT {','.join(args)} FROM trainings_data_{self.year}"

        self.cursor.execute(date_selection_query)
        result = self.cursor.fetchall()
        return result
