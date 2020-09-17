import os
import yaml

CONFIG_PATH = os.environ.get("CONFIG_PATH") or "config/config.dev.yaml"


class Config:
    def __init__(self, config, subconfig):
        self._config = config[subconfig]

    def try_get_property(self, key: str):
        try:
            return self._config[key]
        except:
            return None


class Configs:
    def __init__(self, config, subconfig, index):
        self._config = config[subconfig][index]

    def try_get_property(self, key: str):
        try:
            return self._config[key]
        except:
            return None


class CommonConfig(Config):
    def __init__(self, config):
        Config.__init__(self, config, "commonConfig")
        self.backup_path = self.try_get_property("backupPath")
        self.image_storage_path = self.try_get_property("imageStoragePath")
        self.min_pause_time = self.try_get_property("minPauseTime")
        self.max_pause_time = self.try_get_property("maxPauseTime")
        self.api_host = self.try_get_property("apiHost")
        self.api_port = self.try_get_property("apiPort")


class TargetConfig(Configs):
    def __init__(self, config, index):
        Configs.__init__(self, config, "targetConfig", index)
        self.host = self.try_get_property("host")
        self.releases_url = self.try_get_property("releasesURL")
        self.sign_in_url = self.try_get_property("signInURL")
        self.search_url = self.try_get_property("searchURL")
        self.login = self.try_get_property("login")
        self.password = self.try_get_property("password")


class TLSConfig(Config):
    def __init__(self, config):
        Config.__init__(self, config, "TLS")
        self.enabled = self.try_get_property("enableTLS")
        self.cert_file = self.try_get_property("certFile")
        self.key_file = self.try_get_property("keyFile")


class MongoConfig(Config):
    def __init__(self, config):
        Config.__init__(self, config, "mongoConfig")
        self.URL = self.try_get_property("URL")
        self.TLS = TLSConfig(self._config)
        self.database = self.try_get_property("database")
        self.collection = self.try_get_property("collection")
        self.brands_collection = self.try_get_property("brandCollection")
        self.models_collection = self.try_get_property("modelCollection")
        self.login = self.try_get_property("login")
        self.password = self.try_get_property("password")


class ServiceConfig:
    def __init__(self, config):
        self.common = CommonConfig(config)
        self.stadium_goods = TargetConfig(config, 0)
        self.goat = TargetConfig(config, 1)
        self.mongodb = MongoConfig(config)


with open(CONFIG_PATH) as stream:
    parsed = yaml.load(stream, Loader=yaml.Loader)
service_config = ServiceConfig(config=parsed)
