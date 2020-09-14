import re
import json
import logging
import pandas as pd
import numpy as np
import mongoengine as mdb

from typing import List, Dict
from model.sneaker_models import SneakerReference
from config.config import service_config as config


def transform_data(data: List[SneakerReference]) -> List[SneakerReference]:
    df = to_dataframe(data)
    unique_ids = get_unique_ids(df)

    pipeline = [
        distinct,
        query_by_brandname,
        query_by_modelname,
        handle_nan,
        union_with_db,
        base_model_by_categories,
        base_model_by_predefined
    ]

    for step in pipeline:
        df = step(df)

    df = get_target_records(df, target_ids=unique_ids)
    return generate_db_records(df)


def to_dict(data: List[mdb.Document]) -> List[dict]:
    return [r.to_mongo().to_dict() for r in data]


def to_dataframe(data: List[mdb.Document]) -> pd.DataFrame:
    dicts = to_dict(data)
    fields = list(dicts[0].keys())
    return pd.DataFrame(to_dict(data), columns=fields[1:])


def query_by_brandname(df: pd.DataFrame) -> pd.DataFrame:
    with open("../meta/brands.json", "r") as stream:
        brand_query = json.load(stream)
    filtered = df.brandname.isin(brand_query)
    logging.info(f"found {len(df) - len(filtered)} records to filter out by brand names")
    return df[~filtered]


def query_by_modelname(df: pd.DataFrame) -> pd.DataFrame:
    with open("../meta/modelname-nin-query.json", "r") as stream:
        keywords_query = json.load(stream)
    filtered = df.modelname.str.contains(keywords_query)
    logging.info(f"found {len(filtered)} records to filter out by modelname keywords")
    return df[~filtered]


def distinct(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset="uniqueid", keep="first")


def handle_nan(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace(np.nan, '', regex=True)


def get_unique_ids(df: pd.DataFrame) -> List[str]:
    return list(pd.unique(df.uniqueid.values))


def union_with_db(df: pd.DataFrame) -> pd.DataFrame:
    dbf = to_dataframe(SneakerReference.objects())
    df = df.merge(dbf, on="uniqueid")
    return handle_nan(df)


# Determine base model by categories
def base_model_by_categories(df: pd.DataFrame) -> pd.DataFrame:
    df["BaseModel"] = df.apply(determine_base_model, axis=1)
    return df


def camel_case_split(s):
    idx = list(map(str.isupper, s))
    l = [0]
    for (i, (x, y)) in enumerate(zip(idx, idx[1:])):
        if x and not y:
            l.append(i)
        elif not x and y:
            l.append(i + 1)
    l.append(len(s))
    return [s[x:y] for x, y in zip(l, l[1:]) if x < y]


def get_acronym(source):
    return "".join(filter(str.isupper, source.title()))


def determine_base_model(row):
    modelname = row["modelname"]
    categories = row["categories"]
    if not categories:
        return None
    distances = {}
    for category in categories:
        distance = sum([word.lower() in modelname.lower() for word in camel_case_split(category)])
        if not distance:
            distance = 1 if get_acronym(category) in modelname else 0
        if distance:
            distances[category] = distance

    base_model = max(distances or [None], key=distances.get)
    return base_model


# Determine base model by predefined base model list
def base_model_by_predefined(df: pd.DataFrame) -> pd.DataFrame:
    base_models = pd.read_json("../meta/base-model-tags.json")[0].tolist()

    s = df.modelname.str.len().sort_values(ascending=False).index
    sdf = df.reindex(s)
    sequence = list(sdf.T.to_dict().values())
    groups = {}
    for model in base_models:
        child_models = [item for item in sequence if model.upper() in item["modelname"].upper()]
        [sequence.remove(item) for item in child_models]
        groups[model] = child_models

    sequence = list()
    for key, items in groups.items():
        sequence.extend([dict(item, basemodel=key) for item in items])
    return pd.DataFrame(sequence)


def map_base_model_names(df: pd.DataFrame) -> pd.DataFrame:
    with open("../meta/base-model-map.json", "r") as stream:
        model_map = json.load(stream)
    df["basemodelname"] = df["basemodelname"].map(model_map).fillna(df["basemodelname"])
    return df


def get_target_records(df: pd.DataFrame, target_ids) -> pd.DataFrame:
    return df[df.uniqueid.isin(target_ids)]


def generate_db_records(df: pd.DataFrame) -> List[SneakerReference]:
    references = [dt for dt in list(df.T.to_dict().values())]
    return [map_to_db_record(row) for row in references]


def map_to_db_record(ref: dict) -> SneakerReference:
    unique_id = ref["uniqueid"]
    brand = model = basemodel = None
    re_id = re.compile(r"[\n\t\s;,.()\\/]")
    try:
        brand_id = re_id.sub("-", ref["brand"])
        brand = brand_id
    except:
        print(f"Error finding brand: '{brand_id}'")
    try:
        model_id = re_id.sub("-", ref["name"])
        model_id = f"{brand_id}_{model_id}"
        model = model_id
    except:
        print(f"Error finding model: '{model_id}'")
    try:
        if ref["basemodel"]:
            basemodel_id = re_id.sub("-", ref["basemodel"])
            basemodel_id = f"{brand_id}_{basemodel_id}"
            basemodel = basemodel_id
    except:
        print(f"Error finding basemodel: '{basemodel_id}'")

    return SneakerReference(
        unique_id=unique_id,
        manufacture_sku=ref["manufacturesku"],
        brand_name=ref["brandname"],
        brand=brand,
        model_name=ref["modelname"],
        model=model,
        base_model_name=ref["basemodel"],
        base_model=basemodel,
        description=ref["description"],
        color=ref["color"],
        gender=ref["gender"],
        nickname=ref["nickname"],
        release_date=ref["releasedate"],
        release_strdate=ref["releasedate"],
        price=ref["price"],
        materials=ref["Materials"] if len(ref["Materials"]) else None,
        categories=ref["Categories"] if len(ref["Categories"]) else None,
        image_link=f"{unique_id}.png",
        image_links=generate_image_names(ref),
        stadium_url=ref["url"],
    )


def generate_image_names(ref) -> List[str]:
    images = []
    unique_id = ref["uniqueid"]
    links = ref["imagelinks"]
    for i in range(2, len(links) + 1):
        filename = f"{unique_id}_{i}.png"
        images.append(filename)
    return images
