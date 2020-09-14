import os
import logging
import urllib.request

from typing import List
from model.sneaker_models import SneakerReference
from config.config import service_config as config


def download_images(records: List[SneakerReference]):
    for i, ref in enumerate(records):
        links = list(sorted(set(ref.image_links + [ref.image_link])))
        for j, link in enumerate(links):
            file_name = f"{ref.unique_id}.png" if j == 0 else f"{ref.unique_id}_{j+1}.png"
            image_path = os.path.join(config.common.image_storage_path, file_name)
            if os.path.exists(image_path):
                continue
            try:
                download(link, image_path)
            except Exception as e:
                logging.warning(f"Download[{i}] {link} failed: {e}")
                continue


def download(url, path):
    opener = urllib.request.URLopener()
    opener.addheader('User-Agent', 'IPhone')
    opener.retrieve(url, path)
