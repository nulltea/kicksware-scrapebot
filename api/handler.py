import logging
import usecase.extract.extract_backup as backup
import usecase.scheduler.release_scheduler as scheduler
from flask import Flask, Response, jsonify
from config.config import service_config as config
from multiprocessing import Process

handler = Flask(__name__)


def expose_api() -> Process:
    process = Process(target=__expose_api)
    process.start()
    return process


def __expose_api():
    handler.run(host=config.common.api_host, port=config.common.api_port, threaded=True)
    logging.info(f"API exposed and available by address: {config.common.api_host}:{config.common.api_port}")


@handler.route("/backup")
def get_backup():
    return jsonify([r.to_mongo().to_dict() for r in backup.read_backup_records()])


@handler.route("/backup/<filename>")
def get_backup_file(filename):
    return jsonify([r.to_mongo().to_dict() for r in backup.read_backup_records(filename)])


@handler.route("/daily/run", methods=["POST"])
def run_daily_task():
    scheduler.process_daily_task()
    return "Task running..."


@handler.route("/daily/terminate", methods=["POST"])
def terminate_daily_task():
    scheduler.terminate_daily_task()
    return "Task terminated."


@handler.route("/daily/cancel", methods=["POST"])
def cancel_daily_task():
    scheduler.cancel_daily_task()
    return "Task canceled."


@handler.route("/daily/schedule", methods=["POST"])
def schedule_daily_task():
    scheduler.schedule_daily_task()
    return "Task scheduled"


@handler.route("/schedule/start", methods=["POST"])
def start_schedule():
    scheduler.start()
    return "Scheduler started!"


@handler.route("/schedule/stop", methods=["POST"])
def stop_schedule():
    scheduler.stop()
    return "Scheduler stopped"


@handler.route("/health/live")
def live():
    return Response(status=200)


@handler.route("/health/ready")
def ready():
    return Response(status=200)


