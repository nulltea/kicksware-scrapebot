import yaml


class CommonConfig:
    def __init__(self, config):
        self._config = config["commonConfig"]
        self.selenium_path = self._config["seleniumPath"]


class TargetConfig:
    def __init__(self, config):
        self._config = config["targetConfig"]
        self.host = self._config["host"]
        self.releases_url = self._config["releasesURL"]
        self.sign_in_url = self._config["signInURL"]
        self.search_url = self._config["searchURL"]


class TLSConfig:
    def __init__(self, config):
        self._config = config["TLS"]
        self.enabled = self._config["enableTLS"]
        self.cert_file = self._config["certFile"]
        self.key_file = self._config["keyFile"]


class MongoConfig:
    def __init__(self, config):
        self._config = config["mongoConfig"]
        self.URL = self._config["URL"]
        self.TLS = TLSConfig(self._config)
        self.database = self._config["database"]
        self.collection = self._config["collection"]
        self.brands_collection = self._config["brandCollection"]
        self.models_collection = self._config["modelCollection"]
        self.login = self._config["login"]
        self.password = self._config["password"]


class ServiceConfig:
    def __init__(self, config):
        self.common = CommonConfig(config)
        self.target = TargetConfig(config)
        self.mongodb = MongoConfig(config)


with open("config/config.dev.yaml") as stream:
    parsed = yaml.load(stream, Loader=yaml.Loader)
service_config = ServiceConfig(config=parsed)
