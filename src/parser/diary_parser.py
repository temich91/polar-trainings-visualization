from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.remote.webdriver import WebElement
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
from src.utils import constants as c
from src.utils.paths import *

COOKIES_PATH = DATA_DIR / "cookies.json"

def get_xpath_by_text(text: str | int | float, prefix="/") -> str:
    """Return the XPath to element containing specific text.

    XPath tags of previous nodes can be added as prefix.
    By default, path to any element with given text is defined.

    Args:
        text: Text of the element to make the path to.
        prefix: XPath nodes preceding the text node.

    Returns:
        XPath string.
    """
    return f"{prefix}/*[contains(text(), '{text}')]"

class Scrapper:
    """Polar Flow running sessions scrapper.

    Login to Polar Flow account, parse IDs of running sessions from training history page
    and download all csv to specified folder.
    Local webdriver is used.
    Cookies are saved in ``cookies.json`` at first entry and are uploaded to webdriver for repeated requests.
    """
    def __init__(self, driver_path):
        # uncomment to disable browser window
        # options = Options()
        # options.add_argument("--headless=new")
        edge_service = Service(driver_path)
        self.driver = webdriver.Edge(service=edge_service)
        self.wait = WebDriverWait(self.driver, timeout=c.ELEMENT_VISIBILITY_TIMEOUT)

    def wait_visible_element(self, locator: tuple[str, str], click: bool=True) -> WebElement:
        """Alias for WebDriverWait.until method.

        Args:
            locator: Used to find the element on page.
            click: If True, found element is clicked.

        Returns:
            WebElement if it is located and visible.
        """
        element = self.wait.until(ec.visibility_of_element_located(locator))
        if click:
            element.click()
        return element

    def login(self, username: str, password: str) -> None:
        """Log in to Polar Flow.

        Tries to upload cookies to avoid logging in again.
        If there is no ``cookies.json`` in the data directory or the cookies are outdated, a new json will be saved.

        Args:
            username: Polar Flow login.
            password: Polar Flow password.

        Returns:
            None.
        """
        if not self.check_cookies():
            self.driver.get(f"{c.FLOW_URL}/login")
            print("Cookies...")
            # If the cookies json is not in the data directory
            # unnecessary cookies decline menu will be transmitted to the website, so the cookies menu will appear.

            # if "cookies.json" not in os.listdir(c.COOKIES_DIR):
            #     self.wait_visible_element((By.ID, c.COOKIE_DECLINE_BTN_CLASS))
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
            with open(COOKIES_PATH, "w") as cookies_file:
                json.dump(self.driver.get_cookies(), cookies_file)

        self.load_cookies()

    def check_cookies(self) -> bool:
        """Check if `cookies.json` file exists and is up to date.

        If cookies file exists tries to log in.
        If successful, cookies are valid.

        Returns:
            Bool of check result.
        """
        if "cookies.json" not in os.listdir(DATA_DIR):
            return False
        self.driver.get(c.FLOW_URL)
        self.load_cookies()
        self.driver.get(f"{c.FLOW_URL}/diary/training-list")
        time.sleep(2.5)
        if "login" in self.driver.current_url:
            os.remove(COOKIES_PATH)
            return False
        return True

    def load_cookies(self) -> None:
        """Upload cookies from local json into current webdriver session.

        Existing cookies with the same name will be overwritten.

        Returns:
            None.
        """
        for cookie in json.load(open(COOKIES_PATH, "r")):
            self.driver.add_cookie(cookie)

    def check_authentication(self) -> bool:
        """Check if the username and password on the authorization page are suitable.

        Returns:
            Bool of check result.
        """
        return "bad_credentials" not in self.driver.current_url

    def select_calendar_date(self, date: datetime, period_boundary: str) -> None:
        """Select specific date in the calendar at trainings history page.

        Args:
            date: Datetime object for selecting the date.
            period_boundary: Beginning or end date of the period being selected.

        Returns:
            None.
        """
        calendar_id = f"history{period_boundary.capitalize()}"

        self.wait_visible_element((By.ID, calendar_id))
        self.wait.until(lambda driver: len(driver.find_elements(By.CLASS_NAME, c.MONTHS_SWITCHER_CLASS)) == 1)
        self.wait_visible_element((By.CLASS_NAME, c.MONTHS_SWITCHER_CLASS))

        # year
        year = int(self.wait_visible_element((By.CLASS_NAME, c.YEARS_SWITCHER_CLASS), False).text)
        arrow_class = c.SWITCHER_LEFT_ARROW_CLASS
        if year < date.year:
            arrow_class = c.SWITCHER_RIGHT_ARROW_CLASS
        while not self.driver.find_elements(By.XPATH,
                                            get_xpath_by_text(date.year, prefix="//th[@class='picker-switch']")):
            self.driver.find_element(By.CLASS_NAME, arrow_class).click()

        # month
        self.driver.find_element(By.XPATH, get_xpath_by_text(c.MONTHS[date.month])).click()

        # day
        day = str(date.day).zfill(2)
        self.driver.find_element(By.XPATH, get_xpath_by_text(day)).click()

    def get_trainings_ids(self) -> list[str]:
        """Collect Polar Flow IDs of sessions.

        Checks if there is data on the page, then parses ids from html classes of session record row.

        Returns:
            List of parsed ids of running sessions.
        """
        try:
            self.wait_visible_element((By.XPATH, get_xpath_by_text('Дата')), False)
        except TimeoutException:
            self.wait_visible_element((By.XPATH, get_xpath_by_text('Нет данных')), False)
            return []

        src = self.driver.page_source

        soup = BeautifulSoup(src, 'lxml')
        ids = []
        for div in soup.find_all("div", {"role": "listitem"}):
            div_class = div.attrs["class"]  # format: row history-list__row history-list id-0000000000
            if "row" in div_class:
                id_ = div_class[-1][3:]
                ids.append(id_)
        return ids

    def export_csv(self, output_dir: str, session_ids: list[str]) -> None:
        """Download csv of sessions by their ids.

        Args:
            output_dir: Name of the directory to save csv of sessions in.
            session_ids: List of Polar Flow IDs of sessions to export.

        Returns:
            None
        """
        output_path = f"./{output_dir}"
        if not os.path.exists(output_path):
            os.mkdir(output_path)

        for id_ in session_ids:
            session = requests.Session()
            # Load cookies to be logged in to website during requests session
            for cookie in self.driver.get_cookies():
                session.cookies.set(cookie['name'], cookie['value'])

            csv = session.get(f"{c.FLOW_URL}/api/export/training/csv/{id_}").text
            filename = f"{id_}.csv"
            print("Writing file %s..." % filename)
            with open(os.path.join(output_dir, filename), 'w', encoding="UTF-8") as output:
                output.write(csv)

    def check_running_in_list(self) -> bool:
        """Check if running is in the sports list at trainings history page.

        Looks for running in sports dropout.

        Returns:
            Bool of check result.
        """
        self.wait_visible_element((By.CLASS_NAME, "trigger"))
        try:
            self.wait_visible_element((By.XPATH, get_xpath_by_text('Бег')))
        except (TimeoutException, StaleElementReferenceException):
            return False
        self.driver.find_element(By.TAG_NAME, "body").click()
        return True

    def get_all_trainings(self, output_dir="csv_export") -> None:
        """Download csv of all sessions that are in the account to specific directory.

        Collects all trainings from training history page.
        Since maximal range of period is 3 years, webdriver switches dates in the calendar by 3 years.

        Args:
            output_dir: Name of directory to download files to.

        Returns:
            None.
        """
        self.driver.get(f"{c.FLOW_URL}/diary/training-list")
        self.wait_visible_element((By.CLASS_NAME, c.PERIOD_SWITCHER_CLASS))
        self.wait_visible_element((By.XPATH, get_xpath_by_text('Все')))

        today = datetime.now()
        current_year = today.year
        period_length = current_year - c.FIRST_YEAR

        # initial date in start calendar
        left_bound = today - relativedelta(years=3)
        self.select_calendar_date(left_bound, "start")
        # loop does period length + 3 iterations in case it is not divisible by 3
        # and we need to display maximum 3 more years
        for i in range(period_length // 3 + 1):
            running_in_list = self.check_running_in_list()
            if running_in_list:
                session_ids = self.get_trainings_ids()
                self.export_csv(output_dir, session_ids)
            # switch dates with arrow button (website switches dates by 3 years automatically)
            self.driver.find_element(By.CLASS_NAME, c.PREVIOUS_DATE_ARROW_CLASS).click()


if __name__ == "__main__":
    username = polar_config.username
    password = polar_config.password
    webdriver_path = BASE_DIR / "msedgedriver.exe"

    scraper = Scrapper(webdriver_path)
    scraper.login(username, password)
    scraper.get_all_trainings()
