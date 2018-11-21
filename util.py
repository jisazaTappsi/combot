from selenium.webdriver.common.keys import Keys
from selenium.webdriver import Chrome
from decouple import config
import platform
import pyautogui
import re
import statistics
import pandas as pd

from cts import *
import unicodedata

EMAIL_ID = 'email'
PASS_ID = 'pass'
LOGIN_BUTTON_ID = 'u_0_2'
SCROLL_SCREENS = 1
SCREEN_HEIGHT = 1080
COORDINATES = (int(config('coordinate_x')), int(config('coordinate_y')))
COLUMNS = ['post', 'word', 'group_name', 'group_url', 'count']
PHONE_REGEX = '(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})'
EMAIL_REGEX = '[a-z\.0-9_-]+@[a-z\.0-9_-]+\.[^png|jpg|jpeg|tiff][a-z\.0-9_-]+'
CHARS_TO_ERASE = ['-', ' ', '(', ')', '_', ',', '.']


def enable_permissions():
    pyautogui.moveTo(*COORDINATES)
    pyautogui.click(interval=0.1)


def load_browser_and_login(main_url):

    if platform.system() == 'Windows':
        browser = Chrome(executable_path='chrome_driver_win.exe')
    else:
        browser = Chrome()

    browser.get(main_url)

    email_element = browser.find_element_by_id(EMAIL_ID)
    email_element.send_keys(config('email'))

    pass_element = browser.find_element_by_id(PASS_ID)
    pass_element.send_keys(config('pass'))

    pass_element.send_keys(Keys.ENTER)

    enable_permissions()

    return browser


def print_list(my_list):
    return ', '.join(my_list)


def get_list_from_print(string):
    """
    inverse of print_list
    :param string:
    :return:
    """
    if string and type(string) is str:
        return string.split(', ')

    if type(string) is int:
        return [str(string)]
    return []


def flatten_list(l):
    return [item for sublist in l for item in sublist]


def get_patterns(pattern, string):
    matches = re.findall(pattern, string)
    if len(matches) > 0:
        return matches
    else:
        return []


def trim_chars(phone):
    for c in CHARS_TO_ERASE:
        phone = phone.replace(c, '')
    return phone


# TODO: add rules for other countries
def filter_phones(phones):
    filtered_phones = list({p for p in phones if statistics.stdev([int(d) for d in p if d in '0123456789']) > 2 and
                            is_colombia_phone(p)})

    # Trim phones a little bit
    return [trim_chars(p) for p in filtered_phones]


# TODO: add rules for other countries
def is_colombia_phone(phone):
    return is_colombia_mobile(phone) or is_colombia_landline(phone)


def is_colombia_mobile(phone):
    return len(phone) == 10 and 300 <= int(phone[0:3]) <= 330


def is_colombia_landline(phone):
    return len(phone) == 7


def filter_emails(emails):
    return list({e for e in emails })


def get_root_url():
    return 'http://127.0.0.1:8000' if DEBUG else 'https://peaku.co/'


def remove_accents_in_string(element):
    """
    Removes accents and non-ascii chars
    Args:
        element: anything.
    Returns: Cleans accents only for strings.
    """
    if isinstance(element, str):
        text = ''.join(c for c in unicodedata.normalize('NFD', element) if unicodedata.category(c) != 'Mn')
        # removes non ascii chars
        text = ''.join([i if ord(i) < 128 else '' for i in text])

        return text.replace('\x00', '')  # remove NULL char
    else:
        return element


def get_html(browser):
    return browser.page_source.lower()


def get_b2b_message():
    with open('B2B_message.txt', encoding='latin-1') as f:
        return f.read()


# TODO: add more countries
def get_first_mobile_phone(phones):
    """
    :return: Gets first phone that complies with mobile phone rules in Colombia or None
    """
    if phones:
        for p in get_list_from_print(phones):
            if is_colombia_mobile(p):
                return p


def get_first_email(emails):
    """
    :return: Gets first email or return None
    """
    if emails:
        for e in get_list_from_print(emails):
            return e


def remove_leads_with_no_phone(df):
    return df.dropna(subset=['phone'], axis=0)


def remove_leads_with_no_email(df):
    return df.dropna(subset=['email'], axis=0)


