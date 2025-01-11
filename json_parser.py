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

    with open(f"data/{json_file_name}", "r", encoding="UTF-8") as file:
        data = json.load(file)
        if "name" not in data:
            avg_hr = 0
            kilocalories = 0
        elif data["name"] == "Бег":
            avg_hr = data["averageHeartRate"]
            kilocalories = data["kiloCalories"]
        else:
            print(data["name"]) # Р‘РµРі
            return False
        start_datetime = data["startTime"]
        date, start_time = start_datetime.split("T")
        distance = int(data["distance"])
        week_number, weekday = get_week_data(date)
        date = f"'{date}'"
        start_time = f"'{start_time[:8]}'"
        stop_time = "'{}'".format(data["stopTime"].split("T")[1][:8])

        summary = f"({date}, {week_number}, {weekday}, {distance}, {avg_hr}, {start_time}, {stop_time}, {kilocalories})"

    return summary


def collect_trainings_data():
    data = []
    for training_json in os.listdir("data"):
        summary = get_training_summary_from_json(training_json)
        if summary:
            data.append(summary)
        else:
            print(summary)
            print(training_json)
            os.remove(f"data/{training_json}")
    return data
