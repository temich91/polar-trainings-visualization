from json_parser import collect_trainings_data
from MySQLClient import MysqlClient
from config import *

if __name__ == "__main__":
    data = collect_trainings_data()
    client = MysqlClient(host, port, user, password, db_name)
    client.fill_table(data)
