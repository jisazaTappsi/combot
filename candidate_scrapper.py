
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
import re
import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException

import util

EMAIL_ID = 'txEmail'
PASS_ID = 'txPwd'
CV_text = ' Hoja de vida de  '
EMAIL = 'email'
CAMPAIGN_ID = 'campaign_id'
KEY = 'key'
CSV_FILENAME = 'sent_candidates.csv'


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
# TODO: add missing params
    optional params to API:
        phone2

    optional FILES to combot:
        photo_url
        brochure_url
"""


def get_city(cities, city_field):

    if '/' in city_field:
        city_field = city_field.split('/')[1]

    city_name = util.remove_accents_in_string(city_field.lower().strip())

    closest_match = None
    closest_distance = 100
    for city in cities:
        db_city_name = util.remove_accents_in_string(city['fields']['name'].lower().strip())
        if city['fields']['alias']:
            db_city_alias = util.remove_accents_in_string(city['fields']['alias'].lower().strip())
        else:
            db_city_alias = 'this is never ever a city...'

        distance = stringdist.levenshtein(city_name, db_city_name)
        distance_alias = stringdist.levenshtein(city_name, db_city_alias)

        if (distance < closest_distance and distance < 6) or \
                (distance_alias < closest_distance and distance_alias < 6):  # if Levishtein distance is close enough will do!
            closest_match = city
            closest_distance = min(distance, distance_alias)
            print('city: ' + db_city_name + ' distance: ' + str(closest_distance))

    return closest_match


def get_campaign_with_id(campaigns, profile_list_html):

    campaign_name = profile_list_html.find(id='pMembPack').span.text
    campaign_name = util.remove_accents_in_string(campaign_name.lower().strip())

    matches = re.findall(r'\d+', campaign_name)
    if len(matches) > 0:
        campaign_id = int(matches[-1])
    else:
        print('could not find any match for campaign, will send candidate to Default Campaign :(')
        return None

    for c in campaigns:
        if int(c['pk']) == campaign_id:
            return c

    print('could not find any match for campaign, will send candidate to Default Campaign :(')
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
        user[CAMPAIGN_ID] = campaign['pk']
    if campaign and campaign['fields']['work_area']:
        user['work_area_id'] = campaign['fields']['work_area']

    name = get_name(profile_soup)
    if name:
        user['name'] = name

    emails = util.get_patterns(util.EMAIL_REGEX, html_source)
    emails = [t for t in emails if config('bolsa1_name') not in t and 'santiagopsa' not in t]

    if len(emails) > 0:
        user[EMAIL] = emails[0]

    phones_obj = profile_soup.find_all('span', class_='fl fw_n mt3')

    if len(phones_obj) > 0 and phones_obj[0]:
        user['phone'] = phones_obj[0].text

    if len(phones_obj) > 1 and phones_obj[1]:
        user['phone2'] = phones_obj[1].text

    city_obj = profile_soup.find('span', class_='icon pais')
    city = get_city(cities, city_obj.parent.text)
    if city:
        user['city_id'] = city['pk']

    salary_string = profile_soup.find('span', class_='icon salario').parent.text

    user['salary'] = int(salary_string.split('$')[1].strip().replace(',', '').split('.')[0])

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
    return [f for f in listdir(directory) if isfile(join(directory, f)) and 'crdownload' not in f]


def get_last_download_path():
    cv_directory = config('path_to_cvs')

    all_files = get_all_file_names(cv_directory)

    last_file = None
    file_time = 0
    for cv_path in [os.path.join(cv_directory, f) for f in all_files]:
        try:
            if os.path.getmtime(cv_path) > file_time:
                file_time = os.path.getmtime(cv_path)
                last_file = cv_path
        except FileNotFoundError:
            pass

    if last_file:
        return os.path.join(cv_directory, last_file)
    else:
        return None


def poll_for_last_download(current_cv_path):
    """
    Will wait for the download to finish, up to 5 min, else will output None
    :param current_cv_path: This is the last path just before clicking
    :return: a new path
    """
    timeout = 1*60

    current_time = time.time()
    while get_last_download_path() == current_cv_path and time.time() - current_time < timeout:
        time.sleep(1)

    return get_last_download_path() if get_last_download_path() != current_cv_path else None


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
            cv_path = os.path.join(config('path_to_cvs'), user[EMAIL].replace('.', ''))
            download_file(cv_url, cv_path)
            return cv_path

    return None


def get_complete_bolsa_url(href_url):
    return config('bolsa1_company_url') + href_url


def get_key(user, campaign):
    if campaign is not None:
        return user[EMAIL] + ' ' + str(campaign['pk'])
    else:
        return user[EMAIL] + ' None'


def candidate_not_sent(sent_candidates, user, campaign):
    return sum(sent_candidates[KEY] == get_key(user, campaign)) == 0


def send_user_with_cv(current_cv_path, user):

    cv_path = poll_for_last_download(current_cv_path)

    if cv_path is not None:

        with open(cv_path, 'rb') as cv:
            response = requests.post(util.get_root_url() + '/api/v1/register',
                                     data=user,
                                     files={'curriculum_url': cv})
        print('user cv_path: ' + cv_path)

        return response

    else:
        return requests.post(util.get_root_url() + '/api/v1/register', data=user)


def get_icon(browser, second_class):
    try:
        return browser.find_element_by_css_selector(".icon.{}".format(second_class))
    except NoSuchElementException:
        return None


def scrap_candidate(campaigns, cities, browser, sent_candidates):

    campaign = get_campaign_with_id(campaigns, BeautifulSoup(browser.page_source, 'html.parser'))

    user = scrap_profile(html_source=browser.page_source,
                         cities=cities,
                         campaign=campaign)

    if user.get(EMAIL) and candidate_not_sent(sent_candidates, user, campaign):

        current_cv_path = get_last_download_path()

        # TODO: if found more formats, please add:
        pdf_icon = get_icon(browser, 'pdf_hdv')
        doc_icon = get_icon(browser, 'doc_hdv')

        if pdf_icon:
            pdf_icon.click()
            response = send_user_with_cv(current_cv_path, user)
        elif doc_icon:
            doc_icon.click()
            response = send_user_with_cv(current_cv_path, user)
        else:
            response = requests.post(util.get_root_url() + '/api/v1/register', data=user)

        print('user data:')
        print(user)

        print('sent user with response: ' + str(response.status_code))

        return sent_candidates.append([{EMAIL: user[EMAIL],
                                       CAMPAIGN_ID: user.get(CAMPAIGN_ID),
                                       KEY: get_key(user, campaign)}])
    else:
        return sent_candidates


def run():
    cities = get_cities()
    campaigns = get_campaigns()

    try:
        sent_candidates = pd.read_csv(CSV_FILENAME, sep=',')
    except FileNotFoundError:
        sent_candidates = pd.DataFrame(columns=[EMAIL, CAMPAIGN_ID, KEY])

    browser = load_browser_and_login(config('bolsa1_url'))

    post_list_html = BeautifulSoup(browser.page_source, 'html.parser')

    for subscribed_obj in post_list_html.find_all('li', class_='inscritos'):

        a = subscribed_obj.find('a', href=True)

        if a is not None and a.text:
            url = get_complete_bolsa_url(a['href'])
            print('accessing: ' + url)
            browser.get(url)
            profile_list_html = BeautifulSoup(browser.page_source, 'html.parser')

            a = profile_list_html.find('a', class_='js-o-link nom ')

            if a is None:
                a = profile_list_html.find('a', class_='js-o-link nom visited')

            if a is not None and a.text:

                url = get_complete_bolsa_url(a['href'])
                print('accessing: ' + url)
                browser.get(url)

                while True:

                    sent_candidates = scrap_candidate(campaigns, cities, browser, sent_candidates)
                    sent_candidates.to_csv(CSV_FILENAME, sep=',')

                    try:
                        next_btn = browser.find_element_by_id('js-next')
                        next_btn.click()
                    except NoSuchElementException:
                        break


if __name__ == '__main__':
    run()
