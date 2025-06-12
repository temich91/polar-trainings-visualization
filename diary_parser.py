from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import json
import requests
import polar_config
import time
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta

from test import split_period

"""
TODO:
    - docker with webdriver
    - Other languages localization (file with words parser looks for on pages)
    - Constants in separate file
    - Decent check of cookies file
    - Send progress messages to GUI
    - Load user data from db
"""

FLOW_URL = "https://flow.polar.com"
ELEMENT_VISIBILITY_TIMEOUT = 10
COOKIE_DECLINE_BTN_CLASS = "CybotCookiebotDialogBodyButtonDecline"
MONTHS_SWITCHER_CLASS = "picker-switch__link.picker-switch-days"
YEARS_SWITCHER_CLASS = "picker-switch__link.picker-switch-months"
SWITCHER_LEFT_ARROW_CLASS = "icon.icon-arrow-left.picker-previous-button"
SWITCHER_RIGHT_ARROW_CLASS = "icon.icon-arrow-right.picker-next-button"
KEEP_SIGNED_IN_ID = "checkbox_keep_me_signed_in"
COOKIES_DIALOG_ID = "CybotCookiebotDialogBodyUnderlay"
MONTHS = {1: "янв.", 2: "фев.", 3: "март", 4: "апр.", 5: "май", 6: "июнь",
          7: "июль", 8: "авг.", 9: "сент.", 10: "окт.", 11: "нояб.", 12: "дек."}


class Scrapper:
    def __init__(self):
        # options = Options()
        # options.add_argument("--headless=new")
        edge_service = Service("msedgedriver.exe")
        self.driver = webdriver.Edge(service=edge_service)
        self.wait = WebDriverWait(self.driver, timeout=ELEMENT_VISIBILITY_TIMEOUT)

    def wait_visible_element(self, args: tuple, click=True):
        element = self.wait.until(ec.visibility_of_element_located(args))
        if click:
            element.click()
        return element

    def login(self, username, password):
        # if not self.check_cookies(): # TODO: add decent check of cookies file
        if "cookies.json" not in os.listdir("."):
            self.driver.get("%s/login" % FLOW_URL)
            print("Cookies...") # TODO: send this message to authentication window
            self.wait_visible_element((By.ID, COOKIE_DECLINE_BTN_CLASS))
            self.wait_visible_element((By.ID, "login"))

            print("Signing in...")
            self.wait.until(ec.visibility_of_element_located((By.NAME, "username"))).send_keys(username)
            self.wait.until(ec.visibility_of_element_located((By.NAME, "password"))).send_keys(password)
            self.wait_visible_element((By.ID, KEEP_SIGNED_IN_ID))
            self.driver.switch_to.active_element.send_keys(Keys.ENTER)

            if self.check_authentication():
                print("Logged in")
            else:
                print("Erorr: wrong email/password")
                return
            with open("cookies.json", "w") as cookies_file:
                json.dump(self.driver.get_cookies(), cookies_file)

        self.driver.get(FLOW_URL)
        self.load_cookies()

    def check_cookies(self):
        if "cookies.json" not in os.listdir("."):
            return False
        self.driver.get(FLOW_URL)
        self.load_cookies()
        self.driver.get(FLOW_URL + "/diary/training-list")
        time.sleep(2.5)
        if "login" in self.driver.current_url:
            os.remove("./cookies.json")
            return False
        return True

    def load_cookies(self):
        for cookie in json.load(open("cookies.json", "r")):
            self.driver.add_cookie(cookie)

    def check_authentication(self):
        return "bad_credentials" not in self.driver.current_url

    def get_all_trainings(self):
        pass

    def select_calendar_date(self, date: datetime, period_boundary: str):
        if period_boundary == "start":
            calendar_id = "historyStart"
        else:  # "end"
            calendar_id = "historyEnd"

        self.wait_visible_element((By.ID, calendar_id))
        self.wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, MONTHS_SWITCHER_CLASS)) == 1)
        self.wait_visible_element((By.CLASS_NAME, MONTHS_SWITCHER_CLASS))

        # year
        year = int(self.wait_visible_element((By.CLASS_NAME, YEARS_SWITCHER_CLASS), False).text)
        arrow_class = SWITCHER_LEFT_ARROW_CLASS
        if year < date.year:
            arrow_class = SWITCHER_RIGHT_ARROW_CLASS
        while not self.driver.find_elements(By.XPATH,f"//th[@class='picker-switch']/*[contains(text(), '{date.year}')]"):
            self.driver.find_element(By.CLASS_NAME, arrow_class).click()

        # month
        self.driver.find_element(By.XPATH, f"//*[contains(text(), '{MONTHS[date.month]}')]").click()

        # day
        self.driver.find_element(By.XPATH, f"//*[contains(text(), '{str(date.day).zfill(2)}')]").click()

    @staticmethod
    def get_dates_difference(start_date, end_date):
        diff = relativedelta(start_date, end_date)
        return diff.years, diff.months, diff.days

    @staticmethod
    def split_period(start_date, end_date):
        intervals = []
        start = start_date
        end = start_date + relativedelta(years=3)

        while end < end_date:
            intervals.append((start, end))
            start = end + relativedelta(days=1)
            end += relativedelta(years=3, days=1)
        intervals.append((start, end_date))
        return intervals

    def get_trainings_by_dates(self, start_date, end_date):
        self.driver.get(FLOW_URL + "/diary/training-list")
        self.wait_visible_element((By.CLASS_NAME, "trigger"))
        self.wait_visible_element((By.XPATH, "//*[contains(text(), 'Бег')]"))
        self.wait_visible_element((By.CLASS_NAME, "select-component__value-container.select-component__value-container--has-value.css-1hwfws3"))
        self.wait_visible_element((By.XPATH, "//*[contains(text(), 'Все')]"))

        intervals = split_period(start_date, end_date)
        for interval in intervals:
            print(f"Setting dates of the period {interval[0]} / {interval[1]}")
            self.select_calendar_date(interval[0], "start")
            self.select_calendar_date(interval[1], "end")
            time.sleep(2)

        # soup = BeautifulSoup(src, 'lxml')
        # ids = []
        # for div in soup.find_all("div", {"role": "listitem"}):
        #     div_class = div.attrs["class"]
        #     if ("row" in div_class) and (div.find("div", {"class": "data-column exercise-link"}).text == "Бег"):
        #         ids.append(div_class[-1][3:])
        # print(ids)
        # return ids

def export_exercise(driver, exercise_id, output_dir):
    def _load_cookies(session, cookies):
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

    s = requests.Session()
    _load_cookies(s, driver.get_cookies())

    r = s.get("%s/api/export/training/csv/%s" % (FLOW_URL, exercise_id))
    csv_data = r.text
    filename = f"{exercise_id}.csv"

    if not os.path.exists(output_dir):
        print(f"Creating directory {output_dir}...")
        os.makedirs(output_dir)

    outfile = open(os.path.join(output_dir, filename), 'w', encoding="UTF-8")
    outfile.write(csv_data)
    outfile.close()
    print("Writing file %s..." % filename)

# def run(driver, username, password, month, year, output_dir):
#     exercise_ids =  login(driver, username, password)
#     for ex_id in exercise_ids:
#         export_exercise(driver, ex_id, output_dir)

if __name__ == "__main__":
    username = polar_config.username
    password = polar_config.password

    scraper = Scrapper()
    scraper.login(username, password)
    start = datetime(year=2023, month=4, day=7)
    end = datetime(year=2025, month=1, day=11)
    scraper.get_trainings_by_dates(start, end)
