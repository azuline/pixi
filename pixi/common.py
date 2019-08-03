from urllib import parse

from pixivapi import Client, LoginError

from pixi import CONFIG_DIR
from pixi.config import Config
from pixi.errors import GoAuthenticate, InvalidURL, PixiError


def get_client():
    config = Config()
    client = Client()

    if not config['refresh_token']:
        raise GoAuthenticate

    try:
        client.authenticate(config['refresh_token'])
    except LoginError as e:
        raise GoAuthenticate from e


def make_config_directory():
    try:
        CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)
    except FileNotFoundError:
        raise PixiError('Could not create configuration directory.')


def parse_id(string, path=None, param=None):
    try:
        return int(string)
    except ValueError:
        pass

    if path and param:
        try:
            split = parse.urlsplit(string)
            if split.netloc == 'www.pixiv.net' and split.path == path:
                return int(dict(parse.parse_qsl(split.query))[param])
        except (KeyError, TypeError):
            pass

    raise InvalidURL
