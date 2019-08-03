from configparser import ConfigParser

from pixi import CONFIG_DIR
from pixi.errors import InvalidConfig

_CONFIG_VALUES = {
    'download_directory': None,
    'filename_format': None,
}


class Config:
    """
    A singleton that returns the same instance when instantiated.
    """

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
        return cls.__instance

    def __init__(self):
        self.config = _load_config()
        if not _validate_config(self.config):
            raise InvalidConfig


def _load_config():
    config = ConfigParser()
    config.read(CONFIG_DIR / 'config.ini')
    return config


def _validate_config(config):
    return False
