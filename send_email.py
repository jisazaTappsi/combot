import pandas as pd
import requests
from decouple import config
import util


def get_files(attachment):
    if attachment:
        return [("attachment", (attachment, open(attachment, "rb").read()))]
    else:
        return []


def mail_gun_post(recipients, subject, body, attachment=None):
    try:
        requests.post(config('mailgun_url'),
                      auth=("api", config('mailgun_api_key')),
                      data={"from": config('email'),
                            "to": config('email'),
                            "bcc": recipients,
                            "subject": subject,
                            "text": body},
                      files=get_files(attachment), )
    except ConnectionError:
        print('Error connecting to mail_gun...')


def run():

    leads = pd.read_excel('leads.xlsx')
    emails = [util.get_list_from_print(string_list) for string_list in list(leads['emails'])]
    emails = util.flatten_list(emails)

    with open('email_body.txt', 'r', encoding='utf-8') as email_body:
        with open('email_subject.txt', 'r', encoding='utf-8') as email_subject:
            mail_gun_post(emails, email_subject.read(), email_body.read())


if __name__ == '__main__':
    run()
