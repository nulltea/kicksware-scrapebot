import time
import logging

import usecase.scheduler.release_scheduler as scheduler
import api.handler as api

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    logging.info("starting service...")
    api_proc = api.expose_api()
    scheduler_proc = scheduler.start()
    api_proc.join()
    scheduler_proc.join()

