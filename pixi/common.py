import os
from urllib import parse

from pixi.errors import InvalidURL


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


def check_duplicate(path):
    new_path = path
    dupe_number = 1
    while new_path.exists():
        name, ext = os.path.splitext(path.name)
        new_path = path.with_name(f'{name} ({dupe_number}){ext}')
        dupe_number += 1
    return new_path


def format_filename(id_, title):
    return f'{id_}. {title}'
