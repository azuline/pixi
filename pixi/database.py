import logging
import sqlite3
import sys
from collections import namedtuple
from contextlib import contextmanager
from pathlib import Path

import click

from pixi import DATA_DIR

logger = logging.getLogger(__name__)
Migration = namedtuple('Migration', 'path, version')

DATABASE_PATH = DATA_DIR / 'db.sqlite3'
MIGRATIONS_DIR = Path(__file__).parent / 'migrations'


@contextmanager
def database():
    with sqlite3.connect(str(DATABASE_PATH)) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        yield conn, cursor
        cursor.close()


def create_database_if_nonexistent():
    with database() as (conn, cursor):
        cursor.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='versions'
            """
        )
        if not cursor.fetchone():
            cursor.execute(
                """
                CREATE TABLE versions (
                    version INTEGER,
                    PRIMARY KEY (version)
                )
                """
            )
            conn.commit()


def confirm_database_is_updated():
    if calculate_migrations_needed():
        if not len(sys.argv) == 2 or sys.argv[1] != 'migrate':
            click.echo('The database needs to be migrated.')
            click.echo('Run `pixi migrate`.')
            sys.exit(1)


def calculate_migrations_needed():
    migrations = _find_migrations()
    version = _get_version()

    needed = []
    for mig in migrations:
        if mig.version > version:
            needed.append(mig)
    return sorted(needed, key=lambda m: m.version)


def _find_migrations():
    migrations = []
    for sql_path in [
        f for f in MIGRATIONS_DIR.listdir() if f.endswith('.sql')
    ]:
        try:
            migrations.append(
                Migration(path=sql_path, version=int(sql_path.stem))
            )
        except TypeError:
            click.echo(f'Invalid migration name: {sql_path}.')
            raise click.Abort
    return migrations


def _get_version():
    with database() as (conn, cursor):
        cursor.execute('SELECT MAX(version) FROM versions')
        return cursor.fetchone()[0] or 0
