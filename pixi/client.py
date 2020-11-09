from math import ceil

from pixivapi import Client as BaseClient
from pixivapi import LoginError
from tqdm import tqdm

from pixi.config import Config
from pixi.errors import GoAuthenticate
from pixi.util import rename_duplicate_file


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
            if not config["pixi"]["refresh_token"]:
                raise GoAuthenticate

            try:
                self.authenticate(config["pixi"]["refresh_token"])
            except LoginError:
                raise GoAuthenticate

    def download(self, url, destination, referer="https://pixiv.net"):
        response = self.session.get(url, headers={"Referer": referer}, stream=True)
        destination = rename_duplicate_file(destination)

        try:
            total = ceil(int(response.headers["Content-Length"]) / 16384)
        except (KeyError, ValueError):
            total = None

        try:
            with destination.open("wb") as f:
                for chunk in tqdm(
                    iterable=response.iter_content(chunk_size=16384),
                    total=total,
                    unit="KB",
                    unit_scale=True,
                ):
                    f.write(chunk)
        except:  # noqa E722
            destination.unlink()
            raise
