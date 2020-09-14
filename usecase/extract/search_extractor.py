import re
import string
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from usecase.extract.extract_common import *
from usecase.extract.extract_save import *
from model.sneaker_models import SneakerReference
from config.config import service_config as config
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


SELECT_KEYS = ["id", "name", "brand", "sku", "manufacturer_sku", "description", "color", "gender", "nickname",
               "price", "raw_price", "retail_price", "image_link", "template_image_link", "url", "sgp"]


def extract_by_search(tags_max=0, offset=0):
    browser = provide_browser()
    browser.get(config.target.sign_in_url)
    sign_in(browser)
    for i, tag in enumerate(alphanum_tags(max_length=tags_max, offset=offset)):
        selector = ".seller-searchbar input[type='text']"
        wait_until_located(browser, selector)
        search_input = browser.find_element_by_css_selector(selector)
        if not search_input:
            logging.error("could not find search input")
            continue
        wait_until_intractable(browser, search_input)
        input_tag(browser, search_input, tag)
        scroll_bottom(browser)
        time.sleep(2)
        scraper = BeautifulSoup(browser.page_source, 'html.parser')
        details = scraper.select("[id^=add-remove] a:last-child")
        maps = [unmarshal_button_content(html) for html in details]
        if len(maps) != 0:
            append_csv(os.path.join(config.common.backup_path, "details.csv"), maps)
            append_json(os.path.join(config.common.backup_path, "details.json"), maps)
        time.sleep(2)


def alphanum_tags(max_length=0, offset=0):
    tags = []
    for j, digit in enumerate(string.digits):
        tags.append(digit)
    for i, letter in enumerate(string.ascii_uppercase):
        tags.append(letter)
        for j, digit in enumerate(string.digits):
            tags.append(letter + digit)
            tags.append(digit + letter)
            for k, sub_digit in enumerate(string.digits):
                tags.append(digit + sub_digit)
    tags = list(set(tags))
    if max_length >= 0 and offset < max_length:
        return tags[offset:]
    return tags[offset:]


def sign_in(browser):
    username_input = browser.find_element_by_css_selector("#user_email")
    password_input = browser.find_element_by_css_selector("#user_password")
    remember_input = browser.find_element_by_css_selector(".chk-rdbtn-set .chkbox-label")

    username_input.send_keys(config.target.sign_in)
    password_input.send_keys(config.target.password)
    remember_input.click()

    browser.find_element_by_name("commit").click()


def input_tag(browser, input_elem, tag):
    actions = ActionChains(browser)
    actions.click(input_elem)
    actions.send_keys(Keys.CONTROL + "a")
    actions.send_keys(Keys.DELETE)
    actions.send_keys(tag)
    actions.send_keys(Keys.ENTER)
    actions.perform()


def unmarshal_button_content(html):
    js_code = html.get('onclick')
    if js_code is None or js_code == '' or not js_code:
        return None
    js_code = str(js_code).replace("\r\n", ' ')
    js_code = str(js_code).replace("\n", ' ')
    regex = re.compile(r'''{(.*)}''')
    json_str = f"{{{regex.search(js_code).groups()[0]}}}"
    obj = json.loads(json_str)
    return {key: obj.get(key) for key in SELECT_KEYS}
