import os
from math import ceil

from pixivapi import Client as BaseClient
from tqdm import tqdm


class Client(BaseClient):
    """
    A Pixiv client that downloads with progress bars!
    """

    def download(self, url, destination, referer='https://pixiv.net'):
        response = self.session.get(
            url, headers={'Referer': referer}, stream=True
        )

        destination = check_duplicate(destination)

        with destination.open('wb') as f:
            """
            with click.progressbar(
                iterable=response.iter_content(chunk_size=1024),
                length=ceil(int(response.headers['Content-Length']) / 1024),
                label=destination.name,
                show_percent=True,
            ) as bar:
            """
            for chunk in tqdm(
                iterable=response.iter_content(chunk_size=1024),
                total=ceil(int(response.headers['Content-Length']) / 1024),
            ):
                f.write(chunk)


def check_duplicate(path):
    new_path = path
    dupe_number = 1
    while new_path.exists():
        name, ext = os.path.splitext(path.name)
        new_path = path.with_name(f'{name} ({dupe_number}){ext}')
        dupe_number += 1
    return new_path
