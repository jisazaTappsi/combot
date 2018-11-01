import random

import util
import publisher
from decouple import config


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
    with open('text_to_publish.txt', 'r', encoding='utf-8') as f:
        text = f.read()
        publisher.publish_text(text, browser)


if __name__ == '__main__':
    publish(util.load_browser_and_login(config('fulgencio_url')))
