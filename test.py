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

print("imports ok")

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

print("driver created")

driver.get("https://discovery.renater.fr/edugain/WAYF?cru=yes&entityID=https%3A%2F%2Fevento.renater.fr%2F&return=https%3A%2F%2Fevento.renater.fr%2FShibboleth.sso%2FLogin%3FSAMLDS%3D1%26target%3Dss%253Amem%253Aed9904aecaee9f03359fd3b125f2fdb804586bb82705130d2733235b63904d6e")

menu = driver.find_element(By.CLASS_NAME, "select2-selection--single")
menu.click()
search = driver.find_element(By.CLASS_NAME, "select2-search__field")
search.send_keys("INSA Lyon")

print("school selected")
