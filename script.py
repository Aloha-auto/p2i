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
from PIL import Image

USER = os.environ['USER'] #mondossierweb
PASS = os.environ['PASS'] #mondossierweb
URL = os.environ['URL'] #jsonbin
API_KEY = os.environ['API_KEY'] #jsonbin
IMGBB_API_KEY = os.environ['IMGBB_API_KEY'] #ImgBB

places = [40, 42, 46, 43, 44, 46, 46, 42]

# Fonction pour prendre une capture d'écran
def save_screenshot(driver, filename):
    driver.save_screenshot(filename)
    im = Image.open(filename)
    im.show()  # Ouvre la capture d'écran (commentez cette ligne si vous ne voulez pas que la capture d'écran s'affiche)
    return filename

# Fonction pour envoyer une capture d'écran à imgbb.com
def upload_to_imgbb(api_key, image_path):
    url = "https://api.imgbb.com/1/upload"
    with open(image_path, "rb") as file:
        files = {"image": file}
        payload = {"key": api_key}
        response = requests.post(url, files=files, data=payload)
        return response.json()["data"]["url"]

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
screenshot_path_before = save_screenshot(driver, "screenshot_before_switch.png")
imgbb_url_after = upload_to_imgbb(IMGBB_API_KEY, screenshot_path_before)
print(f"Screenshot before switch uploaded to imgbb.com: {imgbb_url_after}")

###

try:
    answers_switch = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/main/section/div[2]/label")))
    answers_switch.click()
except Exception as e:
    print(f"Error clicking on switch: {e}")
    screenshot_path = save_screenshot(driver, "screenshot_error.png")
    imgbb_url = upload_to_imgbb(IMGBB_API_KEY, screenshot_path)
    print(f"Screenshot uploaded to imgbb.com: {imgbb_url}")
    # Ajoutez d'autres informations de débogage si nécessaire
    raise e

wait = WebDriverWait(driver, 10)

###
screenshot_path_after = save_screenshot(driver, "screenshot_after_switch.png")
imgbb_url_after = upload_to_imgbb(IMGBB_API_KEY, screenshot_path_after)
print(f"Screenshot after switch uploaded to imgbb.com: {imgbb_url_after}")
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
