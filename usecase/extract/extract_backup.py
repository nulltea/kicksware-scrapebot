import os
import json
import logging
import pandas as pd
import mongoengine as mdb

from typing import List, Any
from model.sneaker_models import SneakerReference
from config.config import service_config as config

BACKUP_PATH = config.common.backup_path


def backup_records(records: List[mdb.Document], filename="backup"):
    backup_records_csv(records, f"{filename}.csv")
    backup_records_json(records, f"{filename}.json")


def backup_record(records: mdb.Document, filename="backup"):
    backup_record_csv(records, f"{filename}.csv")
    backup_record_json(records, f"{filename}.json")


def backup_records_json(records: List[mdb.Document], filename="backup.json"):
    all_docs = []
    path = os.path.join(BACKUP_PATH, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as fp:
            try:
                all_docs.extend(json.load(fp))
            except:
                pass
    all_docs.extend([r.to_mongo().to_dict() for r in records])
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(all_docs, fp, ensure_ascii=False, indent=4)


def backup_record_json(record: mdb.Document, filename="backup.json"):
    backup_records_json([record], filename)


def backup_records_csv(records: List[mdb.Document], filename="backup.csv"):
    df = pd.DataFrame([r.to_mongo().to_dict() for r in records])
    path = os.path.join(BACKUP_PATH, filename)
    df.to_csv(path, mode='a', header=(not os.path.exists(path)), na_rep="")


def backup_record_csv(record: mdb.Document, filename="backup.csv"):
    backup_records_csv([record], filename)


def backup(records: List[Any], filename="backup"):
    backup_csv(records, f"{filename}.csv")
    backup_json(records, f"{filename}.json")


def backup_one(records: Any, filename="backup"):
    backup_one_csv(records, f"{filename}.csv")
    backup_one_json(records, f"{filename}.json")


def backup_json(records: List[Any], filename="backup.json"):
    all_docs = []
    path = os.path.join(BACKUP_PATH, filename)
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as fp:
            try:
                all_docs.extend(json.load(fp))
            except:
                pass
    all_docs.extend(records)
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(all_docs, fp, ensure_ascii=False, indent=4)


def backup_one_json(record: Any, filename="backup.json"):
    backup_json([record], filename)


def backup_csv(records: List[Any], filename="backup.csv"):
    df = pd.DataFrame(records)
    path = os.path.join(BACKUP_PATH, filename)
    df.to_csv(path, mode='a', header=(not os.path.exists(path)), na_rep="")


def backup_one_csv(record: Any, filename="backup.csv"):
    backup_csv([record], filename)


def read_backup_records(filename="backup") -> List[SneakerReference]:
    records = None
    try:
        records = read_backup_records_json(f"{filename}.json")
    except:
        try:
            records = read_backup_records_csv(f"{filename}.csv")
        except:
            return []
    return records


def read_backup_records_json(filename="backup.json") -> List[SneakerReference]:
    path = os.path.join(BACKUP_PATH, filename)
    with open(path, 'r', encoding='utf-8') as fp:
        records = json.load(fp)
    return [SneakerReference.from_json(json.dumps(dt)) for dt in records]


def read_backup_records_csv(filename="backup.csv") -> List[SneakerReference]:
    path = os.path.join(BACKUP_PATH, filename)
    df = pd.read_csv(path)
    return [SneakerReference.from_json(json.dumps(dt)) for dt in list(df.T.to_dict().values())]


def close_backup(filename="backup"):
    records = read_backup_records(filename)
    if not records:
        try:
            os.remove(os.path.join(BACKUP_PATH,f"{filename}.json"))
            os.remove(os.path.join(BACKUP_PATH,f"{filename}.csv"))
        except Exception as e:
            logging.warning(f"empty backup files remove failed: {e}")
        return
