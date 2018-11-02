
import platform
from decouple import config
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import json
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

    print('city field: ' + city_field)
    if '/' in city_field:
        city_field = city_field.split('/')[1]

    city_name = util.remove_accents_in_string(city_field.lower().strip())

    for id, db_city_name in cities_tuple:
        if city_name == db_city_name:
            return id

    # search for not available city
    for id, db_city_name in cities_tuple:
        if city_name == 'not available':
            return id


def get_campaign_id(campaign_tuple, campaign_name):

    campaign_name = util.remove_accents_in_string(campaign_name.lower().strip())

    for id, db_campaign_name in campaign_tuple:
        if campaign_name == db_campaign_name:
            return id

    return None


if __name__ == '__main__':

    response = requests.get(util.get_root_url() + '/api/v1/get_cities')
    cities = json.loads(response.json())
    cities_tuple = [(city['pk'], util.remove_accents_in_string(city['fields']['name']).lower().strip()) for city in cities]

    #browser.find_elements_by_class_name("icon pdf_hdv")[0].click()

    response = requests.get(util.get_root_url() + '/api/v1/get_campaigns')
    campaigns = json.loads(response.json())
    campaigns_tuple = [(c['pk'], util.remove_accents_in_string(c['fields']['name']).lower().strip()) for c in campaigns]

    browser = load_browser_and_login(config('bolsa1_url'))

    post_list_html = BeautifulSoup(browser.page_source, 'lxml')

    for subscribed_obj in post_list_html.find_all('li', class_='inscritos'):

        a = subscribed_obj.find('a', href=True)
        if a is not None and a.text:
            url = 'https://' + config('bolsa1_company_url') + a['href']
            print(url)
            browser.get(url)
            profile_list_html = BeautifulSoup(browser.page_source, 'lxml')

            campaign_name = profile_list_html.find('p', class_='gescan_subtit').span.strong.text.lower().strip()
            campaign_id = get_campaign_id(campaigns_tuple, campaign_name)

            for profile_article in profile_list_html.find_all('article', class_='rowuser pos_rel cp'):

                a = profile_article.find('a', class_='js-o-link nom ')
                if a is not None and a.text:

                    url = 'https://' + config('bolsa1_company_url') + a['href']
                    print(url)
                    browser.get(url)

                    html = util.get_html(browser)
                    with open('html_scrapper_bolsa1', 'w', encoding='latin-1') as f:
                        f.write(html)

                    profile_html = BeautifulSoup(browser.page_source, 'lxml')

                    user = dict()
                    user['campaign_id'] = campaign_id
                    user['name'] = profile_html.find('p', class_='').text.replace(' Hoja de vida de  ', '')
                    user['email'] = profile_html.find('span', class_='icon email').parent.text
                    phones_obj = profile_html.find_all('span', class_='fl fw_n mt3')

                    if phones_obj[0]:
                        user['phone'] = phones_obj[0].text

                    if len(phones_obj) > 1 and phones_obj[1]:
                        user['phone2'] = phones_obj[1].text

                    city_obj = profile_html.find('span', class_='icon pais')
                    user['city_id'] = get_city_id(cities_tuple, city_obj.parent.text)

                    salary_string = profile_html.find('span', class_='icon salario').parent.text

                    print('salary: ' + salary_string)
                    user['salary'] = int(salary_string.split('$')[1].strip().replace(',', '').split('.')[0])

                    print('user data:')
                    print(user)
                    response = requests.post(util.get_root_url() + '/api/v1/register', data=user)
                    print('sent user with response: ' + str(response.status_code))
