from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import json
import time
import datetime
import pytz
import os

print("imports ok")

USER = os.environ['USER'] #CAS
PASS = os.environ['PASS'] #CAS
URL = os.environ['URL'] #jsonbin
API_KEY = os.environ['API_KEY'] #jsonbin

places = [40, 42, 46, 43, 44, 46, 46, 42]

tz = pytz.timezone('Europe/Paris')

firefox_options = Options()
# firefox_options.add_argument("-headless")

driver = webdriver.Firefox(options=firefox_options)

print("driver created")

driver.get("https://evento.renater.fr/survey/fc-ventilation-dans-les-p2i-etape-2-vjoqpyve")

menu = driver.find_element(By.CLASS_NAME, "select2-selection--single")
menu.click()
search = driver.find_element(By.CLASS_NAME, "select2-search__field")
search.send_keys("INSA Lyon")

print("school selected")

wait = WebDriverWait(driver, 10)
time.sleep(2)

search.send_keys(Keys.ENTER)

wait = WebDriverWait(driver, 10)
time.sleep(2)

submit = driver.find_element(By.NAME, "Select")
submit.submit()

print("submitted renater form")

WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
time.sleep(1)

username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password")

username.send_keys(USER)
password.send_keys(PASS)


wait = WebDriverWait(driver, 10)
time.sleep(3)

password.submit()

print("authenticated with CAS")

WebDriverWait(driver, 10).until(EC.url_changes(driver.current_url))
time.sleep(1)

print("survey launched")
try:
    cookie_banner = driver.find_element(By.XPATH, '/html/body/section')
    
    print("cookie banner found")
    driver.execute_script("""
    var element = arguments[0];
    element.parentNode.removeChild(element);
    """, cookie_banner)
    print("cookie banner deleted")
except:
    pass

wait = WebDriverWait(driver, 10)

try:
    answers_switch = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/main/section/div[2]/label")))
    answers_switch.click()
    print("switch clicked")
except Exception as e:
    print(f"Error clicking on switch: {e}")
    raise e

wait = WebDriverWait(driver, 10)
time.sleep(1)

driver.execute_script("window.scrollTo(0,document.body.scrollHeight)")

wait = WebDriverWait(driver, 10)
time.sleep(1)

answers = driver.find_elements(By.CLASS_NAME, "sum_row")[1]

print("answers found")

timestamp = datetime.datetime.now(tz).strftime("%d/%m/%Y-%H:%M:%S")

dic = {timestamp: {}}
i = 1
for el in answers.find_elements(By.TAG_NAME, "td") :
    dic[timestamp][i] = {"votes": int(el.text), "pourcentage": float(el.get_attribute("title").split(" : ")[1][:-1]), "dispo": places[i-1] - int(el.text), "total": places[i-1]}
    i += 1

driver.close()
print("driver closed")

old = requests.get(URL, headers={"authorization": f"token {API_KEY}"}).json()

new = {**old, **dic}
r = requests.post(URL, data = json.dumps(new), headers={"authorization": f"token {API_KEY}"})
print(r.status_code)
