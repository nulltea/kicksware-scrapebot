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
from multiprocessing import Process, Queue

daily_job = schedule.Job(interval=1)
daily_task_process = Process()
scheduler_process = Process()


def start() -> Process:
    global scheduler_process
    scheduler_process = Process(target=__start)
    scheduler_process.start()
    return scheduler_process


def __start():
    logging.info("Scheduler is working...")
    while True:
        schedule.run_pending()
        time.sleep(60)


def stop():
    global scheduler_process
    scheduler_process.close()
    logging.info("Scheduler is stopped.")


def schedule_daily_task():
    global daily_job
    daily_job = schedule.every(1).day.do(daily_task)


def cancel_daily_task():
    global daily_job
    schedule.cancel_job(daily_job)


def process_daily_task():
    global daily_task_process
    logging.info("starting daily task process...")
    daily_task_process = Process(target=daily_task)
    daily_task_process.start()
    daily_task_process.join()


def terminate_daily_task():   # TODO terminate task
    global daily_task_process
    daily_task_process.terminate()
    logging.info("daily task process terminated.")


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
            print(f"Execution {i+1} step [{step.__name__}] with {(0 if not records else len(records))} records")
            if not i:
                records = step()
            elif i == (len(pipeline) - 1):
                success = step(records)
            else:
                records = step(records)
            if not len(records) and not i:
                logging.info("nothing was extracted, stopping pipeline here")
                break
            else:
                logging.warning(f"step [{step.__name__}] does not return any records, but they was at last step, " +
                                "stopping pipeline here")
                break
    except Exception as e:
        logging.error(f"pipeline failed with: {e}\r\n{traceback.format_exc()}")
    return success
