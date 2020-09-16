import time
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebElement, WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from config.config import service_config as config

PAUSE_TIME = config.common.min_pause_time


def provide_browser() -> WebDriver:
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1420,1080")
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-setuid-sandbox")
    options.add_argument("--disable-extensions")
    prefs = {"profile.managed_default_content_settings.images": 2}
    options.add_experimental_option("prefs", prefs)
    browser = webdriver.Chrome(options=options)
    return browser


def scroll_to_element(browser: WebDriver, element: WebElement):
    actions = ActionChains(browser)
    actions.move_to_element(element).perform()


def scroll_to_last_element(browser: WebDriver, selector: str, times: int):
    wait_until_located(browser, selector)
    for _ in range(times):
        time.sleep(PAUSE_TIME)
        last = browser.find_elements_by_css_selector(selector)[-1]
        scroll_to_element(browser, last)


def scroll_bottom(browser: WebDriver):
    last_height = browser.execute_script("return document.body.scrollHeight")
    while True:
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(PAUSE_TIME)
        new_height = browser.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def wait_until_located(browser: WebDriver, selector: str):
    try:
        WebDriverWait(browser, 5).until(ec.presence_of_element_located((By.CSS_SELECTOR, selector)))
    except:
        return


def wait_until_intractable(browser: WebDriver, selector: str):
    time.sleep(1)
    try:
        WebDriverWait(browser, 10).until(ec.element_to_be_clickable(selector))
    except:
        return
