import click

from pixi import commandgroup
from pixi.common import make_config_directory
from pixi.config import write_default_config_if_doesnt_exist
from pixi.errors import GoAuthenticate, InvalidConfig, PixiError


def run():
    try:
        make_config_directory()
        write_default_config_if_doesnt_exist()
        commandgroup()
    except PixiError as e:
        click.echo(e)
    except GoAuthenticate:
        click.echo('Invalid token. Re-authenticate with `pixi auth`.')
    except InvalidConfig as e:
        click.echo(f'Invalid config: {e}. Edit the config with `pixi config`.')


run()
