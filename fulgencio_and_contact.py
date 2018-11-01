import time
import pandas as pd
from selenium.webdriver.common.keys import Keys
from decouple import config
from selenium.common.exceptions import WebDriverException

import util
import fulgencio


INBOX_CLASS_NAME = '_42ft _4jy0 _4jy4 _517h _51sy'
DEBUG = 0


def get_contact_text():
    with open('companies_message.txt', 'r', encoding='utf-8') as f:
        return f.read()


def send_message(results, text, browser):

    for my_idx, (idx_df, _) in enumerate(results.iterrows()):

        try:
            if DEBUG:
                if my_idx % 2:
                    browser.get(config('test_user_1'))
                else:
                    browser.get(config('test_user_2'))
            else:
                browser.get(idx_df)

            inbox_button = browser.find_element_by_xpath(f"//*[@class='{INBOX_CLASS_NAME}']")
            inbox_button.click()

            time.sleep(2)

            active_element = browser.switch_to.active_element
            active_element.send_keys(text)
            active_element.send_keys(Keys.RETURN)
            time.sleep(2)
        except WebDriverException:  # error accessing or interacting with elements.
            print(f"couldn't read url: {my_idx}")
            print('continuing...')
            continue


def run():

    browser = util.load_browser_and_login(config('fulgencio_url'))

    if DEBUG:
        results = pd.DataFrame([1, 2, 3, 4])
    else:
        results = fulgencio.scrape_all(browser)

    send_message(results, get_contact_text(), browser)


if __name__ == '__main__':
    run()
