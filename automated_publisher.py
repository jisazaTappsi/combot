"""
This file obeys the API to run, rather than manual messages from the .txt file
"""

import json
import requests
from queue import Queue

import util
import publisher
from decouple import config

DEBUG = 0


def publish_post(post, browser):
    text = post['fields']['text']
    publisher.publish_text(text, browser)


def get_posts():

    if DEBUG:
        response = requests.get('http://127.0.0.1:8000/api/get_public_posts')
    else:
        response = requests.get('https://peaku.co/api/get_public_posts')

    response.encoding = 'ISO-8859-1'

    data = json.loads(response.text)
    return json.loads(data)


def run():

    posts_queue = Queue()
    [posts_queue.put(m) for m in get_posts()]
    browser = util.load_browser_and_login(config('fulgencio_url'))

    while not posts_queue.empty():
        publish_post(posts_queue.get(), browser)


if __name__ == '__main__':
    run()
