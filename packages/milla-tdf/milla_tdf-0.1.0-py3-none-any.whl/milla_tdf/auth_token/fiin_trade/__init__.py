from genericpath import isfile
import json
import logging
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
from urllib.parse import urlparse
from urllib.parse import parse_qs
import os.path
from pathlib import Path
import requests
from milla_tdf.config import TradingFrameWorkConfig
from sys import platform
from urllib import request
import zipfile


class FiinAuthToken():
    def check_driver_and_download():
        CHROME_DRIVER_PATH = TradingFrameWorkConfig.selenium_driver_path

        if(isfile(CHROME_DRIVER_PATH) == True or isfile(f'{CHROME_DRIVER_PATH}.exe') == True):
            return

        #create directory
        driver_path = os.path.normpath(CHROME_DRIVER_PATH + os.sep + os.pardir)
        Path(driver_path).mkdir(parents=True, exist_ok=True)

        mapping_file = {
            'win32' : 'chromedriver_win32.zip',
            'darwin' : 'chromedriver_mac64_m1.zip'
        }
        file = mapping_file[platform]

        logging.info(f'downloading {TradingFrameWorkConfig.selenium_download_url}/{file}')

        request.urlretrieve(f'''{TradingFrameWorkConfig.selenium_download_url}/{file}''', f"{driver_path}/{file}")

        with zipfile.ZipFile(f"{driver_path}/{file}", 'r') as zip_ref:
            zip_ref.extractall(f"{driver_path}")


    def get_token_by_selenium() -> str:

        FiinAuthToken.check_driver_and_download()

        logging.info('Auth with fiin trade ....')
        CHROME_DRIVER_PATH = TradingFrameWorkConfig.selenium_driver_path
        USERNAME=TradingFrameWorkConfig.fiin_trade_username
        PASSWORD=TradingFrameWorkConfig.fiin_trade_password

        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}

        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument("--log-level=3")
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, chrome_options=options,desired_capabilities=caps)

        driver.get('https://fiintrade.vn')

        for i in range(10):
            try:
                driver.find_element(By.XPATH,'//*[@id="root"]/div[6]/header/div/div/div[3]/div[1]/div[2]').click()
                break
            except NoSuchElementException:
                time.sleep(3)

        for i in range(10):
            try:
                driver.find_element(By.XPATH,'//*[@id="exampleInputEmail1"]').send_keys(USERNAME)
                driver.find_element(By.XPATH,'//*[@id="exampleInputPassword1"]').send_keys(PASSWORD)
                driver.find_element(By.XPATH,'//*[@id="home"]/form/fieldset/div[3]/button').click()
                break
            except NoSuchElementException:
                time.sleep(3)

        def process_browser_log_entry(entry):
            response = json.loads(entry['message'])['message']
            return response

        browser_log = driver.get_log('performance') 
        events = [process_browser_log_entry(entry) for entry in browser_log]
        events = [event for event in events if 'Network.response' in event['method']]

        f = open("test.txt", "a")

        location:str = None
        for event in events:
            f.writelines(json.dumps(event))
            f.writelines('')
            f.writelines('')


        for event in events:
            try:
                if(event['params']['headers'].get('Location') != None):
                    location = event['params']['headers'].get('Location')
                    
            except KeyError:
                pass
            
        token = location.split('access_token=')[1].split('&')[0]
        driver.quit()
        logging.info(f'fiin trade token {token}')
        TradingFrameWorkConfig.fiin_cookie = f'Bearer {token}'

        return token