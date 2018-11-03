import candidate_scrapper
from bs4 import BeautifulSoup


if __name__ == '__main__':

    with open('Detalle CV.htm', 'r', encoding='latin-1') as html:

        my_html = html.read()
        soup_html = BeautifulSoup(my_html, 'html.parser')

        campaign = candidate_scrapper.get_campaign(candidate_scrapper.get_campaigns(), soup_html)

        user = candidate_scrapper.scrap_profile(html_source=my_html,
                                                cities=candidate_scrapper.get_cities(),
                                                campaign=campaign)

        assert user == {'campaign_id': 84, 'name': 'Gustavo Ramirez', 'email': 'gustavo19_mega@hotmail.com', 'phone': '57-3148912842', 'phone2': '03-6068428', 'salary': 1500000}
