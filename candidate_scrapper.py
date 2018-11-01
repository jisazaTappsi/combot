
import platform
from decouple import config
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests

import util

EMAIL_ID = 'txEmail'
PASS_ID = 'txPwd'


def load_browser_and_login(main_url):

    if platform.system() == 'Windows':
        browser = Chrome(executable_path='chrome_driver_win.exe')
    else:
        browser = Chrome()

    browser.get(main_url)
    browser.execute_script("ShowLogin();")

    email_element = browser.find_element_by_id(EMAIL_ID)
    email_element.send_keys(config('email_bolsa1'))

    pass_element = browser.find_element_by_id(PASS_ID)
    pass_element.send_keys(config('pass_bolsa1'))

    pass_element.send_keys(Keys.ENTER)

    """
    enable_permissions()
    """

    return browser


"""
    optional params:
        email = str
        name = str
        phone = str
        work_area_id = int
        city_id = int
        google_token = str
        politics = str
        campaign_id = int

    optional FILES:
        curriculum_url
        photo_url
        brochure_url
"""


def get_city_id(cities_tuple, city_field):

    city_name = util.remove_accents_in_string(city_field.split('/')[1].lower().strip())

    for id, db_city_name in cities_tuple:
        if city_name == db_city_name:
            return id

    # search for not available city
    for id, db_city_name in cities_tuple:
        if city_name == 'not available':
            return id


if __name__ == '__main__':

    cities = requests.get(util.get_root_url(), 'api/v1/get_cities')
    cities_tuple = [(city['pk'], util.remove_accents_in_string(city['fields']['name']).lower().strip()) for city in cities.json()]

    browser = load_browser_and_login(config('bolsa1_url'))

    post_list_html = BeautifulSoup(browser.page_source, 'lxml')

    for subscribed_url in post_list_html.find_all('li', class_='inscritos'):
        subscribed_url = subscribed_url.a['href']
        browser.get(subscribed_url)

        profile_list_html = BeautifulSoup(browser.page_source, 'lxml')
        for profile_article in profile_list_html.find_all('article', class_='rowuser pos_rel cp'):
            profile_url = profile_article.find('a', class_='js-o-link nom ').a['href']
            browser.get(profile_url)

            profile_html = BeautifulSoup(browser.page_source, 'lxml')

            user = dict()
            user['name'] = profile_html.find('p', class_='').text.replace(' Hoja de vida de  ', '')
            user['email'] = profile_html.find('span', class_='icon email').text
            phones_obj = profile_html.find_all('span', class_='fl fw_n mt3')

            if phones_obj[0]:
                user['phone'] = phones_obj[0].text

            if phones_obj[1]:
                user['phone2'] = phones_obj[1].text

            user['city_id'] = get_city_id(cities_tuple, profile_html.find('span', class_='icon email').text)

            salary_string = profile_html.find('span', class_='icon salary').text

            user['salary'] = int(salary_string.split('$')[1].strip().replace(',', '').split('.')[0])











# Brainstorming:

# 1. Pimp my CV
# 2. trivias
# hacer prueba con correos para ver respuesta:
    # a. formulario de CV-->google forms
    # b. formulario de trivia-->google forms

# 3. Hacer robot de Computrabajo y otras Bolsas --> hagale ya

# 4. Fulgencio para candidatos:
# + grupos
# + keywords
# Guion generico y ejecutar fulgencio mixto -> que pasa?
# partir el problema en 2

# 5. compartir --> personas pueden compartir ofertas

# 6. unsubscribe

# 7. Mejorar UI de tests

# 8. Entrar a Chile: David Escobar

