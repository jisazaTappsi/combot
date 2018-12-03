import requests
import urllib.parse
from cts import *
import fulgencio
import util


def run():

    phone_leads = util.read_phone_excel_leads()
    phone_leads = fulgencio.filter_results(phone_leads)

    print(phone_leads)

    if not DEBUG:

        r = requests.post(urllib.parse.urljoin(util.get_root_url(), 'api/add_messages'),
                          data={'names': phone_leads['name'], 'messages': phone_leads['message'],
                                'phones': phone_leads['phone'], 'emails': phone_leads['email'],
                                'facebook_urls': phone_leads.index.values})
        print(r.status_code, r.reason)

    fulgencio.save_leads_in_api(phone_leads)


if __name__ == '__main__':
    run()
