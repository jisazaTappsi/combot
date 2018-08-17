from selenium.webdriver import Chrome
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import time
import pyautogui
import re
import pandas as pd
import os
from decouple import config
import platform

EMAIL_ID = 'email'
PASS_ID = 'pass'
LOGIN_BUTTON_ID = 'u_0_2'
SCROLL_SCREENS = 1
SCROLL_STEPS = int(config('scroll_steps'))
SCREEN_HEIGHT = 1080
COORDINATES = (int(config('coordinate_x')), int(config('coordinate_y')))
COLUMNS = ['post', 'word', 'group_name', 'group_url', 'count']
MAIN_URL = config('main_url')


def get_profile(split):
    closest_math = [m.start() for m in re.finditer(MAIN_URL, split)]
    if len(closest_math) > 0:
        closest_math = closest_math[-1]
        almost = split[closest_math:]
    else:
        return None

    pattern = f'{MAIN_URL}\S*'
    return re.search(pattern, almost).group()


def scrap_word(word, df, html, group_name, group_url):
    """
    :param word: string
    :param df: pandas Dataframe
    :param html: str html
    :param group_url: str
    :return: df
    """

    post_pattern = f'>[^>]*\s{word}\s[^<]*<'
    splits = re.compile(post_pattern).split(html)[:-1]
    
    # search email
    splits = [post for post in splits if '@' in post]

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
                #browser.save_screenshot(os.path.join('images', f'{post[:min(20, len(post))]}.png'))

                row = pd.Series({'post': post,
                                 'word': word,
                                 'group_name': group_name,
                                 'group_url': group_url,
                                 'count': 1}, name=profile)

                df = df.append(row)

    return df


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


def enable_permissions():
    pyautogui.moveTo(*COORDINATES)
    pyautogui.click(interval=0.1)


def scroll_down(group_name):
    for i in range(SCROLL_STEPS):
        height = SCREEN_HEIGHT * SCROLL_SCREENS
        browser.execute_script(f'window.scrollTo({i * height}, {(i + 1) * height})')

        # TODO: make this work
        browser.save_screenshot(os.path.join('images', f'{group_name}_{i}.png'))
        time.sleep(0.3)


def save_and_get_html():
    html = browser.page_source.lower()
    with open('page.html', 'w', encoding='utf-8') as f:
        f.write(html)

    return html


def get_file(name):
    with open(name, 'rb', encoding='utf-8') as my_file:
        return my_file.readlines()


def scrape_all():
    results = pd.DataFrame(columns=COLUMNS)

    for idx, group_name_and_url in enumerate(get_file('groups.txt')):

        group_name, group_url = group_name_and_url.split(',')
        browser.get(group_url)

        scroll_down(group_name)
        html = save_and_get_html()

        for word in get_file('keywords.txt'):
            results = scrap_word(word=word.lower().replace('\n', ''),
                                 df=results,
                                 html=html,
                                 group_url=group_url,
                                 group_name=group_name)

    results.sort_values(by='count', ascending=False).to_excel('leads.xlsx')


if __name__ == '__main__':

    browser = load_browser_and_login()
    scrape_all()
