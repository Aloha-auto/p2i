from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import datetime
import requests
import json
import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

USER = os.environ['USER'] #mondossierweb
PASS = os.environ['PASS'] #mondossierweb
URL = os.environ['URL'] #jsonbin
API_KEY = os.environ['API_KEY'] #jsonbin

places = [40, 42, 46, 43, 44, 46, 46, 42]

firefox_options = Options()
# firefox_options.add_argument("-headless")

driver = webdriver.Firefox(options=firefox_options)

driver.get("https://discovery.renater.fr/edugain/WAYF?cru=yes&entityID=https%3A%2F%2Fevento.renater.fr%2F&return=https%3A%2F%2Fevento.renater.fr%2FShibboleth.sso%2FLogin%3FSAMLDS%3D1%26target%3Dss%253Amem%253Aed9904aecaee9f03359fd3b125f2fdb804586bb82705130d2733235b63904d6e")

menu = driver.find_element(By.CLASS_NAME, "select2-selection--single")
menu.click()
search = driver.find_element(By.CLASS_NAME, "select2-search__field")
search.send_keys("INSA Lyon")

wait = WebDriverWait(driver, 10)
time.sleep(2)

search.send_keys(Keys.ENTER)
# switch656a6cda3d7b1

wait = WebDriverWait(driver, 10)
time.sleep(2)

submit = driver.find_element(By.NAME, "Select")
submit.submit()

wait = WebDriverWait(driver, 10)
time.sleep(2)

driver.get("https://login.insa-lyon.fr/cas/login?service=https%3A%2F%2Flogin.insa-lyon.fr%2Fidp%2FAuthn%2FExtCas%3Fconversation%3De1s1&entityId=https%3A%2F%2Fevento.renater.fr%2F")

wait = WebDriverWait(driver, 10)

username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")

username.send_keys(USER)
password.send_keys(PASS)


wait = WebDriverWait(driver, 10)
time.sleep(4)

password.submit()

wait = WebDriverWait(driver, 10)
time.sleep(1)

driver.get("https://evento.renater.fr/survey/fc-ventilation-dans-les-p2i-etape-1-id32ibkl")


try:
    cookie_banner = driver.find_element(By.CSS_SELECTOR, 'section[data-template-content="banner_cookie_container"]')
    driver.execute_script("""
    var element = arguments[0];
    element.parentNode.removeChild(element);
    """, cookie_banner)
except:
    pass

###
driver.save_screenshot("screenshot_before_switch.png")
###

try:
    # Utilisez une attente explicite pour s'assurer que l'élément est présent
    answers_switch = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "switch-container")))
    answers_switch.click()
except Exception as e:
    print(f"Error clicking on switch: {e}")
    driver.save_screenshot("screenshot_error.png")
    # Ajoutez d'autres informations de débogage si nécessaire
    raise e

wait = WebDriverWait(driver, 10)

###
driver.save_screenshot("screenshot_after_switch.png")
###

answers = driver.find_elements(By.CLASS_NAME, "sum_row")[1]

timestamp = datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")

dic = {timestamp: {}}
i = 1
for el in answers.find_elements(By.TAG_NAME, "td") :
    dic[timestamp][i] = {"votes": int(el.text), "pourcentage": float(el.get_attribute("title").split(" : ")[1][:-1]), "dispo": max(places[i-1] - int(el.text), 0), "total": places[i-1]}
    i += 1

old = requests.get(URL, headers={"authorization": f"token {API_KEY}"}).json()

new = {**old, **dic}
requests.post(URL, data = json.dumps(new), headers={"authorization": f"token {API_KEY}"})
