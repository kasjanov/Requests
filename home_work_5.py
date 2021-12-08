import hashlib

from pymongo import MongoClient
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


chrome_options = Options()
chrome_options.add_argument('start-maximized')

login_name = 'study.ai_172'
passwd = 'NextPassword172#'
url = 'https://e.mail.ru'


def parser_letters_url(_driver, _url):
    _driver.get(url)

    # Авторизуемся на сервере почты
    login = WebDriverWait(_driver, 10).until(ec.visibility_of_element_located((By.NAME, 'username')))
    login.send_keys(login_name)
    login.submit()

    password = WebDriverWait(_driver, 10).until(ec.visibility_of_element_located((By.NAME, 'password')))
    password.send_keys(passwd)
    password.submit()

    # Вычисляем количество писем в почтовом ящике
    WebDriverWait(_driver, 20). \
        until(ec.visibility_of_element_located((By.XPATH, '//a[contains(@title, "Входящие")]')))
    number_letters = int(_driver.find_element(By.XPATH, '//a[contains(@title, "Входящие")]').
                         get_attribute('title').split(',')[1].split(' ')[1])

    url_list = set()

    # Собираем URL писем в почтовом ящике
    while len(url_list) < number_letters:
        WebDriverWait(_driver, 20). \
            until(ec.visibility_of_element_located((By.CLASS_NAME, 'js-letter-list-item')))
        letters_list = _driver.find_elements(By.CLASS_NAME, 'js-letter-list-item')

        for item in letters_list:
            url_list.add(item.get_attribute('href'))

        actions = ActionChains(_driver)
        actions.move_to_element(letters_list[-1])
        actions.perform()

    return url_list


def parser_letters(mail_list, driver, url_list):

    # Проходим по всем письмам и собираем информацию
    for item in url_list:
        letter = {}
        driver.get(item)
        driver.implicitly_wait(10)
        try:
            letter['from'] = driver.find_element(By.XPATH, '//span[@class="letter-contact"]').text
        except NoSuchElementException:
            letter['from'] = ''
        letter['from_link'] = driver.find_element(By.XPATH,
                                                  '//div[@class="letter__author"]/span').get_attribute('title')
        letter['date'] = driver.find_element(By.XPATH, '//div[@class="letter__date"]').text
        letter['subject'] = driver.find_element(By.XPATH, '//h2[@class="thread__subject"]').text
        text_objects = driver.find_elements(By.XPATH, '//div[@class="letter-body"]')
        full_text = ''
        for text in text_objects:
            full_text += text.text
        letter['text'] = full_text
        letter['_id'] = str(hashlib.md5(letter['from_link'].encode('utf-8', 'ignore')).hexdigest())
        mail_list.update_one({'_id': letter['_id']}, {'$set': letter}, upsert=True)


client = MongoClient('127.0.0.1', 27017)
db = client['mail']
mail_list = db.mail_list

driver_ = webdriver.Chrome(executable_path='./chromedriver.exe', options=chrome_options)

url_list_ = parser_letters_url(driver_, url)
parser_letters(mail_list, driver_, url_list_)

driver_.quit()
