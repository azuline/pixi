from math import ceil

from pixivapi import Client as BaseClient
from pixivapi import LoginError
from tqdm import tqdm

from pixi.common import check_duplicate
from pixi.config import Config
from pixi.errors import GoAuthenticate


class Client:
    """
    A "proxy singleton" that returns the same PixivClient instance when
    instantiated.
    """

    __pixiv_client = None

    def __new__(cls, authenticate=True):
        if cls.__pixiv_client is None:
            cls.__pixiv_client = _PixivClient(authenticate)
        return cls.__pixiv_client


class _PixivClient(BaseClient):
    """
    A Pixiv client that downloads with progress bars!
    """

    def __init__(self, authenticate=True):
        super().__init__()

        if authenticate:
            config = Config()
            if not config['pixi']['refresh_token']:
                raise GoAuthenticate

            try:
                self.authenticate(config['pixi']['refresh_token'])
            except LoginError:
                raise GoAuthenticate

    def download(self, url, destination, referer='https://pixiv.net'):
        response = self.session.get(
            url, headers={'Referer': referer}, stream=True
        )

        destination = check_duplicate(destination)
        with destination.open('wb') as f:
            for chunk in tqdm(
                iterable=response.iter_content(chunk_size=1024),
                total=ceil(int(response.headers['Content-Length']) / 1024),
            ):
                f.write(chunk)
