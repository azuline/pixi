import click
from pixivapi import Client, LoginError

from pixi import commandgroup
from pixi.common import get_client, parse_id
from pixi.config import CONFIG_PATH, Config
from pixi.errors import PixiError


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
def image(image):
    """Download an image by URL or ID."""
    client = get_client()
    illustration_id = parse_id(
        string=image,
        path='/member_illust.php',
        param='illust_id',
    )
    illustration = client.fetch_illustration(illustration_id)
    illustration.download()
