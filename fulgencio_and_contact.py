import time
from selenium.webdriver.common.keys import Keys

import util
import fulgencio


INBOX_CLASS_NAME = '_42ft _4jy0 _4jy4 _517h _51sy'


def get_contact_text():
    return 'Vi que estás publicando una oferta laboral en redes sociales te invitamos a PeakU donde podrás encontrar los candidatos perfecto completamente grátis. https://peaku.co/seleccion_de_personal/seleccion_gratis'


if __name__ == '__main__':
    browser = util.load_browser_and_login()
    results = fulgencio.scrape_all(browser)

    text = get_contact_text()

    for idx, row in results.iterrows():

        print(idx)
        browser.get(idx)
        # TODO: test
        #browser.get('https://www.facebook.com/santiagopsa?fb_dtsg_ag=AdysXi0iM7Yj_xqdJzmHDkdtpJBXEq_IO8ffxkmWoB3MAw%3AAdw1ZMxR3g084CpOJLY8CxrQ0R2cQO_-rCudF2wbWys6OQ')

        inbox_button = browser.find_element_by_xpath(f"//*[@class='{INBOX_CLASS_NAME}']")
        inbox_button.click()

        time.sleep(2)

        active_element = browser.switch_to.active_element
        active_element.send_keys(text)
        active_element.send_keys(Keys.RETURN)
