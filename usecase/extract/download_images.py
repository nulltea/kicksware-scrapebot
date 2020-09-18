import os
import time
import logging
import urllib.request

from typing import List
from model.sneaker_models import SneakerReference
from config.config import service_config as config

PAUSE_TIME = config.common.max_pause_time


def download_images(records: List[SneakerReference]) -> List[SneakerReference]:
    for i, ref in enumerate(records):
        links = list(sorted(set(ref.image_links + [ref.image_link])))
        ref.image_links = []
        for j, link in enumerate(links):
            file_name = f"{ref.unique_id}.png" if j == 0 else f"{ref.unique_id}_{j+1}.png"
            image_path = os.path.join(config.common.image_storage_path, file_name)
            logging.info(f"Processing {ref.unique_id} {link}")
            if not os.path.exists(image_path):
                try:
                    time.sleep(PAUSE_TIME)
                    download(link, image_path)
                except Exception as e:
                    logging.warning(f"Download[{i}] {link} failed: {e}")
            if j == 0:
                ref.image_link = file_name
            else:
                ref.image_links.append(file_name)
    return records


def download(url, path):
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-Agent', 'IPhone')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, path)
