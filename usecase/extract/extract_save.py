import os
import json
import pandas as pd


def append_json(path, docs):
    all_docs = []
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as fp:
            all_docs.extend(json.load(fp))
    all_docs.extend(docs)
    with open(path, 'w', encoding='utf-8') as fp:
        json.dump(all_docs, fp, ensure_ascii=False, indent=4)


def append_csv(path, docs):
    df = pd.DataFrame(docs)
    df.to_csv(path, mode='a', header=(not os.path.exists(path)), na_rep="")
