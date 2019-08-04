from pathlib import Path

import click
from pixivapi import BadApiResponse, Client, LoginError, Size
from requests import RequestException

from pixi import commandgroup
from pixi.common import format_filename, get_client, parse_id
from pixi.config import CONFIG_PATH, Config
from pixi.errors import DownloadError, PixiError


@commandgroup.command()
@click.option('--username', '-u', prompt='Username')
@click.option('--password', '-p', prompt='Password', hide_input=True)
def auth(username, password):
    """Log into Pixiv and generate a refresh token."""
    client = Client()

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
@click.argument('image', nargs=1)
@click.option(
    '--directory', '-d',
    type=click.Path(exists=True, file_okay=False),
    help='Config override for download directory.'
)
def image(image, directory):
    """Download an image by URL or ID."""
    client = get_client()
    illustration_id = parse_id(
        string=image,
        path='/member_illust.php',
        param='illust_id',
    )

    try:
        illustration = client.fetch_illustration(illustration_id)
        directory = Path(directory or Config()['pixi']['download_directory'])
        filename = format_filename(illustration.id, illustration.title)

        if illustration.meta_pages:
            click.echo(
                'Downloading multi-page illustration '
                f'{illustration_id}. {illustration.title}.\n'
            )
        else:
            click.echo(
                f'Downloading illustration {illustration_id}. '
                f'{illustration.title}.\n'
            )

        illustration.download(
            directory=directory,
            size=Size.ORIGINAL,
            filename=filename,
        )
    except (BadApiResponse, RequestException) as e:
        raise DownloadError from e
