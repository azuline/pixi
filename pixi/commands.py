import functools

import click
from pixivapi import BadApiResponse, LoginError
from requests import RequestException

from pixi import commandgroup
from pixi.client import Client
from pixi.common import download_image, parse_id
from pixi.config import CONFIG_PATH, Config
from pixi.errors import DownloadFailed, PixiError

SHARED_OPTIONS = [
    click.option(
        '--directory', '-d',
        type=click.Path(exists=True, file_okay=False),
        help='Config override for download directory.'
    ),
    click.option(
        '--ignore-duplicates', '-i',
        is_flag=True,
        default=False,
        help='Downloads illustrations even if previously downloaded.',
    ),
]


def shared_options(func):
    for decorator in SHARED_OPTIONS:
        func = functools.wraps(func)(decorator(func))
    return func


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
@click.argument(
    'illustration',
    nargs=1,
    callback=lambda ctx, param, value: (
        parse_id(value, path='/member_illust.php', param='illust_id')
    ),
)
@shared_options
def illust(illustration, directory, ignore_duplicates):
    """Download an illustration by URL or ID."""
    try:
        download_image(
            Client().fetch_illustration(illustration),
            directory=directory,
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
@click.option(
    '--page', '-p',
    nargs=1,
    type=click.INT,
    default=1,
    help='Page of artist\'s works to start downloading on.',
)
@shared_options
def artist(artist, page, directory, ignore_duplicates):
    """Download illustrations of an artist by URL or ID."""
    client = Client()
    response = client.fetch_user_illustrations(artist, offset=(page - 1) * 30)
    if not response['illustrations']:
        raise PixiError('No illustrations found.')

    while response['next']:
        click.echo(
            f'Downloading page {response["next"] // 30} of illustrations.\n'
        )
        for illustration in response['illustrations']:
            try:
                download_image(illustration, directory=directory, tries=3)
            except DownloadFailed:
                click.echo(
                    f'Failed to download image {illustration.id}. '
                    f'{illustration.title} three times. Skipping...'
                )

        if response['next']:
            response = client.fetch_user_illustrations(
                artist, offset=response['next']
            )

    click.echo(f'Finished downloading artist {artist}.')


@commandgroup.command()
@click.option(
    '--user', '-u',
    help='The user whose bookmarks to download. Default logged in account.',
    callback=lambda ctx, param, value: (
        parse_id(value, path='/member.php', param='id')
    ),
)
@click.option(
    '--visibility', '-v',
    type=click.Choice(['public', 'private']),
    help=(
        'The visibility of the bookmarks that should be downloaded. '
        'Leave blank to download all.'
    ),
)
@click.option(
    '--tag', '-t',
    help='The bookmark tag to filter bookmarks by.',
)
@shared_options
def bookmark(user, visibility, tag, directory, ignore_duplicates):
    """Download illustrations bookmarked by a user."""
    pass


@commandgroup.command()
def failed():
    """View illustrations that failed to download."""
    pass


@commandgroup.command()
@click.option(
    '--table', '-t',
    type=click.Choice(['downloads', 'failed']),
    help='Which table to delete; leave blank to wipe everything.'
)
def wipe():
    """Wipe the saved history of downloaded illustrations."""
    pass
