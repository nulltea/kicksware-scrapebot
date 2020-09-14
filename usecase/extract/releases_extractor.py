import re
import demjson
import logging
from typing import List, Dict
from bs4 import BeautifulSoup
from usecase.extract.extract_common import *
from model.sneaker_models import SneakerReference
from config.config import service_config as config


def extract_releases() -> List[SneakerReference]:
    extracted, found_existed, last_label, iteration = [], False, "", 0
    selector = 'a[data-element="Product Tile"]'
    browser = provide_browser()
    browser.get(config.target.releases_url)
    while not found_existed:
        wait_until_located(browser, selector)
        product_tiles = browser.find_elements_by_css_selector(selector)
        if last_label and (last_elem := browser.find_element_by_css_selector(f'a[aria-label="{last_label}"]')):
            index = product_tiles.index(last_elem) + 1
            if index == len(product_tiles):
                break
            product_tiles = product_tiles[index:]
        for tile in product_tiles:
            product_link = tile.get_attribute("href")
            product_label = last_label = tile.get_attribute("aria-label")
            logging.info(f'Start processing "{product_label}" product from "{product_link}"')
            browser.get(product_link)
            if record := extract_from_page(browser.page_source):
                record.generate_id()
                if not already_exists(record):
                    extracted.append(record)
                    continue
                found_existed = True
                break
        browser.get(config.target.releases_url)
        iteration += 1
        scroll_to_last_element(browser, selector, iteration)
    return extracted


def extract_from_page(page_source) -> SneakerReference:
    source = BeautifulSoup(page_source, "html.parser")
    meta_data, script_data, brand_data, material_data, attr_data = None, None, None, None, None
    if meta_elem := source.select_one("meta[name=description]"):
        meta_content = meta_elem.attrs["content"]
        meta_data = parse_meta(meta_content)
    if modal_elem := source.select_one("#modal-product"):
        script_elem = modal_elem.find_previous_sibling("script")
        script_data = parse_script(script_elem.contents[0])
    if meta_brand := source.select_one("meta[itemprop=category]"):
        brand_data = meta_brand.attrs["content"]
    if meta_material := source.select_one("meta[itemprop=material]"):
        material_data = meta_material.attrs["content"]
    if attr_table := source.select_one("#product-attribute-specs-table"):
        attr_data = parse_table(attr_table)
    sneaker_record = SneakerReference()
    if meta_data:
        sneaker_record.manufacture_sku = meta_data["SKU"]
        sneaker_record.model_name = meta_data["Name"]
        sneaker_record.release_strdate = meta_data["ReleaseDate"]
        sneaker_record.color = meta_data["Color"]
        sneaker_record.description = meta_data["Description"]
    if script_data:
        if not sneaker_record.manufacture_sku and (sku := script_data["SKU"]):
            sneaker_record.manufacture_sku = sku.split("|")[-1]
        if name := script_data["Name"]:
            sneaker_record.model_name = name
        sneaker_record.price = script_data["Price"]
        sneaker_record.categories = script_data["Categories"]
        sneaker_record.stadium_url = script_data["URL"]
    if brand_data:
        sneaker_record.brand_name = brand_data
    if material_data:
        sneaker_record.materials = [material.strip() for material in material_data.split(",")]
    if attr_data:
        if not sneaker_record.manufacture_sku and (sku := attr_data["Manufacturer Sku"]):
            sneaker_record.manufacture_sku = sku
        if not sneaker_record.release_strdate and (date := attr_data["Release Date"]):
            sneaker_record.release_strdate = date
        if not sneaker_record.color and (color := attr_data["Colorway"]):
            sneaker_record.colorway = color
        sneaker_record.nickname = attr_data["Nickname"]
        sneaker_record.gender = attr_data["Gender"]
    if (images := extract_images(source)) and len(images):
        sneaker_record.image_link = images[0]
        sneaker_record.image_links = images
    return sneaker_record


def extract_images(page_source: BeautifulSoup) -> List[str]:
    gallery = page_source.select_one(".product-gallery")
    images = gallery.select("img")
    return [img.attrs["src"] for img in images]


def parse_script(script):
    regex = re.compile(r"(?<=var item = {)(.*)(?=};)", flags=re.DOTALL)
    match = regex.search(script)
    if match and (group := match.group(1)):
        json_str = f"{{{group.strip()}}}"
        return demjson.decode(json_str)


def parse_meta(meta_source) -> Dict[str, str]:
    re_sku = re.search(r"(?<=SKU: )(.*)", meta_source)
    re_name = re.search(r"\n(.*)\n", meta_source)
    re_date = re.search(r"(?<=Release Date: )(.*)", meta_source)
    re_color = re.search(r"(?<=Color: )(.*)", meta_source)
    re_description = re.search(r"^(.*)\n", meta_source)
    meta = {
        "SKU": re_sku[0].strip() if re_sku else None,
        "Name": re_name[0].strip() if re_name else None,
        "ReleaseDate": re_date[0].strip() if re_date else None,
        "Color": re_color[0].strip() if re_color else None,
        "Description": re_description[0].strip() if re_description else None,
    }
    return meta


def parse_table(table_source) -> Dict[str, str]:
    data = None
    if table_body := table_source.find("tbody"):
        data = {}
        rows = table_body.find_all("tr")
        for row in rows:
            key = row.find("th").text.strip()
            value = row.find("td").text.strip()
            data[key] = value
    return data


def already_exists(record: SneakerReference) -> bool:
    return len(SneakerReference.objects(unique_id=record.unique_id)) != 0
