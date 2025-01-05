from MySQLClient import MysqlClient
from config import *
import seaborn as sns
import matplotlib.pyplot as plt


class Visualizer:
    def __init__(self):
        self.mysql_client = MysqlClient(host, port, user, password, db_name)
        self.plotting_params = {
            "month": {"query_params": ["date", "distance"],
                      "x_ticks_count": 12,
                      "x_labels": ["ЯНВ", "ФЕВ", "МАРТ", "АПР", "МАЙ", "ИЮНЬ", "ИЮЛЬ", "АВГ", "СЕН", "ОКТ", "НОЯ", "ДЕК"]},
            "weekday": {"query_params": ["weekday", "distance"],
                        "x_ticks_count": 7,
                        "x_labels": ["ПН", "ВТ", "СР", "ЧТ", "ПТ", "СБ", "ВС"]}
        }

    def plot_distance(self, x):
        if x not in self.plotting_params:
            print(f"No such option: {x}. You can try `month`, `week` or `weekday`.")
            return

        datetime_dist_pairs = self.mysql_client.select(*self.plotting_params[x]["query_params"])
        x_ticks_count = self.plotting_params[x]["x_ticks_count"]
        x_labels = self.plotting_params[x]["x_labels"]
        distances_dict = {i + 1: 0 for i in range(x_ticks_count)}

        for pair in datetime_dist_pairs:
            if x == "month":
                number = pair["date"].month
            elif x == "weekday":
                number = pair["weekday"]
            # distance = int(pair["distance"]) # km
            distance = pair["distance"] / 1000 # m
            distances_dict[number] += distance

        sns.barplot(distances_dict)
        locs, labels = plt.xticks()
        plt.xticks(locs, x_labels)
        plt.ylabel("Расстояние, км")
        plt.show()

    def plot_distance_monthly(self):
        self.plot_distance("month")

    def plot_distance_weekly(self):
        self.plot_distance("week")

    def plot_distance_by_weekday(self):
        self.plot_distance("weekday")

    def plot_start_times(self):
        pass

    def plot_year_summary(self):
        pass


v = Visualizer()
v.plot_distance_monthly()
