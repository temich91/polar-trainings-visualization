from json_parser import collect_trainings_data
from MySQLClient import MysqlClient
from config import *
from visualizer import Visualizer


def main(year, data):
    """
    Menu for getting plots.
    :param year: year number to plot data about
    :return: None
    """
    vis = Visualizer(year, data)
    while True:
        command = input("Choose the period to plot summary (\n"
                        "`1` - by hours,\n"
                        "`2` - by weekdays,\n"
                        "`3` - by weeks,\n"
                        "`4` - by months,\n"
                        "`q` to exit)")
        if command == "q":
            return
        if command == "1":
            vis.plot_distance_by_start_times()
        elif command == "2":
            vis.plot_distance_by_weekday()
        elif command == "3":
            vis.plot_distance_by_week()
        elif command == "4":
            vis.plot_distance_by_month()
        else:
            print("Unknown option")


if __name__ == "__main__":
    year = input("Number of year to plot summary:")
    data = collect_trainings_data(year)
    client = MysqlClient(host, port, user, password, db_name, year, data)
    main(year, data)
