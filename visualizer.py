from MySQLClient import MysqlClient
from config import *
import seaborn as sns
import matplotlib.pyplot as plt
from dataclasses import dataclass
import datetime
import os


def get_year():
    some_filename = os.listdir("data")[0]
    return int(some_filename.split("-")[2])


def get_max_week_number():
    year = get_year()
    return datetime.date(year, 12, 28).isocalendar().week


@dataclass
class PlottingData:
    name: str
    query_params: list[str]
    x_ticks_count: int
    labels: list


class Visualizer:
    def __init__(self):
        self.mysql_client = MysqlClient(host, port, user, password, db_name)
        self.plotting_params = ["month", "week", "weekday", "start time"]
        self.year = get_year()

    def plot_distance(self, data: PlottingData):
        if data.name not in self.plotting_params:
            print(f"No such option: {data.name}. You can try `month`, `week` or `weekday`.")
            return

        datetime_dist_pairs = self.mysql_client.select(*data.query_params)
        distances_dict = {i + 1: 0 for i in range(data.x_ticks_count)}

        for pair in datetime_dist_pairs:
            if data.name == "month":
                number = pair["date"].month
            elif data.name == "weekday":
                number = pair["weekday"]
            elif data.name == "week":
                number = pair["week_num"]
            elif data.name == "start time":
                number = (int(str(pair["start_time"]).split(":")[0]) + 1) % 24

            # distance = int(pair["distance"]) # km
            distance = pair["distance"] / 1000 # m
            distances_dict[number] += distance

        sns.barplot(distances_dict, color="#C9716F")
        locs, labels = plt.xticks()
        plt.title(f"Distance by {data.name} in {self.year}")
        plt.xticks(locs, data.labels, fontsize=10)
        plt.xlabel(data.name)
        plt.ylabel("distance, km")
        plt.show()

    def plot_distance_by_month(self):
        month_abbreviations = ["ЯНВ", "ФЕВ", "МАРТ", "АПР", "МАЙ", "ИЮНЬ",
                               "ИЮЛЬ", "АВГ", "СЕН", "ОКТ", "НОЯ", "ДЕК"]
        month_data_to_plot = PlottingData("month", ["date", "distance"], 12, month_abbreviations)
        self.plot_distance(month_data_to_plot)

    def plot_distance_by_week(self):
        max_week_number = get_max_week_number()
        week_number_range = list(range(1, max_week_number + 1))
        week_data_to_plot = PlottingData("week", ["week_num", "distance"], max_week_number, week_number_range)
        self.plot_distance(week_data_to_plot)

    def plot_distance_by_weekday(self):
        weekday_abbreviations = ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]
        weekday_data_to_plot = PlottingData("weekday", ["weekday", "distance"], 7, weekday_abbreviations)
        self.plot_distance(weekday_data_to_plot)

    def plot_distance_by_start_times(self):
        hours_range = list(range(24))
        start_time_data_to_plot = PlottingData("start time", ["start_time", "distance"], 24, hours_range)
        self.plot_distance(start_time_data_to_plot)

    def plot_year_summary(self):
        pass
