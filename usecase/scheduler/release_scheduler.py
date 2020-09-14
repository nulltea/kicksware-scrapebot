import logging
import schedule
import usecase.extract.releases_extractor as extractor
import usecase.extract.download_images as downloader
import usecase.transform.data_transformer as transformer
import model.sneaker_models as saver
from typing import List, Callable


def schedule_daily_task():
    schedule.every(1).day.do(daily_task)


def daily_task():
    pipeline = [
        extractor.extract_releases,
        downloader.download_images,
        transformer.transform_data,
        saver.save_records
    ]
    if execute_pipeline(pipeline):
        logging.info("daily task completed successfully!")


def execute_pipeline(pipeline: List[Callable]) -> bool:
    records, success = None, False
    try:
        for i, step in pipeline:
            if not i:
                records = step()
            elif i == (len(pipeline) - 1):
                success = step(records)
            else:
                records = step(records)
    except Exception as e:
        logging.error(f"pipeline failed with: {e}")
    return success
