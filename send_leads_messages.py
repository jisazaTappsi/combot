import requests
import urllib.parse
import pandas as pd
import util

DEBUG = False


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
    df['message'] = get_b2b_message()
    df['phone'] = df['phones'].apply(get_mobile_phone)
    # Removes lines with no phone
    df.dropna(subset=['phone'], axis=0, inplace=True)

    df['email'] = df['emails'].apply(get_first_email)

    return df


def run():

    df = read_excel_leads()
    print(df)
    root_url = 'http://127.0.0.1:8000' if DEBUG else 'https://peaku.co/'

    # TODO: make this a post and use the restfull api
    r = requests.get(urllib.parse.urljoin(root_url, 'api/add_messages'),  # 'login_user'),
                     {'names': df['name'], 'messages': df['message'],
                      'phones': df['phone'], 'emails': df['email']})
    print(r.status_code, r.reason)

    # TODO: https://stackoverflow.com/questions/10134690/using-requests-python-library-to-connect-django-app-failed-on-authentication
    """
    'username': 'my_account@peaku.co', 'password': 'my_happy_pass',
    cookies = dict(sessionid=r.cookies.get('sessionid'))

    r = requests.post(urllib.parse.urljoin(root_url, 'api/add_messages'),
                      data={'names': df['name'], 'messages': df['message'],
                            'phones': df['phone'], 'emails': df['email'],},
                      cookies=cookies)
    print(r.status_code, r.reason)
    """


if __name__ == '__main__':
    run()
