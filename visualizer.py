from MySQLClient import MysqlClient
from config import *
import seaborn as sns
import matplotlib.pyplot as plt
from dataclasses import dataclass
import datetime


def get_max_week_number(year):
    """
    Get maximum number of week in specific year
    :return: int
    """
    return datetime.date(int(year), 12, 28).isocalendar().week


@dataclass
class PlottingData:
    """
    Dataclass for plot configuration
    name: period (hour, weekday, week, month)
    query_params: columns to select in database
    x_ticks_count: number of ticks at x-axis
    labels: labels for x-axis ticks
    group_args: columns to group by when select unique values
    """
    name: str
    query_params: list[str]
    distinct_query_params: list[str]
    x_ticks_count: int
    labels: list
    group_args: list[str] = None


class Visualizer:
    """
    Configure and plot summary about running trainings by different periods
    """
    def __init__(self, year, data):
        self.mysql_client = MysqlClient(host, port, user, password, db_name, year, data)
        self.plotting_params = ["month", "week", "weekday", "start time"]
        self.y_options = ["distance (km)", "quantity"]
        self.year = year

    def get_plot_data(self, data: PlottingData, plot_attr):
        """
        Prepares trainings data from database
        :param data: PlottingData parameters of period for plot
        :param plot_attr: `distance` or `quantity`, training attribute to count
        :return: dict of plot axes data
        """
        if data.name not in self.plotting_params:
            print(f"No such option: {data.name}. You can try `month`, `week`, `weekday` or `start time`.")
            return

        data_pairs = []
        if plot_attr == "distance":
            data_pairs = self.mysql_client.select(*data.query_params)
        elif plot_attr == "quantity":
            data_pairs = self.mysql_client.select(*data.distinct_query_params,
                                                  is_distinct=True, group_args=data.group_args)

        data_dict = {i + 1: 0 for i in range(data.x_ticks_count)}
        for pair in data_pairs:
            if data.name == "month":
                number = pair["date"].month
            elif data.name == "weekday":
                number = pair["weekday"]
            elif data.name == "week":
                number = pair["week_num"]
            elif data.name == "start time":
                if plot_attr == "distance":
                    number = (int(str(pair["start_time"]).split(":")[0]) + 1) % 24
                elif plot_attr == "quantity":
                    number = (int(str(pair["min(start_time)"]).split(":")[0]) + 1) % 24

            if plot_attr == "distance":
                distance = pair["distance"] / 1000
                data_dict[number] += distance
            elif plot_attr == "quantity":
                data_dict[number] += 1

        return data_dict

    def plot(self, data: PlottingData):
        """
        Draw barchart of trainings distance and count for specific periods (hours, weekday, weeks, months)
        :param data: dict of plot axes data
        :return: None
        """
        distance_data = self.get_plot_data(data, "distance")
        quantity_data = self.get_plot_data(data, "quantity").values()
        ax = sns.barplot(distance_data, color="#C9716F")
        ax.bar_label(ax.containers[0], labels=quantity_data, size=10)
        locs, labels = plt.xticks()
        plt.title(f"Distance by {data.name} in {self.year}")
        plt.xticks(locs, data.labels, fontsize=10)
        plt.xlabel(data.name)
        plt.ylabel("distance, km")
        plt.show()

    def plot_distance_by_month(self):
        """
        Configure query parameters and plot barchart for monthly trainings
        :return: None
        """
        month_abbreviations = ["JAN", "FEB", "MAR", "APR", "MAY", "JUNE",
                               "JULE", "AUG", "SEN", "OCT", "NOV", "DEC"]
        month_data_to_plot = PlottingData("month", ["date", "distance"], ["date"], 12, month_abbreviations)
        self.plot(month_data_to_plot)

    def plot_distance_by_week(self):
        """
        Configure query parameters and plot barchart for weekly trainings
        :return: None
        """
        max_week_number = get_max_week_number(self.year)
        week_number_range = list(range(1, max_week_number + 1))
        week_data_to_plot = PlottingData("week", ["week_num", "distance"], ["date", "week_num"], max_week_number, week_number_range)
        self.plot(week_data_to_plot)

    def plot_distance_by_weekday(self):
        """
        Configure query parameters and plot barchart for trainings by day of the week
        :return: None
        """
        weekday_abbreviations = ["MON", "TUE", "WED", "THR", "FRI", "SAT", "SUN"]
        weekday_data_to_plot = PlottingData("weekday", ["weekday", "distance"], ["date", "weekday"], 7, weekday_abbreviations)
        self.plot(weekday_data_to_plot)

    def plot_distance_by_start_times(self):
        """
        Configure query parameters and plot barchart for trainings by every hour
        :return: None
        """
        hours_range = list(range(24))
        start_time_data_to_plot = PlottingData("start time", ["start_time", "distance"], ["date", "min(start_time)"], 24, hours_range, group_args=["date"])
        self.plot(start_time_data_to_plot)

    def plot_year_summary(self):
        pass
