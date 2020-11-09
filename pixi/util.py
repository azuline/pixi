import os
import re
from urllib import parse

import click
from pixivapi import BadApiResponse, Size
from requests import RequestException

from pixi.database import database
from pixi.errors import DownloadFailed, DuplicateImage, InvalidURL, PixiError


def parse_id(string, path=None, param=None):
    try:
        return int(string)
    except ValueError:
        pass

    if path and param:
        try:
            split = parse.urlsplit(string)
            if split.netloc == "www.pixiv.net" and split.path == path:
                return int(dict(parse.parse_qsl(split.query))[param])
        except (KeyError, TypeError):
            pass

    raise InvalidURL


def rename_duplicate_file(path):
    new_path = path
    dupe_number = 1
    while new_path.exists():
        name, ext = os.path.splitext(path.name)
        new_path = path.with_name(f"{name} ({dupe_number}){ext}")
        dupe_number += 1
    return new_path


def format_filename(id_, title):
    return re.sub(r'[:\?<>\\*\|"\/]', "_", f"{id_}. {title}")


def resolve_track_download(track_download, directory):
    if track_download is None:
        return not directory
    return track_download


def download_image(
    illustration,
    directory,
    tries=1,
    allow_duplicate=False,
    track_download=True,
):
    if not allow_duplicate:
        try:
            check_duplicate(illustration.id)
        except DuplicateImage:
            return click.echo(
                f"{illustration.id}. {illustration.title} has been downloaded "
                "previously, skipping..."
            )

    for attempt in range(tries):
        try:
            filename = format_filename(illustration.id, illustration.title)

            if illustration.meta_pages:
                click.echo(
                    "Downloading multi-page illustration "
                    f"{illustration.id}. {illustration.title}."
                )
            else:
                click.echo(
                    f"Downloading illustration {illustration.id}. "
                    f"{illustration.title}."
                )

            illustration.download(
                directory=directory,
                size=Size.ORIGINAL,
                filename=filename,
            )

            click.echo()
            clear_failed(illustration.id)
            if track_download:
                record_download(illustration.id, str(directory))

            break
        except (BadApiResponse, RequestException) as e:
            click.echo(
                f"Failed to download illustration {illustration.id}. "
                f"{illustration.title} ({e}). Attempting to re-download "
                f"(attempt {attempt + 1})."
            )
    else:
        mark_failed(illustration)
        raise DownloadFailed


def download_pages(
    get_next_response,
    starting_offset,
    directory,
    allow_duplicates=False,
    track_download=True,
    start_page=1,
):
    response = get_next_response(starting_offset)
    if not response["illustrations"]:
        raise PixiError("No illustrations found.")

    page = start_page
    while True:
        click.echo(f"Downloading page {page} of illustrations.\n")
        for illustration in response["illustrations"]:
            try:
                download_image(
                    illustration,
                    directory=directory,
                    tries=3,
                    allow_duplicate=allow_duplicates,
                    track_download=(resolve_track_download(track_download, directory)),
                )
            except DownloadFailed:
                click.echo(
                    f"Failed to download image {illustration.id}. "
                    f"{illustration.title} three times. Skipping..."
                )

        if not response["next"]:
            break

        response = get_next_response(response["next"])
        page += 1


def mark_failed(illustration):
    with database() as (conn, cursor):
        cursor.execute(
            """
            INSERT OR IGNORE INTO failed (id, artist, title) VALUES (?, ?, ?)
            """,
            (
                illustration.id,
                illustration.user.account,
                illustration.title,
            ),
        )
        conn.commit()


def clear_failed(illustration_id):
    with database() as (conn, cursor):
        cursor.execute(
            """
            DELETE FROM failed WHERE id = ?
            """,
            (illustration_id,),
        )
        conn.commit()


def record_download(illustration_id, path):
    with database() as (conn, cursor):
        cursor.execute(
            """
            INSERT OR IGNORE INTO downloaded (id, path) VALUES (?, ?)
            """,
            (
                illustration_id,
                path,
            ),
        )
        conn.commit()


def check_duplicate(illustration_id):
    with database() as (conn, cursor):
        cursor.execute(
            """
            SELECT path FROM downloaded WHERE id = ?
            """,
            (illustration_id,),
        )
        row = cursor.fetchone()
        if row:
            raise DuplicateImage(row["path"])
