from pathlib import Path

import click
from appdirs import user_config_dir

CONFIG_DIR = Path(user_config_dir('pixi', 'azuline'))


@click.group()
def commandgroup():
    pass
