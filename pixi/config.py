import os
from configparser import ConfigParser

from pixi import CONFIG_DIR
from pixi.errors import InvalidConfig, PixiError

CONFIG_PATH = CONFIG_DIR / 'config.ini'

DEFAULT_CONFIG = {
    'pixi': {
        'download_directory': '',
        'refresh_token': '',
    },
}


def make_config_directory():
    try:
        CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    except PermissionError:  # pragma: no cover
        raise PixiError('Could not create configuration directory.')


def write_default_config():
    if not CONFIG_PATH.exists():
        parser = ConfigParser()
        parser.read_dict(DEFAULT_CONFIG)
        with CONFIG_PATH.open('w') as f:
            parser.write(f)


class Config:
    """
    A "proxy singleton" that returns the same ConfigParser instance when
    instantiated.
    """

    __parser = None

    def __new__(cls, validate=True):
        if cls.__parser is None:
            cls.__parser = _load_config()
            if validate:
                _validate_config(cls.__parser)
        return cls.__parser


def _load_config():
    ConfigParser.save = _save_config
    config = ConfigParser()
    config.read(CONFIG_DIR / 'config.ini')
    return config


def _save_config(parser):
    with CONFIG_PATH.open('w') as f:
        parser.write(f)


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
