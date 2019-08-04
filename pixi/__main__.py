import traceback

import click

import pixi.commands  # noqa
from pixi import commandgroup
from pixi.config import make_config_directory, write_default_config
from pixi.errors import DownloadError, GoAuthenticate, InvalidConfig, PixiError


def run():
    try:
        make_config_directory()
        write_default_config()
        commandgroup()
    except GoAuthenticate:
        click.echo('Invalid token. Re-authenticate with `pixi auth`.')
    except InvalidConfig as e:
        click.echo(f'Invalid config: {e}. Edit the config with `pixi config`.')
    except DownloadError:
        click.echo('Failed to download image.\n')
        traceback.print_exc()
    except PixiError as e:
        click.echo(e)


run()
