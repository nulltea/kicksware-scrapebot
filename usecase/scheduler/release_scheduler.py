import time
import logging
import schedule
import traceback
import usecase.extract.releases_extractor as extractor
import usecase.extract.download_images as downloader
import usecase.transform.data_transformer as transformer
import model.sneaker_models as saver
from typing import List, Callable
from config.config import service_config as config


def run():
    logging.info("Scheduler is working...")
    while True:
        schedule.run_pending()
        time.sleep(60)


def schedule_daily_task():
    schedule.every(1).day.do(daily_task)


def daily_task():
    pipeline = [
        extractor.extract_releases,
        transformer.transform_data,
        downloader.download_images,
        saver.save_records
    ]
    if execute_pipeline(pipeline):
        logging.info("daily task completed successfully!")


def execute_pipeline(pipeline: List[Callable]) -> bool:
    records, success = None, False
    try:
        for i, step in enumerate(pipeline):
            if not i:
                records = step()
            elif i == (len(pipeline) - 1):
                success = step(records)
            else:
                records = step(records)
    except Exception as e:
        logging.error(f"pipeline failed with: {e}\r\n{traceback.format_exc()}")
    return success
