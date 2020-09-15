import re
import mongoengine as mdb
from typing import List
from config.config import service_config as config

mdb.connect(
    db=config.mongodb.database,
    host=config.mongodb.URL,
    username=config.mongodb.login,
    password=config.mongodb.password,
    authentication_source="admin",
    ssl=config.mongodb.TLS.enabled,
    ssl_ca_certs=config.mongodb.TLS.cert_file
)


class SneakerBrand(mdb.Document):
    unique_id = mdb.StringField(db_field="uniqueid")
    name = mdb.StringField()
    logo = mdb.StringField()
    hero = mdb.StringField()
    description = mdb.StringField()
    meta = {"collection": config.mongodb.brands_collection}


class SneakerModel(mdb.Document):
    unique_id = mdb.StringField(db_field="uniqueid")
    name = mdb.StringField()
    hero = mdb.StringField()
    description = mdb.StringField()
    meta = {"collection": config.mongodb.models_collection}


class SneakerReference(mdb.Document):
    unique_id = mdb.StringField(db_field="uniqueid")
    manufacture_sku = mdb.StringField(db_field="manufacturesku")
    brand_name = mdb.StringField(db_field="brandname")
    model_name = mdb.StringField(db_field="modelname")
    base_model_name = mdb.StringField(db_field="basemodelname")
    brand = mdb.StringField()
    model = mdb.StringField()
    base_model = mdb.StringField(db_field="basemodel")
    description = mdb.StringField()
    release_date = mdb.DateField("releasedate")
    release_strdate = mdb.StringField()
    color = mdb.StringField()
    gender = mdb.StringField()
    nickname = mdb.StringField()
    price = mdb.DecimalField()
    materials = mdb.ListField()
    categories = mdb.ListField()
    image_link = mdb.StringField(db_field="imagelink")
    image_links = mdb.ListField(db_field="imagelinks")
    stadium_url = mdb.StringField(db_field="stadiumurl")
    meta = {"collection": config.mongodb.collection, "strict": False}

    def generate_id(self):
        re_id = re.compile(r"[\n\t\s;,.()\\/]")
        model_id = re_id.sub("-", self.model_name)
        sku_id = re_id.sub("-", self.manufacture_sku)
        self.unique_id = f"{model_id}_{sku_id}".lower()


def save_records(records: List[SneakerReference]) -> bool:
    return len(SneakerReference.objects.insert(records)) > 0
