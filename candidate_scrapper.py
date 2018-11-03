
import platform
from decouple import config
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import json
import stringdist
from os import listdir
from os.path import isfile, join
import os

import util

EMAIL_ID = 'txEmail'
PASS_ID = 'txPwd'
CV_text = ' Hoja de vida de  '


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

    return browser


"""
    optional params:
        phone2

    optional FILES:
        photo_url
        brochure_url
"""


def get_city(cities, city_field):

    if '/' in city_field:
        city_field = city_field.split('/')[1]

    city_name = util.remove_accents_in_string(city_field.lower().strip())

    for city in cities:
        #print(db_city_name)
        #print('distance: ' + str(stringdist.levenshtein(city_name, db_city_name)))
        if stringdist.levenshtein(city_name, city['fields']['name']) < 4:  # if Levishtein distance is close enough will do!
            return city

    return None


def get_max_campaign_with_id(campaigns):
    max_id = max([c['pk'] for c in campaigns])
    return [c for c in campaigns if c['pk'] == max_id][0]


def get_campaign(campaigns, profile_list_html):
    """
    Gets the last campaign, that its name is close enough.
    :param campaigns:
    :param profile_list_html:
    :return:
    """

    campaign_name = profile_list_html.find('p', class_='gescan_subtit').span.text.replace('Oferta', '')

    campaign_name = util.remove_accents_in_string(campaign_name.lower().strip())

    #print('campaign_name: ' + str(campaign_name))

    possible_campaigns = []
    for campaign in campaigns:
        #print(campaign['pk'])
        #print(campaign['fields']['title_es'])
        if stringdist.levenshtein(campaign_name, campaign['fields']['title_es']) < 3:  # if Levishtein distance is close enough will do!
            #print('added: ' + str(id))
            possible_campaigns.append(campaign)

    if len(possible_campaigns) > 0:
        return get_max_campaign_with_id(possible_campaigns)
    else:
        return None


def get_name(profile_html):
    for p in profile_html.find_all('p', {'class': 'fl'}):
        if CV_text in p.text:
            return p.text.replace(CV_text, '').replace('\n', '')

    return None


def scrap_profile(html_source, cities, campaign):

    profile_soup = BeautifulSoup(html_source, 'html.parser')

    user = dict()
    if campaign:
        user['campaign_id'] = campaign['pk']
    if campaign and campaign['fields']['work_area']:
        user['work_area_id'] = campaign['fields']['work_area']

    name = get_name(profile_soup)
    if name:
        user['name'] = name

    #user['name'] = profile_html.find_all('p', {'class': 'fl'}).text.replace(, '')

    emails = util.get_patterns(util.EMAIL_REGEX, html_source)
    emails = [t for t in emails if config('bolsa1_name') not in t and 'santiagopsa' not in t]

    if len(emails) > 0:
        user['email'] = emails[0]

    phones_obj = profile_soup.find_all('span', class_='fl fw_n mt3')

    if phones_obj[0]:
        user['phone'] = phones_obj[0].text

    if len(phones_obj) > 1 and phones_obj[1]:
        user['phone2'] = phones_obj[1].text

    city_obj = profile_soup.find('span', class_='icon pais')
    city = get_city(cities, city_obj.parent.text)
    if city:
        user['city_id'] = city['pk']

    salary_string = profile_soup.find('span', class_='icon salario').parent.text

    user['salary'] = int(salary_string.split('$')[1].strip().replace(',', '').split('.')[0])

    print('user data:')
    print(user)

    return user


def get_cities():
    response = requests.get(util.get_root_url() + '/api/v1/get_cities')
    return json.loads(response.json())


def get_campaigns():
    """
    List of dictionaries with campaigns
    :return:
    """
    response = requests.get(util.get_root_url() + '/api/v1/get_campaigns')
    return [c for c in json.loads(response.json()) if c['fields']['title_es'] is not None]


def get_all_file_names(directory):
    return [f for f in listdir(directory) if isfile(join(directory, f))]


def get_last_download_path():
    cv_directory = config('path_to_cvs')

    all_files = get_all_file_names(cv_directory)

    last_file = None
    file_time = 0
    for cv_path in [os.path.join(cv_directory, f) for f in all_files]:
        if os.path.getmtime(cv_path) > file_time:
            file_time = os.path.getmtime(cv_path)
            last_file = cv_path

    if last_file:
        return os.path.join(cv_directory, last_file)
    else:
        return None


def download_file(url, file_path):
    reply = requests.get(url, stream=True)
    with open(file_path, 'wb') as file:
        for chunk in reply.iter_content(chunk_size=1024):
            if chunk:
                file.write(chunk)


def download_and_get_cv_path(browser, user):
    """
    ONly implemented for CVs
    :param browser:
    :param user:
    :return:
    """

    profile_soup = BeautifulSoup(browser.page_source, 'html.parser')

    parent = profile_soup.find('div', {'id': 'cvCandidatePdf'})
    children = parent.findChildren("a", recursive=False)

    for a_tag_child in children:
        if a_tag_child['href'] != '#':
            cv_url = get_complete_bolsa_url(a_tag_child['href'])
            cv_path = os.path.join(config('path_to_cvs'), user['email'].replace('.', ''))
            download_file(cv_url, cv_path)
            return cv_path

    return None


def get_complete_bolsa_url(href_url):
    return config('bolsa1_company_url') + href_url


def run():
    cities = get_cities()
    campaigns = get_campaigns()

    browser = load_browser_and_login(config('bolsa1_url'))

    post_list_html = BeautifulSoup(browser.page_source, 'lxml')

    for subscribed_obj in post_list_html.find_all('li', class_='inscritos'):

        a = subscribed_obj.find('a', href=True)
        if a is not None and a.text:
            url = get_complete_bolsa_url(a['href'])
            print('accessing: ' + url)
            browser.get(url)
            profile_list_html = BeautifulSoup(browser.page_source, 'html.parser')

            campaign = get_campaign(campaigns, profile_list_html)

            for profile_article in profile_list_html.find_all('article', class_='rowuser pos_rel cp'):

                a = profile_article.find('a', class_='js-o-link nom ')
                if a is None:
                    a = profile_article.find('a', class_='js-o-link nom visited')

                if a is not None and a.text:

                    url = get_complete_bolsa_url(a['href'])
                    print('accessing: ' + url)
                    browser.get(url)

                    user = scrap_profile(html_source=browser.page_source,
                                         cities=cities,
                                         campaign=campaign)

                    #cv_path = download_and_get_cv_path(browser, user)

                    parent = browser.find_element_by_id('cvCandidatePdf')
                    parent.click()

                    cv_path = get_last_download_path()

                    if cv_path:
                        with open(cv_path, 'rb') as cv:
                            response = requests.post(util.get_root_url() + '/api/v1/register',
                                                     data=user,
                                                     files={'curriculum_url': cv})
                    else:  # no cv case
                        response = requests.post(util.get_root_url() + '/api/v1/register', data=user)
                    print('sent user with response: ' + str(response.status_code))


if __name__ == '__main__':
    run()
