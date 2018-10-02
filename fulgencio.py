"""
Gets lots of job vacancies!
Writes them in leads.xlsx
"""

import time
import re
import pandas as pd
import os
from decouple import config
from selenium.common.exceptions import WebDriverException

import values
import util
from cts import *


EMAIL_ID = 'email'
PASS_ID = 'pass'
LOGIN_BUTTON_ID = 'u_0_2'
SCROLL_SCREENS = 1
SCREEN_HEIGHT = 1080
COORDINATES = (int(config('coordinate_x')), int(config('coordinate_y')))
COLUMNS = ['name', 'post', 'word', 'group_name', 'group_url', 'count']
MAIN_URL = config('main_url')
COMPANY_URL = 'company_url'
EMAILS = 'emails'
PHONES = 'phones'
NAME_CLASS_TAG = '_2nlw _2nlv'


def get_company_url_from_email(email):
    if email and not any([e in email for e in ('gmail', 'hotmail', 'yahoo', 'msn')]):
        return email.split('@')[1]
    else:
        return ''


def get_profile(split):
    closest_match = [m.start() for m in re.finditer(MAIN_URL, split)]
    if len(closest_match) > 0:
        closest_match = closest_match[-1]
        almost = split[closest_match:]
    else:
        return None

    pattern = f'{MAIN_URL}\S*'
    big_url = re.search(pattern, almost).group()

    return big_url.split('?')[0]


def filter_posts_with_email(df):
    return df[df['post'].apply(lambda p: len(re.findall(util.EMAIL_REGEX, p)) > 0)]


def scrap_word(word, df, html, group_name, group_url, browser):
    """
    :param word: string
    :param df: pandas Dataframe
    :param html: str html
    :param group_url: str
    :return: df
    """

    post_pattern = f'>[^>]*\s{word}\s[^<]*<'
    splits = re.compile(post_pattern).split(html)[:-1]

    # found nothing
    if len(splits) == 0:
        print(f'nothing found :( for word {word} on group {group_url}')
        return df

    posts = re.findall(post_pattern, html)
    for idx, split in enumerate(splits):
        profile = get_profile(split)
        if profile and MAIN_URL in profile:
            post = posts[idx].replace('>', '').replace('<', '')
            if profile in list(df.index.values):
                if post == df.loc[profile, 'post']:
                    df.loc[profile, 'count'] += 1
                else:
                    df.loc[profile, 'post'] += post
            else:

                phones = util.get_patterns(util.PHONE_REGEX, post)
                emails = util.get_patterns(util.EMAIL_REGEX, post)
                if emails or phones:

                    if len(emails) > 0:
                        company_url = get_company_url_from_email(emails[0])
                    else:
                        company_url = ''

                    try:
                        browser.get(profile)
                        name = browser.find_element_by_xpath(f"//*[@class='{NAME_CLASS_TAG}']")
                        name_text = name.text
                    except WebDriverException:
                        print(f'failed to load {profile}, continuing...')
                        name_text = ''

                    # By default will assign It to all positions
                    row = pd.Series({'name': name_text,
                                     'post': post,
                                     'phones': util.print_list(phones),
                                     'emails': util.print_list(emails),
                                     COMPANY_URL: company_url,
                                     'word': word,
                                     'group_name': group_name,
                                     'group_url': group_url,
                                     'count': 1,
                                     WORK_AREA_CODE: 'IT'}, name=profile)

                    df = df.append(row)

    return df


def scroll_down(group_name, scroll_steps, browser):
    for i in range(scroll_steps):
        height = SCREEN_HEIGHT * SCROLL_SCREENS
        browser.execute_script(f'window.scrollTo({i * height}, {(i + 1) * height})')

        # TODO: make this work
        browser.save_screenshot(os.path.join('images', f'{group_name}_{i}.png'))
        time.sleep(0.3)


def get_html(browser):
    return browser.page_source.lower()


def get_file(name):
    with open(name, 'rb', encoding='utf-8') as my_file:
        return my_file.readlines()


def scrape_company_url(results, browser):
    """
    The Angarita automation
    :return:
    """
    for profile, row in results.iterrows():
        if row[COMPANY_URL]:
            try:
                browser.get('http://www.' + row[COMPANY_URL])
                html = get_html(browser)

                emails = util.get_list_from_print(results.loc[profile, EMAILS]) + util.get_patterns(util.EMAIL_REGEX, html)
                emails = util.filter_emails(emails)

                phones = util.get_list_from_print(results.loc[profile, PHONES]) + util.get_patterns(util.PHONE_REGEX, html)
                phones = util.filter_phones(phones)

                results.loc[profile, EMAILS] = util.print_list(emails)
                results.loc[profile, PHONES] = util.print_list(phones)
            except WebDriverException:
                print(f'failed to load {row[COMPANY_URL]}, continuing...')

    # Save final result
    results.sort_values(by='count', ascending=False).to_excel('leads.xlsx')


def scrape_all(browser):
    results = pd.DataFrame(columns=COLUMNS)

    for idx, (group_name, group_url, scroll_steps) in enumerate(values.get_groups()):

        browser.get(group_url)

        scroll_down(group_name, scroll_steps, browser)
        html = get_html(browser)

        for word in values.get_keywords():
            results = scrap_word(word=word.lower().replace('\n', ''),
                                 df=results,
                                 html=html,
                                 group_url=group_url,
                                 group_name=group_name,
                                 browser=browser)

        # Escape odd chars and Save partial result
        results = results.applymap(lambda x: x.encode('unicode_escape').decode('utf-8') if isinstance(x, str) else x)
        results.sort_values(by='count', ascending=False).to_excel('leads.xlsx')

    scrape_company_url(results, browser)

    return results


if __name__ == '__main__':
    scrape_all(util.load_browser_and_login())


