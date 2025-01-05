import os
import json
import datetime


def get_week_data(date):
    """
    :param date: str
    :return: pair of week number and number of weekday
    :rtype: list
    """

    year, month, day = map(int, date.split("-"))
    isoformat_date = datetime.date(year, month, day).isocalendar()
    return [isoformat_date.week, isoformat_date.weekday]


def get_training_summary_from_json(json_file_name):
    """
    :param json_file_name: str
    :return: date (YYYY-MM-DD), week number, weekday, distance (meters), average heartrate (bpm),
             start and stop times (hh:mm:ss), kilocalories.
    :rtype: str
    """

    with open(f"data/{json_file_name}", "r") as file:
        data = json.load(file)
        start_datetime = data["startTime"]
        date, start_time = start_datetime.split("T")
        distance = int(data["distance"])
        week_number, weekday = get_week_data(date)
        date = f"'{date}'"
        start_time = f"'{start_time[:8]}'"
        stop_time = "'{}'".format(data["stopTime"].split("T")[1][:8])
        if "averageHeartRate" not in data:
            avg_hr = 0
            kilocalories = 0
        else:
            avg_hr = data["averageHeartRate"]
            kilocalories = data["kiloCalories"]

        summary = f"({date}, {week_number}, {weekday}, {distance}, {avg_hr}, {start_time}, {stop_time}, {kilocalories})"

    return summary


def collect_trainings_data():
    data = []
    i = 0
    for training_json in os.listdir("data"):
        i += 1
        data.append(get_training_summary_from_json(training_json))
    return data
