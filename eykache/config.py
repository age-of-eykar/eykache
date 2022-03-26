import toml
import os
import shutil


class Config:
    def __init__(self) -> None:
        self.file = self._extract_config("config.toml", "config.template.toml")
        self.config = toml.load(self.file)

    @property
    def endpoint(self) -> str:
        return self.config["api"]["endpoint"]

    @property
    def database(self) -> str:
        return self.config["database"]["database"]

    @property
    def user(self) -> str:
        return self.config["database"]["user"]

    @property
    def password(self) -> str:
        return self.config["database"]["password"]

    @property
    def host(self) -> str:
        return self.config["database"]["host"]

    @property
    def db_port(self) -> str:
        return self.config["database"]["host"]

    @property
    def chain_id(self) -> str:
        return self.config["api"]["chain_id"]

    @property
    def from_block(self) -> str:
        return self.config["api"]["from_block"]

    @property
    def page_size(self) -> str:
        return self.config["api"]["page_size"]

    @property
    def port(self) -> str:
        return self.config["server"]["port"]

    @property
    def request_max_size(self) -> str:
        return self.config["server"]["request_max_size"]

    @property
    def contract(self) -> str:
        return self.config["eykar"]["contract"]

    def _get_path(self, name: str) -> str:
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

    def _extract_config(self, file_name: str, template_name: str):
        config_file = self._get_path(file_name)
        if not os.path.isfile(config_file):
            print(f"config {file_name} doesn't exist, copying template!")
            shutil.copyfile(self._get_path(template_name), config_file)
        return config_file
