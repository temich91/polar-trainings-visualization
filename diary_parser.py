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

"""
TODO:
    - Other languages localization (file with words parser looks for on pages)
    - Constants in separate file
    - Decent check of cookies file
    - Send progress messages to GUI
    - Load user data from db
"""

FLOW_URL = "https://flow.polar.com"
ELEMENT_VISIBILITY_TIMEOUT = 10
COOKIE_DECLINE_BTN_CLASS = "CybotCookiebotDialogBodyButtonDecline"
START_DATE_CALENDAR_ID = "historyStart"
END_DATE_CALENDAR_ID = "historyEnd"
MONTHS_SWITCHER_CLASS = "picker-switch__link.picker-switch-days"
YEARS_SWITCHER_CLASS = "picker-switch__link.picker-switch-months"
SWITCHER_LEFT_ARROW_CLASS = "icon.icon-arrow-left.picker-previous-button"
MONTHS = {1: "янв.", 2: "фев.", 3: "март", 4: "апр.", 5: "май", 6: "июнь",
          7: "июль", 8: "авг.", 9: "сент.", 10: "окт.", 11: "нояб.", 12: "дек."}


class Scrapper:
    def __init__(self):
        # options = Options()
        # options.add_argument("--headless=new")
        edge_service = Service("msedgedriver.exe")
        self.driver = webdriver.Edge(service=edge_service)
        self.wait = WebDriverWait(self.driver, timeout=ELEMENT_VISIBILITY_TIMEOUT)


    def login(self, username, password):
        if "cookies.json" not in os.listdir("."): # TODO: add decent check of cookies file
            self.driver.get("%s/login" % FLOW_URL)
            print("Cookies...") # TODO: send this message to authentication window
            self.wait.until(ec.visibility_of_element_located((By.ID, COOKIE_DECLINE_BTN_CLASS))).click()
            self.wait.until(ec.visibility_of_element_located((By.ID, "login"))).click()

            print("Signing in...")
            self.wait.until(ec.visibility_of_element_located((By.NAME, "username"))).send_keys(username)
            self.wait.until(ec.visibility_of_element_located((By.NAME, "password"))).send_keys(password)
            self.driver.switch_to.active_element.send_keys(Keys.ENTER)

            if self.check_authentication():
                print("Logged in")
            else:
                print("Erorr: wrong email/password")
                return
            with open("cookies.json", "w") as cookies_file:
                json.dump(self.driver.get_cookies(), cookies_file)

        self.driver.get("https://flow.polar.com/diary/training-list")
        self.load_cookies()

    def load_cookies(self):
        for cookie in json.load(open("cookies.json", "r")):
            self.driver.add_cookie(cookie)

    def check_authentication(self):
        return "bad_credentials" not in self.driver.current_url

    def get_all_trainings(self):
        pass

    def get_trainings_by_dates(self, start_date: datetime, end_date: datetime):
        print("Setting the start date of the period")
        self.driver.get("https://flow.polar.com/diary/training-list")
        self.wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "trigger"))).click()
        self.wait.until(ec.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Бег')]"))).click()
        self.wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "select-component__value-container.select-component__value-container--has-value.css-1hwfws3"))).click()
        self.wait.until(ec.visibility_of_element_located((By.XPATH, "//*[contains(text(), 'Все')]"))).click()

        # start date
        start_year = start_date.year
        start_month = start_date.month
        start_day = start_date.day
        self.wait.until(ec.visibility_of_element_located((By.ID, START_DATE_CALENDAR_ID))).click()
        self.wait.until(ec.visibility_of_element_located((By.CLASS_NAME, MONTHS_SWITCHER_CLASS))).click()

        # year
        self.wait.until(ec.visibility_of_element_located((By.XPATH, f"//*[contains(text(), '{datetime.today().year}')]")))
        while not self.driver.find_elements(By.XPATH, f"//th[@class='picker-switch']/*[contains(text(), '{start_year}')]"):
            self.driver.find_element(By.CLASS_NAME, SWITCHER_LEFT_ARROW_CLASS).click()

        # month
        self.driver.find_element(By.XPATH, f"//*[contains(text(), '{MONTHS[start_month]}')]").click()

        # day
        self.driver.find_element(By.XPATH, f"//*[contains(text(), '{str(start_day).zfill(2)}')]").click()

        # self.wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, "year")))[4].click()
        # self.wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "month"))).click()
        # self.wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "day.weekend.new"))).click()

        # src = self.driver.page_source
        # with open("test.html", "w", encoding="UTF-8") as file:
        #     file.write(src)

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
    start = datetime(year=2024, month=6, day=1)
    end = datetime(year=2024, month=6, day=7)
    scraper.get_trainings_by_dates(start, end)
