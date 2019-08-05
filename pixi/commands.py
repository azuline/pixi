import sys

import click
from pixivapi import BadApiResponse, LoginError, Visibility
from requests import RequestException

from pixi import commandgroup
from pixi.client import Client
from pixi.config import CONFIG_PATH, Config
from pixi.database import calculate_migrations_needed, database
from pixi.errors import DownloadFailed, PixiError
from pixi.options import (
    download_directory,
    ignore_duplicates,
    page,
    track_download,
    visibility,
)
from pixi.util import (
    download_image,
    download_pages,
    parse_id,
    resolve_track_download,
)


@commandgroup.command()
@click.option('--username', '-u', prompt='Username')
@click.option('--password', '-p', prompt='Password', hide_input=True)
def auth(username, password):
    """Log into Pixiv and generate a refresh token."""
    client = Client(authenticate=False)

    try:
        client.login(username, password)
    except LoginError:
        raise PixiError('Invalid credentials.')

    config = Config(validate=False)
    config['pixi']['refresh_token'] = client.refresh_token
    config.save()

    click.echo('Successfully authenticated; token written to config.')


@commandgroup.command()
def config():
    """Edit the config file."""
    with CONFIG_PATH.open('r+') as f:
        text = click.edit(f.read())
        if text:
            f.seek(0)
            f.truncate(0)
            f.write(text)
            click.echo('Edit completed.')
        else:
            click.echo('Edit aborted.')


@commandgroup.command()
def migrate():
    """Upgrade the database to the latest migration."""
    migrations_needed = calculate_migrations_needed()

    if not migrations_needed:
        click.echo('Database is up to date.')
        sys.exit(1)

    with database() as (conn, cursor):
        for mig in migrations_needed:
            with mig.path.open() as sql:
                cursor.executescript(sql.read())
                cursor.execute(
                    'INSERT INTO versions (version) VALUES (?)',
                    (mig.version, ),
                )
            conn.commit()


@commandgroup.command()
@click.argument(
    'illustration',
    nargs=1,
    callback=lambda ctx, param, value: (
        parse_id(value, path='/member_illust.php', param='illust_id')
    ),
)
@download_directory
@ignore_duplicates
@track_download
def illust(illustration, directory, ignore_duplicates, track):
    """Download an illustration by URL or ID."""
    try:
        download_image(
            Client().fetch_illustration(illustration),
            directory=directory,
            ignore_duplicate=ignore_duplicates,
            track_download=resolve_track_download(track_download, directory),
        )
    except (BadApiResponse, RequestException) as e:
        raise DownloadFailed from e


@commandgroup.command()
@click.argument(
    'artist',
    nargs=1,
    callback=lambda ctx, param, value: (
        parse_id(value, path='/member.php', param='id')
    ),
)
@page
@download_directory
@ignore_duplicates
@track_download
def artist(artist, page, directory, ignore_duplicates, track):
    """Download illustrations of an artist by URL or ID."""
    client = Client()

    def get_next_response(offset):
        return client.fetch_user_illustrations(artist, offset=offset)

    download_pages(
        get_next_response,
        starting_offset=(page - 1) * 30,
        directory=directory,
        ignore_duplicates=ignore_duplicates,
        track_download=track,
    )

    click.echo(f'Finished downloading artist {artist}.')


@commandgroup.command()
@click.option(
    '--user', '-u',
    help='The user whose bookmarks to download. Default logged in account.',
    callback=lambda ctx, param, value: (
        parse_id(value, path='/member.php', param='id') if value else None
    ),
)
@click.option(
    '--tag', '-t',
    help='The bookmark tag to filter bookmarks by.',
)
@visibility
@page
@download_directory
@ignore_duplicates
@track_download
def bookmarks(
    user, tag, visibility, page, directory, ignore_duplicates, track
):
    """Download illustrations bookmarked by a user."""
    client = Client()

    if visibility:
        visibilities = [Visibility(visibility)]
    else:
        visibilities = [Visibility.PUBLIC, Visibility.PRIVATE]

    for visi in visibilities:
        click.echo(f'Downloading {visi.value} bookmarks.\n')

        def get_next_response(offset):
            return client.fetch_user_bookmarks(
                user_id=user or client.account.id,
                max_bookmark_id=offset,
                visibility=visi,
                tag=tag,
            )

        download_pages(
            get_next_response,
            starting_offset=(page - 1) * 30,
            directory=directory,
            ignore_duplicates=ignore_duplicates,
            track_download=track,
        )

    click.echo(f'Finished downloading artist {artist}.')


@commandgroup.command()
def failed():
    """View illustrations that failed to download."""
    # TODO
    pass


@commandgroup.command()
@click.option(
    '--table', '-t',
    type=click.Choice(['downloads', 'failed']),
    help='Which table to delete; leave blank to wipe everything.'
)
def wipe():
    """Wipe the saved history of downloaded illustrations."""
    # TODO
    pass
