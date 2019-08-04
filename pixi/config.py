import os
from configparser import ConfigParser

from pixi import CONFIG_DIR
from pixi.errors import InvalidConfig

_CONFIG_VALUES = {
    'download_directory': None,
}


class Config:
    """
    A singleton that returns the same ConfigParser instance when
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
        raise InvalidConfig('Config file is empty.')

    try:
        dl_dir = config['pixi']['download_directory']
        if not os.path.isdir(dl_dir) or not os.access(dl_dir, os.W_OK):
            raise InvalidConfig(
                'Download directory does not exist or is not writeable.'
            )
    except KeyError:
        raise InvalidConfig('Config file does not specify download directory.')
