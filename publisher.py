import util
import values

TEXT_BOX_ID = 'find_out!!!'


def publish(browser):
    with open('text_to_publish.txt', 'r') as f:
        text = f.read()

        for idx, (group_name, group_url) in enumerate(values.get_groups_to_publish()):

            browser.get(group_url)

            text_box_element = browser.find_element_by_id(TEXT_BOX_ID)
            text_box_element.send_keys(text)
            text_box_element.send_keys(Keys.ENTER)


if __name__ == '__main__':
    publish(util.load_browser_and_login())
