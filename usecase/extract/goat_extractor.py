import re
from typing import List, Dict
from bs4 import BeautifulSoup
from usecase.extract.extract_common import *
from usecase.extract.extract_backup import *
from model.sneaker_models import SneakerReference
from config.config import service_config as config

MAX_PAUSE_TIME = config.common.max_pause_time
MIN_PAUSE_TIME = config.common.min_pause_time


def extract_releases() -> List[SneakerReference]:
    return extract(config.stadium_goods.releases_url)


def extract_search(query) -> List[SneakerReference]:
    target_url = config.goat.search_url.replace("{query}", query)   #todo target argument
    return extract(target_url)


def extract(url) -> List[SneakerReference]:
    extracted, found_existed, last_url, iteration = [], False, "", 0
    selector = 'a[data-qa="search_grid_cell"]'
    browser = provide_browser()
    browser.get(url)
    backuped_records = [r.goat_url for r in read_backup_records("goat")]
    while not found_existed:
        time.sleep(MAX_PAUSE_TIME)
        wait_until_located(browser, selector)
        product_tiles = browser.find_elements_by_css_selector(selector)
        if last_url and (last_elem := browser.find_element_by_css_selector(f'a[href="{last_url}"]')):
            index = product_tiles.index(last_elem) + 1
            if index == len(product_tiles):
                break
            product_tiles = product_tiles[index:]
        product_attrs = [(tile.get_attribute("href"), tile.get_attribute("title")) for tile in product_tiles]
        product_attrs = [(url, label) for url, label in product_attrs if url not in backuped_records]
        for url, label in product_attrs:
            time.sleep(MIN_PAUSE_TIME)
            logging.info(f'Start processing "{label}" product from "{url}"')
            browser.get(url)
            time.sleep(MAX_PAUSE_TIME)
            if record := extract_from_page(browser.page_source):
                record.generate_id()
                if not already_exists(record):
                    extracted.append(record)
                    backup_record(record, "goat")
                    continue
                found_existed = True
                break
        browser.get(url)
        iteration += 1
        scroll_to_last_element(browser, selector, iteration)
    return extracted


def extract_from_page(page_source) -> SneakerReference:
    source = BeautifulSoup(page_source, "html.parser")
    model_name = nickname = facts_data = description_data = price_data = None
    if title_elem := source.select_one('h1[data-qa="product_display_name_text"]'):
        title_content = title_elem.get_text()
        model_name, nickname = parse_title(title_content)
    if facts_elem := source.select_one('div[data-qa="product_display_nutritional_facts_module"]'):
        facts_data = parse_facts(facts_elem)
    if description_elem := source.select_one('div[data-qa="product_display_story_module"] p > p'):
        description_data = description_elem.get_text()
    if price_elem := source.select_one(".ProductTitlePaneActions__BuyPrice-l1sjea-4"):
        price_data = price_elem.get_text()
    sneaker_record = SneakerReference()
    sneaker_record.manufacture_sku = try_get_fact("sku", facts_data)
    sneaker_record.brand_name = try_get_fact("brand", facts_data)
    sneaker_record.model_name = model_name
    sneaker_record.nickname = try_get_fact("nickname", facts_data) or nickname
    sneaker_record.release_strdate = try_get_fact("release date", facts_data)
    sneaker_record.color = try_get_fact("main color", facts_data)
    sneaker_record.technology = try_get_fact("technology", facts_data)
    sneaker_record.categories = try_get_facts(["technology", "category"], facts_data)
    sneaker_record.designer = try_get_fact("designer", facts_data)
    sneaker_record.materials = try_get_facts(["upper material", "lower material", "material"], facts_data)
    sneaker_record.description = description_data
    sneaker_record.price = price_data.replace("$", "").strip()
    time.sleep(MIN_PAUSE_TIME)
    if (images := extract_images(source)) and len(images):
        sneaker_record.image_link = images[0]
        sneaker_record.image_links = images
    return sneaker_record


def extract_images(page_source: BeautifulSoup) -> List[str]:
    images = page_source.select('div[data-qa="image-carousel"] img')
    return [img.attrs["src"] for img in images]


def parse_title(title: str) -> (str, str):
    re_nickname = re.search(r"(?<=')(.*)'(?<=')", title)
    nickname = re_nickname.group(1)
    model_name = title.replace(f"'nickname'", "").strip()
    return nickname, model_name


def parse_facts(facts_elem: BeautifulSoup) -> dict:
    fact_dict = {}
    fact_elems = facts_elem.select("script")
    for fact in fact_elems:
        fields = fact.find_all("span")
        key = fields[0].get_text()
        value = fields[1].get_text()
        fact_dict[key] = value
    return fact_dict


def try_get_fact(key: str, facts: dict):
    try:
        return facts[key.upper()]
    except:
        return None


def try_get_facts(keys: [str], facts: dict):
    values = []
    for key in keys:
        try:
            values.append(facts[key.upper()])
        except:
            pass
    return values


def already_exists(record: SneakerReference) -> bool:
    return len(SneakerReference.objects(unique_id=record.unique_id)) != 0
