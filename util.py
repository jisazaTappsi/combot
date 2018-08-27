from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from decouple import config
import platform
import pyautogui

EMAIL_ID = 'email'
PASS_ID = 'pass'
LOGIN_BUTTON_ID = 'u_0_2'
SCROLL_SCREENS = 1
SCREEN_HEIGHT = 1080
COORDINATES = (int(config('coordinate_x')), int(config('coordinate_y')))
COLUMNS = ['post', 'word', 'group_name', 'group_url', 'count']
MAIN_URL = config('main_url')


def enable_permissions():
    pyautogui.moveTo(*COORDINATES)
    pyautogui.click(interval=0.1)


def load_browser_and_login():

    if platform.system() == 'Windows':
        browser = Chrome(executable_path='chrome_driver_win.exe')
    else:
        browser = Chrome()

    browser.get(MAIN_URL)

    email_element = browser.find_element_by_id(EMAIL_ID)
    email_element.send_keys(config('email'))

    pass_element = browser.find_element_by_id(PASS_ID)
    pass_element.send_keys(config('pass'))

    pass_element.send_keys(Keys.ENTER)

    enable_permissions()

    return browser
