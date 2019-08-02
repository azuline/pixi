from urllib import parse

from pixi.errors import InvalidURL


def parse_id_from_url(url):
    query = parse.urlsplit(url).query
    try:
        return int(dict(parse.parse_qsl(query))['illust_id'])
    except (KeyError, TypeError):
        raise InvalidURL
