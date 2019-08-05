from pathlib import Path

import click
from appdirs import user_config_dir, user_data_dir

from pixi.errors import PixiError

CONFIG_DIR = Path(user_config_dir('pixi', 'azuline'))
DATA_DIR = Path(user_data_dir('pixi', 'azuline'))


@click.group()
def commandgroup():
    pass


def make_app_directories():
    for name, dir_ in [('configuration', CONFIG_DIR), ('data', DATA_DIR)]:
        try:
            dir_.mkdir(mode=0o700, parents=True, exist_ok=True)
        except PermissionError:  # pragma: no cover
            raise PixiError(f'Could not create {name} directory.')
