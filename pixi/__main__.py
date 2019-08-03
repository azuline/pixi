import click

from pixi import commandgroup
from pixi.common import make_config_directory
from pixi.errors import GoAuthenticate, InvalidConfig

make_config_directory()

try:
    commandgroup()
except GoAuthenticate:
    click.echo(
        'Invalid authorization. Generate a new refresh token with '
        '`pixi auth`.'
    )
except InvalidConfig as e:
    click.echo(
        'Invalid configuration. Edit and fix the configuration with '
        '`pixi config`.'
    )
    click.echo(f'Error: {e}')
