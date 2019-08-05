import traceback

import click

import pixi.commands  # noqa
from pixi import commandgroup, make_app_directories
from pixi.config import write_default_config
from pixi.database import (
    confirm_database_is_updated,
    create_database_if_nonexistent,
)
from pixi.errors import (
    DownloadFailed,
    GoAuthenticate,
    InvalidConfig,
    PixiError,
)


def run():
    try:
        make_app_directories()
        write_default_config()
        create_database_if_nonexistent()
        confirm_database_is_updated()
        commandgroup()
    except GoAuthenticate:
        click.echo('Invalid token. Re-authenticate with `pixi auth`.')
    except InvalidConfig as e:
        click.echo(f'Invalid config: {e}. Edit the config with `pixi config`.')
    except DownloadFailed:
        click.echo('Failed to download image.\n')
        traceback.print_exc()
    except PixiError as e:
        click.echo(e)


run()
