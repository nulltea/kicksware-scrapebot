import time
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebElement, WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By as by
from selenium.webdriver.support import expected_conditions as ec


def provide_browser() -> WebDriver:
    options = webdriver.ChromeOptions()
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(options=options)
    return browser


def scroll_to_element(browser: WebDriver, element: WebElement):
    actions = ActionChains(browser)
    actions.move_to_element(element).perform()


def scroll_to_last_element(browser, selector, times):
    wait_until_located(browser, selector)
    for _ in range(times):
        time.sleep(5)
        last = browser.find_elements_by_css_selector(selector)[-1]
        scroll_to_element(browser, last)


def wait_until_located(browser: WebDriver, selector):
    try:
        WebDriverWait(browser, 5).until(ec.presence_of_element_located((by.CSS_SELECTOR, selector)))
    except:
        return
