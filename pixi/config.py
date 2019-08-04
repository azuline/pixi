import os
from configparser import ConfigParser

from pixi import CONFIG_DIR
from pixi.errors import InvalidConfig

CONFIG_PATH = CONFIG_DIR / 'config.ini'

DEFAULT_CONFIG = """
[pixi]
download_directory =
refresh_token =
"""


def write_default_config_if_doesnt_exist():
    if not CONFIG_PATH.exists():
        with CONFIG_PATH.open('w') as f:
            f.write(DEFAULT_CONFIG)


class Config:
    """
    A "proxy singleton" that returns the same ConfigParser instance when
    instantiated.
    """

    __config = None

    def __new__(cls):
        if cls.__config is None:
            cls.__config = _load_config()
            _validate_config(cls.__config)
        return cls.__config


def _load_config():
    config = ConfigParser()
    config.read(CONFIG_DIR / 'config.ini')
    return config


def _validate_config(config):
    if not config:
        raise InvalidConfig('Empty file')

    try:
        dl_dir = config['pixi']['download_directory']
        if not os.path.isdir(dl_dir) or not os.access(dl_dir, os.W_OK):
            raise InvalidConfig(
                'Download directory does not exist or is not writeable'
            )
    except KeyError:
        raise InvalidConfig('Download directory not configured')
