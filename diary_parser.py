from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from bs4 import BeautifulSoup
import json
import requests
import polar_config
import time
import os
from datetime import datetime
from dateutil.relativedelta import relativedelta
import constants as c


def get_xpath_by_text(text, prefix="/"):
    return f"{prefix}/*[contains(text(), '{text}')]"

class Scrapper:
    def __init__(self):
        # uncomment to disable browser window
        # options = Options()
        # options.add_argument("--headless=new")
        edge_service = Service(c.DRIVER_FILENAME)
        self.driver = webdriver.Edge(service=edge_service)
        self.wait = WebDriverWait(self.driver, timeout=c.ELEMENT_VISIBILITY_TIMEOUT)

    def wait_visible_element(self, args: tuple, click=True):
        element = self.wait.until(ec.visibility_of_element_located(args))
        if click:
            element.click()
        return element

    def login(self, username, password):
        # if not self.check_cookies(): # TODO: add decent check of cookies file
        if "cookies.json" not in os.listdir("."):
            self.driver.get(f"{c.FLOW_URL}/login")
            print("Cookies...") # TODO: send this message to authentication window
            self.wait_visible_element((By.ID, c.COOKIE_DECLINE_BTN_CLASS))
            self.wait_visible_element((By.ID, "login"))

            print("Signing in...")
            self.wait.until(ec.visibility_of_element_located((By.NAME, "username"))).send_keys(username)
            self.wait.until(ec.visibility_of_element_located((By.NAME, "password"))).send_keys(password)
            self.wait_visible_element((By.ID, c.KEEP_SIGNED_IN_ID))
            self.driver.switch_to.active_element.send_keys(Keys.ENTER)

            if self.check_authentication():
                print("Logged in")
            else:
                print("Erorr: wrong email/password")
                return
            with open("cookies.json", "w") as cookies_file:
                json.dump(self.driver.get_cookies(), cookies_file)

        self.driver.get(c.FLOW_URL)
        self.load_cookies()

    def check_cookies(self):
        if "cookies.json" not in os.listdir("."):
            return False
        self.driver.get(c.FLOW_URL)
        self.load_cookies()
        self.driver.get(f"{c.FLOW_URL}/diary/training-list")
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

    def select_calendar_date(self, date: datetime, period_boundary: str):
        if period_boundary == "start":
            calendar_id = "historyStart"
        else:  # "end"
            calendar_id = "historyEnd"

        self.wait_visible_element((By.ID, calendar_id))
        self.wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, c.MONTHS_SWITCHER_CLASS)) == 1)
        self.wait_visible_element((By.CLASS_NAME, c.MONTHS_SWITCHER_CLASS))

        # year
        year = int(self.wait_visible_element((By.CLASS_NAME, c.YEARS_SWITCHER_CLASS), False).text)
        arrow_class = c.SWITCHER_LEFT_ARROW_CLASS
        if year < date.year:
            arrow_class = c.SWITCHER_RIGHT_ARROW_CLASS
        while not self.driver.find_elements(By.XPATH, get_xpath_by_text(date.year, prefix="//th[@class='picker-switch']")):
            self.driver.find_element(By.CLASS_NAME, arrow_class).click()

        # month
        self.driver.find_element(By.XPATH, get_xpath_by_text(c.MONTHS[date.month])).click()

        # day
        self.driver.find_element(By.XPATH, get_xpath_by_text(str(date.day).zfill(2))).click()

    def get_trainings_ids(self):
        try:
            self.wait_visible_element((By.XPATH, get_xpath_by_text('Дата')), False)
        except TimeoutException:
            self.wait_visible_element((By.XPATH, get_xpath_by_text('Нет данных')), False)
            return []

        src = self.driver.page_source

        soup = BeautifulSoup(src, 'lxml')
        ids = []
        for div in soup.find_all("div", {"role": "listitem"}):
            div_class = div.attrs["class"]
            if "row" in div_class:
                ids.append(div_class[-1][3:])
        print("ids len:", len(ids))
        return ids

    def export_csv(self, output_dir):
        output_path = f"./{output_dir}"
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        trainings_ids = self.get_trainings_ids()

        for id_ in trainings_ids:
            session = requests.Session()
            for cookie in self.driver.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])
            csv = session.get(f"{c.FLOW_URL}/api/export/training/csv/{id_}").text
            filename = f"{id_}.csv"

            print("Writing file %s..." % filename)
            with open(os.path.join(output_dir, filename), 'w', encoding="UTF-8") as output:
                output.write(csv)

    def check_running(self):
        self.wait_visible_element((By.CLASS_NAME, "trigger"))
        try:
            self.wait_visible_element((By.XPATH, get_xpath_by_text('Бег')))
        except (TimeoutException, StaleElementReferenceException):
            return False
        self.driver.find_element(By.TAG_NAME, "body").click()
        return True

    def get_all_trainings(self):
        self.driver.get(f"{c.FLOW_URL}/diary/training-list")
        self.wait_visible_element((By.CLASS_NAME, c.PERIOD_SWITCHER_CLASS))
        self.wait_visible_element((By.XPATH, get_xpath_by_text('Бег')))

        today = datetime.now()
        current_year = today.year
        period_length = current_year - c.FIRST_YEAR

        left_bound = today - relativedelta(years=3)
        self.select_calendar_date(left_bound, "start")
        for i in range(period_length // 3 + 3):
            running_in_list = self.check_running()
            if running_in_list:
                self.export_csv("test_csv_export")
            self.driver.find_element(By.CLASS_NAME, c.PREVIOUS_DATE_ARROW_CLASS).click()


if __name__ == "__main__":
    username = polar_config.username
    password = polar_config.password

    scraper = Scrapper()
    scraper.login(username, password)
    scraper.get_all_trainings()
