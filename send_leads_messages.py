import requests
import urllib.parse
import pandas as pd
import util
from decouple import config
from cts import *


def get_b2b_message():
    with open('B2B_message.txt') as f:
        return f.read()


# TODO: add more countries
def get_mobile_phone(phones):
    """
    :return: Gets first phone that complies with mobile phone rules in Colombia or None
    """
    if phones:
        for p in util.get_list_from_print(phones):
            if util.is_colombia_mobile(p):
                return p


def get_first_email(emails):
    """
    :return: Gets first email or return ''
    """
    if emails:
        for e in util.get_list_from_print(emails):
            return e
    return ''


def read_excel_leads():
    df = pd.read_excel('leads.xlsx')
    df['message'] = get_b2b_message().encode('ISO-8859-1')
    df['phone'] = df['phones'].apply(get_mobile_phone)
    # Removes lines with no phone
    df.dropna(subset=['phone'], axis=0, inplace=True)

    df['email'] = df['emails'].apply(get_first_email)

    return df


def run():

    df = read_excel_leads()
    print(df)
    root_url = 'http://127.0.0.1:8000' if DEBUG else 'https://peaku.co/'
    names = [n.replace(config('main_url'), '') for n in df.index.values]
    r = requests.post(urllib.parse.urljoin(root_url, 'api/save_leads'),  # 'login_user'),
                      {'names': names, 'facebook_urls': df.index.values,
                       'phones': df['phone'], 'emails': df['email']})
    print(r.status_code, r.reason)

    r = requests.post(urllib.parse.urljoin(root_url, 'api/add_messages'),
                      data={'names': df['name'], 'messages': df['message'],
                            'phones': df['phone'], 'emails': df['email'],
                            'facebook_urls': df.index.values})
    print(r.status_code, r.reason)


if __name__ == '__main__':
    run()
