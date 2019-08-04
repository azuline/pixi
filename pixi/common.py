from urllib import parse

from pixivapi import LoginError

from pixi.client import Client
from pixi.config import Config
from pixi.errors import GoAuthenticate, InvalidURL


def get_client():
    config = Config()
    if not config['pixi']['refresh_token']:
        raise GoAuthenticate

    client = Client()

    try:
        client.authenticate(config['pixi']['refresh_token'])
    except LoginError:
        raise GoAuthenticate

    return client


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


def format_filename(id_, title):
    return f'{id_}. {title}'
