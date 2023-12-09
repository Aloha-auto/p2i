# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 13:56:22 2023

@author: Alois
"""
import requests
import json
import time
import datetime
import pytz
import os
import itertools
import ftplib
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


USER = os.environ['USER'] #mondossierweb
PASS = os.environ['PASS'] #mondossierweb
URL = os.environ['URL'] #jsonbin
FTP_HOST = os.environ['FTP_HOST'] #ftp
FTP_USER = os.environ['FTP_USER'] #ftp
FTP_PASS = os.environ['FTP_PASS'] #ftp

tz = pytz.timezone('Europe/Paris')


def detecte_p2i(line, dic, timestamp):
    liste = line.split(",")
    nom = liste[0]
    p2i = liste.index("1")
    dic[timestamp][p2i].append(nom)
    dic[timestamp]["names"][nom] = p2i
    return p2i

def get_cookie():    
    firefox_options = Options()
    # firefox_options.add_argument("-headless")

    driver = webdriver.Firefox(options=firefox_options)
    
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
    
    cookies = driver.get_cookies()
    selenium_user_agent = driver.execute_script("return navigator.userAgent;")
    
    driver.close()

    return cookies, selenium_user_agent


def main():
    cookies,selenium_user_agent = get_cookie()
    with requests.Session() as s:
        for cookie in cookies:
            s.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        s.headers.update({"user-agent": selenium_user_agent})
        csv_file = s.get('https://evento.renater.fr/rest.php/survey/vjoqpyve/results?format=download:csv&tz=').text
        result = s.get('https://evento.renater.fr/survey/fc-ventilation-dans-les-p2i-etape-2-vjoqpyve')
        
        html = result.text
    
    # connect to the FTP server
    ftp = ftplib.FTP(FTP_HOST, FTP_USER, FTP_PASS)
    # force UTF-8 encoding
    ftp.encoding = "utf-8"

    ftp.sendcmd('CWD htdocs/p2i/')
    
    content = csv_file.split("\n")
    rows = content[1:-1]
    total = content[-1]
    
    timestamp = datetime.datetime.now(tz).strftime("%d/%m/%Y-%H:%M:%S")
    
    d = {timestamp: {"p2i": {}, "names": {}, 1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], "total": {1: 27, 2: 42, 3: 46, 4: 43, 5: 44, 6: 46, 7: 46, 8: 42}}}
    
    for row in rows:
        detecte_p2i(row, d, timestamp)
        
    for i, el in enumerate(total.split(",")[1::]):
            d[timestamp]["p2i"][i+1] = int(el)

    
    filename = "data.json"
    with open(filename, "wb") as file:
        # use FTP's RETR command to download the file
        ftp.retrbinary(f"RETR {filename}", file.write)

    with open(filename, 'r') as f :
        old = json.load(f)
        
    new = {**old, **d}

    with open(filename, 'w') as f :
        json.dump(new, f)


    with open(filename, "rb") as file:
        # use FTP's STOR command to upload the file
        ftp.storbinary(f"STOR {filename}", file)
    
    print("file uploaded")
    return html

html = main()
# print(html)
