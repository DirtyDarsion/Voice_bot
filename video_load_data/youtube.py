from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import requests

from time import sleep
from humanize import naturalsize


def download_savefrom(user_download_url):
    """
    :param user_download_url: link to YouTube file
    :return:
    """

    url = 'https://ru.savefrom.net/'

    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    driver = webdriver.Chrome(options=options)
    driver.get(url)



    # elem = driver.find_element(By.CLASS_NAME, 'search__input')
    # elem.send_keys(user_download_url)
    # elem.send_keys(Keys.ENTER)
    #
    # while True:
    #     if driver.find_elements(By.CLASS_NAME, 'results__actions'):
    #         break
    #     sleep(1)
    #
    # result = driver.find_element(By.CLASS_NAME, 'results__item')
    # button = result.find_element(By.TAG_NAME, 'a')
    # file_url = button.get_attribute('href')
    # file_name = button.get_attribute('download')
    #
    driver.quit()
    #
    # response = requests.get(file_url)
    # file_size = response.headers['Content-Length']
    #
    # if len(file_size) < 9:
    #     with open('video_load_data/' + file_name, 'wb') as file:
    #         file.write(response.content)
    #     return {
    #         'file': 'video_load_data/' + file_name,
    #     }
    # else:
    #     return {
    #         'file': False,
    #         'link': file_url,
    #         'size': naturalsize(file_size),
    #     }
