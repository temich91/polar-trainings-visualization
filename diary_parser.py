from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import polar_config
import time
import sys
import os

FLOW_URL = "https://flow.polar.com"

def login(driver, username, password):
    driver.get("%s/login" % FLOW_URL)
    time.sleep(1.5)
    print("Cookies...")
    driver.find_element(By.ID, "CybotCookiebotDialogBodyButtonDecline").click()
    driver.find_element(By.ID, "login").click()
    time.sleep(5)
    print("Signing in...")
    driver.find_element(By.NAME, "username").send_keys(username)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.switch_to.active_element.send_keys(Keys.ENTER)
    print("Logged in")

def get_exercise_ids(driver, year, month):
    driver.get("https://flow.polar.com/diary/training-list")
    time.sleep(3.5)
    src = driver.page_source
    with open("test.html", "w", encoding="UTF-8") as file:
        file.write(src)

    soup = BeautifulSoup(src, 'lxml')
    ids = []
    for div in soup.find_all("div", {"role": "listitem"}):
        div_class = div.attrs["class"]
        if "row" in div_class:
            ids.append(div_class[-1][3:])

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
    login(driver, username, password)
    time.sleep(3)
    exercise_ids = get_exercise_ids(driver, year, month)
    for ex_id in exercise_ids:
        export_exercise(driver, ex_id, output_dir)

if __name__ == "__main__":
    username = polar_config.username
    password = polar_config.password
    month = 4
    year = 2025
    output_dir = "output"

    options = Options()
    # options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    try:
        run(driver, username, password, month, year, output_dir)
    finally:
        driver.quit()
