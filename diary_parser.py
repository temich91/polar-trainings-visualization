from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import polar_config
import time
import os

"""
Based on https://github.com/asib/polar-flow-export
"""

FLOW_URL = "https://flow.polar.com"

def login(driver, username, password):
    wait = WebDriverWait(driver, 10)

    driver.get("%s/login" % FLOW_URL)
    print("Cookies...")
    wait.until(ec.visibility_of_element_located((By.ID, "CybotCookiebotDialogBodyButtonDecline"))).click()
    wait.until(ec.visibility_of_element_located((By.ID, "login"))).click()

    print("Signing in...")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.switch_to.active_element.send_keys(Keys.ENTER)

    print("Logged in")
    driver.get("https://flow.polar.com/diary/training-list")

    # start date
    wait.until(ec.visibility_of_element_located((By.ID, "historyStart"))).click()
    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "picker-switch__link.picker-switch-days"))).click()
    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "picker-switch__link.picker-switch-months"))).click()
    wait.until(ec.visibility_of_all_elements_located((By.CLASS_NAME, "year")))[4].click()
    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "month"))).click()
    wait.until(ec.visibility_of_element_located((By.CLASS_NAME, "day.weekend.new"))).click()

    time.sleep(2)
    src = driver.page_source
    with open("test.html", "w", encoding="UTF-8") as file:
        file.write(src)

    soup = BeautifulSoup(src, 'lxml')
    ids = []
    for div in soup.find_all("div", {"role": "listitem"}):
        div_class = div.attrs["class"]
        if ("row" in div_class) and (div.find("div", {"class": "data-column exercise-link"}).text == "Бег"):
            ids.append(div_class[-1][3:])
    print(ids)
    return ids

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

def run(driver, username, password, month, year, output_dir):
    exercise_ids =  login(driver, username, password)
    for ex_id in exercise_ids:
        export_exercise(driver, ex_id, output_dir)

if __name__ == "__main__":
    username = polar_config.username
    password = polar_config.password
    month = 4
    year = 2025
    output_dir = "csv_output"

    options = Options()
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    try:
        run(driver, username, password, month, year, output_dir)
    finally:
        driver.quit()
