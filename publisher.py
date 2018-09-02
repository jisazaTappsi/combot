import time
import values


TEXT_BOX_CLASS_NAME = '_4h98 navigationFocus'
BUTTON_CLASS_NAME = '_1mf7 _4jy0 _4jy3 _4jy1 _51sy selected _42ft'


def publish_text(text, browser):

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