def read_excel_leads():
    df = pd.read_excel('leads.xlsx')
    df['phone'] = df['phones'].apply(get_first_mobile_phone)
    df['email'] = df['emails'].apply(get_first_email)
    return df


def read_phone_excel_leads():
    df = read_excel_leads()
    df['message'] = get_b2b_message().encode('ISO-8859-1')
    return remove_leads_with_no_phone(df)


def read_email_excel_leads():
    df = read_excel_leads()
    return remove_leads_with_no_email(df)


if __name__ == '__main__':
    emails = get_list_from_print('') + \
             get_patterns(EMAIL_REGEX, ' sadasd many@mail.co shit in between another@one.com')

    phones = ['3936101', '1536802200', '3936101', '3936101', '3936101', '3936101', '1519368455', '5226202',
              '5226202', '2333333', '2175250', '8523419016', '5966817755', '1150665', '1523550543', '1535583475',
              '0833333333', '3333333', '1666666666', '6666666', '3333333333', '4166666666', '5833333333',
              '6666666666', '8333333333', '9166666666', '1526255173', '1067498', '1067498', '1519368455',
              '1519368455', '5226202', '5226202', '6287551', '6287551', '7142820', '7142820', '7397726',
              '7397726', '1409236', '1409236', '4716900', '4716900', '2977896', '2977896', '0268170',
              '0268170', '1526243156', '1526243156', '1526242982', '1526242982', '2173079', '8523056482',
              '6047429684', '0397940', '2173079', '8523056482', '6047429684', '0397940', '2173079', '8523056482',
              '6047429684', '0397940', '2173079', '8523056482', '6047429684', '0397940', '1526242723', '2173079',
              '8523056482', '6047429684', '0397940', '2173079', '8523056482', '6047429684', '0397940', '2173079',
              '8523056482', '6047429684', '0397940', '2173079', '8523056482', '6047429684', '0397940', '1526242723',
              '2451902', '3936101', '1523550543', '1535583475', '9999999', '1999998', '1999999']

    phones = ['5149255',
              '215 8043',
              '4909751276',
              '1103459835',
              '4030703326',
              '215 8043',
              '215 9698']

    phones = ['1855745',
                '4022681',
                '9889277046',
                '8282677',
                '8282677',
                '9462725592',
                '0162020',
                '016-2020',
                '016-2020',
                '016-2020',
                '2770449',
                '932-1965',
                '932-1965',
                '932-1965',
                '932-1965',
                '932-1965',
                '1039951808',
                '9852928',
                '1039929160',
                '1546567',
                '1039906577',
                '3173432',
                '1039997113',
                '3782548',
                '1039974458',
                '1261557',
                '1039951808',
                '9852928',
                '1039929160',
                '1546567',
                '1039906577',
                '3173432',
                '1039997113',
                '3782548',
                '1039974458',
                '1261557',
                '1039951808',
                '9852928',
                '4033792',
                '5608103910',
                '7602175134',
                '3138871',
                '4281410',
                '4034672',
                '5379147399',
                '4809041817',
                '4670562',
                '3993653',
                '8875127047',
                '3473901085',
                '3136801',
                '4100412',
                '3252973515',
                '7088949249',
                '3245178',
                '5039495703',
                '4098534',
                '6671193669',
                '2241930455',
                '0722946',
                '1507129432',
                '4126106',
                '1580200584',
                '5511007640',
                '9884345',
                '4033792',
                '5608103910',
                '7602175134',
                '3138871',
                '4281410',
                '4034672',
                '5379147399',
                '4809041817',
                '4670562',
                '3993653',
                '8875127047',
                '3473901085',
                '3136801',
                '4100412',
                '3252973515',
                '7088949249',
                '3245178',
                '5039495703',
                '4098534',
                '6671193669',
                '2241930455',
                '0722946',
                '1507129432',
                '4126106',
                '1580200584',
                '5511007640',
                '9884345',
                '5713394949',
                '5713394949',
                '3128674831',
                '5192149716',
                '1202574',
                '9889277046',
                '8565028',
                '2381979']

    phones = ['1535664563',
                '1535476394',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '0000000000',
                '0000003',
                '616 0492',
                '312 777 1447']

    print(filter_phones(phones))
