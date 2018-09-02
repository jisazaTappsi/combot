"""
This file obeys the API to run, rather than manual messages from the .txt file
"""

import json
import requests

import util
import publisher


def publish_post(post, browser):
    text = post['fields']['text']
    publisher.publish_text(text, browser)


def get_posts():

    response = requests.get('https://peaku.co/api/get_public_posts')
    #response = requests.get('http://127.0.0.1:8000/api/get_public_posts')
    response.encoding = 'ISO-8859-1'

    data = json.loads(response.text)
    return json.loads(data)


def run():
    posts_queue = [m for m in get_posts()]
    browser = util.load_browser_and_login()

    while len(posts_queue) > 0:
        post = posts_queue[0]
        posts_queue = posts_queue[1:]
        publish_post(post, browser)


if __name__ == '__main__':
    run()
