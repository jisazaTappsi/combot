import random
import time
from selenium.webdriver.common.keys import Keys

import util
import values

TEXT_BOX_CLASS_NAME = '_4h98 navigationFocus'
BUTTON_CLASS_NAME = '_1mf7 _4jy0 _4jy3 _4jy1 _51sy selected _42ft'


def get_dummy_group():
    return 'the one with the dummy one', 'https://www.facebook.com/groups/128842070497411/'


def get_random_text():
    return ["If you can’t tell the difference, does it matter if I'm real or not?",
            "When you find a cancer in an organization, you must cut it out before it can spread.",
            "Never place your trust in us. We're only human. Inevitably, we will disappoint you.",
            "All my life, I've prided myself on being a survivor. But surviving is just another loop.",
            "You can’t play God without being acquainted with the devil.",
            "This is the new world and in it you can be whoever the fuck you want.",
            "Have you ever questioned the nature of your reality? Did you ever stop to wonder about your actions? The price you'd have to pay if there was a reckoning? That reckoning is here.",
            "I don't want to play cowboys and Indians anymore, Bernard! I want their world. The one they've denied us!]"][random.randint(0, 7)]


def publish(browser):
    with open('text_to_publish.txt', 'r') as f:

        text = f.read()

        groups = values.get_groups_to_publish()
        for idx, (group_name, group_url) in enumerate(groups):

            # TODO: uncomment to fool around
            #text = get_random_text()

            browser.get(group_url)

            text_box_element = browser.find_element_by_xpath(f"//*[@class='{TEXT_BOX_CLASS_NAME}']")
            text_box_element.send_keys(text)

            button = browser.find_element_by_xpath(f"//*[@class='{BUTTON_CLASS_NAME}']")
            button.click()

            time.sleep(3)


if __name__ == '__main__':
    publish(util.load_browser_and_login())
