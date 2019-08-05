from pathlib import Path

import click
import mock
import pytest
from click.testing import CliRunner

from pixi.database import (
    Migration,
    _find_migrations,
    _get_version,
    calculate_migrations_needed,
    confirm_database_is_updated,
    create_database_if_nonexistent,
    database,
)


def test_database_contextmanager(monkeypatch):
    with CliRunner().isolated_filesystem():
        monkeypatch.setattr(
            'pixi.database.DATABASE_PATH', Path.cwd() / 'db.sqlite3'
        )
        with database() as (conn, cursor):
            cursor.execute('CREATE TABLE ham(id INTEGER PRIMARY KEY)')
            cursor.execute('INSERT INTO ham (id) VALUES (1)')
            conn.commit()
            cursor.execute('SELECT id FROM ham')
            assert cursor.fetchone()[0] == 1


def test_create_nonexistent_database(monkeypatch):
    with CliRunner().isolated_filesystem():
        monkeypatch.setattr(
            'pixi.database.DATABASE_PATH', Path.cwd() / 'db.sqlite3'
        )
        create_database_if_nonexistent()
        with database() as (conn, cursor):
            cursor.execute('SELECT version FROM versions')


@mock.patch('pixi.database.calculate_migrations_needed')
def test_confirm_db_updated_true(calculate):
    calculate.return_value = False
    confirm_database_is_updated()


@mock.patch('pixi.database.calculate_migrations_needed')
def test_confirm_db_updated_false(calculate):
    calculate.return_value = True
    with pytest.raises(SystemExit):
        confirm_database_is_updated()


@mock.patch('pixi.database.calculate_migrations_needed')
@mock.patch('pixi.database.sys')
def test_confirm_db_updated_updating(sys, calculate):
    sys.argv = ['pixi', 'migrate']
    calculate.return_value = True
    confirm_database_is_updated()


@mock.patch('pixi.database._get_version')
@mock.patch('pixi.database._find_migrations')
def test_calculate_migrations_needed(find_migrations, get_version):
    mig1 = Migration(path='', version=1)
    mig2 = Migration(path='', version=2)
    mig3 = Migration(path='', version=3)
    mig4 = Migration(path='', version=4)
    find_migrations.return_value = [mig3, mig4, mig2, mig1]
    get_version.return_value = 1

    assert list(calculate_migrations_needed()) == [mig2, mig3, mig4]


def test_find_migrations(monkeypatch):
    with CliRunner().isolated_filesystem():
        monkeypatch.setattr('pixi.database.MIGRATIONS_DIR', Path.cwd())
        (Path.cwd() / '00001.sql').touch()
        (Path.cwd() / '00002.sql').touch()
        (Path.cwd() / '00003.sql').touch()
        (Path.cwd() / '00004.sql').touch()
        (Path.cwd() / '00005.sql').touch()
        assert len(_find_migrations()) == 5


def test_find_invalid_migration_name(monkeypatch):
    with CliRunner().isolated_filesystem():
        monkeypatch.setattr('pixi.database.MIGRATIONS_DIR', Path.cwd())
        (Path.cwd() / '00001.sql').touch()
        (Path.cwd() / 'hello.sql').touch()
        (Path.cwd() / '00003.sql').touch()
        with pytest.raises(click.Abort):
            _find_migrations()


def test_get_version(monkeypatch):
    with CliRunner().isolated_filesystem():
        monkeypatch.setattr(
            'pixi.database.DATABASE_PATH', Path.cwd() / 'db.sqlite3'
        )
        with database() as (conn, cursor):
            cursor.execute(
                'CREATE TABLE versions (version INTEGER PRIMARY KEY)'
            )
            cursor.execute('INSERT INTO versions (version) VALUES (83)')
            conn.commit()

        assert 83 == _get_version()


def test_get_version_empty_table(monkeypatch):
    with CliRunner().isolated_filesystem():
        monkeypatch.setattr(
            'pixi.database.DATABASE_PATH', Path.cwd() / 'db.sqlite3'
        )
        with database() as (conn, cursor):
            cursor.execute(
                'CREATE TABLE versions (version INTEGER PRIMARY KEY)'
            )
            conn.commit()

        assert 0 == _get_version()
