# -*- coding: utf-8 -*-
"""
Created on Fri Dec  1 22:30:32 2023

@author: Alois
"""

from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import datetime
import requests
import json
import os

USER = os.environ['USER'] #mondossierweb
PASS = os.environ['PASS'] #mondossierweb
URL = os.environ['URL'] #jsonbin
API_KEY = os.environ['API_KEY'] #jsonbin

places = [40, 42, 46, 43, 44, 46, 46, 42]

firefox_options = Options()
firefox_options.add_argument("-headless")

driver = webdriver.Firefox(options=firefox_options)

driver.get("https://discovery.renater.fr/edugain/WAYF?cru=yes&entityID=https%3A%2F%2Fevento.renater.fr%2F&return=https%3A%2F%2Fevento.renater.fr%2FShibboleth.sso%2FLogin%3FSAMLDS%3D1%26target%3Dss%253Amem%253Aed9904aecaee9f03359fd3b125f2fdb804586bb82705130d2733235b63904d6e")

menu = driver.find_element(By.CLASS_NAME, "select2-selection--single")
menu.click()
search = driver.find_element(By.CLASS_NAME, "select2-search__field")
search.send_keys("INSA Lyon")

time.sleep(1)

search.send_keys(Keys.ENTER)

time.sleep(1)

submit = driver.find_element(By.NAME, "Select")
submit.submit()

time.sleep(1)

driver.get("https://login.insa-lyon.fr/cas/login?service=https%3A%2F%2Flogin.insa-lyon.fr%2Fidp%2FAuthn%2FExtCas%3Fconversation%3De1s1&entityId=https%3A%2F%2Fevento.renater.fr%2F")

time.sleep(1)

username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")

username.send_keys(USER)
password.send_keys(PASS)


time.sleep(1)

password.submit()

time.sleep(1)

driver.get("https://evento.renater.fr/survey/fc-ventilation-dans-les-p2i-etape-1-id32ibkl")

cookie_banner = driver.find_element(By.CSS_SELECTOR, 'section[data-template-content="banner_cookie_container"]')
driver.execute_script("""
var element = arguments[0];
element.parentNode.removeChild(element);
""", cookie_banner)

answers_switch = driver.find_elements(By.CLASS_NAME, "switch-container")[0]
answers_switch.click()

time.sleep(2)

answers = driver.find_elements(By.CLASS_NAME, "sum_row")[1]

dic = {datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S"): {}}
i = 1
for el in answers.find_elements(By.TAG_NAME, "td") :
    dic[datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")][i] = {"total": el.text, "pourcentage": float(el.get_attribute("title").split(" : ")[1][:-1])}
    i += 1

old = requests.get(URL, headers={"authorization": f"token {API_KEY}"}).json()

new = {**old, **dic}
requests.post(URL, data = json.dumps(new), headers={"authorization": f"token {API_KEY}"})
