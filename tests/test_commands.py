from pathlib import Path
from shutil import copyfile

import click
import mock
from click.testing import CliRunner
from pixivapi import BadApiResponse, LoginError, Visibility

from pixi.commands import (
    _confirm_table_wipe,
    artist,
    auth,
    bookmarks,
    config,
    failed,
    illust,
    migrate,
    wipe,
)
from pixi.database import Migration, database
from pixi.errors import DownloadFailed, PixiError


@mock.patch('pixi.commands.Config')
@mock.patch('pixi.commands.Client')
def test_auth_failure(client, _):
    client.return_value.login.side_effect = LoginError
    result = CliRunner().invoke(auth, ['-u', 'u', '-p', 'p'])
    assert isinstance(result.exception, PixiError)


@mock.patch('pixi.commands.Config')
@mock.patch('pixi.commands.Client')
def test_auth_success(client, config):
    client.return_value.refresh_token = 'token value'
    config_dict = {'pixi': {}}
    config.return_value = config_dict

    CliRunner().invoke(auth, ['-u', 'u', '-p', 'p'])
    assert config_dict['pixi']['refresh_token'] == 'token value'


@mock.patch('click.edit')
def test_edit_config_completed(edit, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        config_path = Path.cwd() / 'config.ini'
        with config_path.open('w') as f:
            f.write('a bunch of text')

        monkeypatch.setattr('pixi.commands.CONFIG_PATH', config_path)
        edit.return_value = 'text2'
        result = runner.invoke(config)
        assert result.output == 'Edit completed.\n'

        assert edit.called_with('a bunch of text')

        with config_path.open('r') as f:
            assert 'text2' == f.read()


@mock.patch('click.edit')
def test_edit_config_aborted(edit, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        config_path = Path.cwd() / 'config.ini'
        with config_path.open('w') as f:
            f.write('a bunch of text')

        monkeypatch.setattr('pixi.commands.CONFIG_PATH', config_path)
        edit.return_value = None
        result = runner.invoke(config)
        assert result.output == 'Edit aborted.\n'

        with config_path.open('r') as f:
            assert 'a bunch of text' == f.read()


@mock.patch('pixi.commands.calculate_migrations_needed')
def test_migrate(calculate, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        fake_mig = Path.cwd() / '0001.sql'
        with fake_mig.open('w') as f:
            f.write('INSERT INTO test (id) VALUES (29)')

        monkeypatch.setattr(
            'pixi.database.DATABASE_PATH', Path.cwd() / 'db.sqlite3'
        )
        with database() as (conn, cursor):
            cursor.execute('CREATE TABLE test (id INTEGER PRIMARY KEY)')
            cursor.execute(
                'CREATE TABLE versions (version INTEGER PRIMARY KEY)'
            )
            conn.commit()

        calculate.return_value = [Migration(path=fake_mig, version=9)]
        runner.invoke(migrate)

        with database() as (conn, cursor):
            cursor.execute('SELECT version FROM versions')
            assert 9 == cursor.fetchone()[0]
            cursor.execute('SELECT id FROM test')
            assert 29 == cursor.fetchone()[0]


@mock.patch('pixi.commands.calculate_migrations_needed')
def test_migrate_not_needed(calculate, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        monkeypatch.setattr(
            'pixi.database.DATABASE_PATH', Path.cwd() / 'db.sqlite3'
        )
        calculate.return_value = []
        result = runner.invoke(migrate)
        assert isinstance(result.exception, SystemExit)


@mock.patch('pixi.commands.download_image')
@mock.patch('pixi.commands.Client')
@mock.patch('pixi.commands.Config')
def test_illust(_, client, download_image):
    client.return_value.fetch_illustration.return_value = 'Illust!'
    runner = CliRunner()
    with runner.isolated_filesystem():
        runner.invoke(illust, [
            '--directory',
            str(Path.cwd()),
            '--no-track',
            '--allow-duplicates',
            'https://www.pixiv.net/member_illust.php?illust_id=12345',
        ])

        client.return_value.fetch_illustration.assert_called_with(12345)

        assert download_image.call_args[0][0] == 'Illust!'
        assert download_image.call_args[1]['directory'] == Path.cwd()
        assert download_image.call_args[1]['allow_duplicate'] is True
        assert download_image.call_args[1]['track_download'] is False


@mock.patch('pixi.commands.download_image')
@mock.patch('pixi.commands.Client')
@mock.patch('pixi.commands.Config')
def test_illust_error(_, __, download_image):
    download_image.side_effect = BadApiResponse
    result = CliRunner().invoke(illust, '12345')
    assert isinstance(result.exception, DownloadFailed)


@mock.patch('pixi.commands.download_pages')
@mock.patch('pixi.commands.Client')
@mock.patch('pixi.commands.Config')
def test_artist(_, client, download_pages):
    CliRunner().invoke(artist, [
        '--page',
        '372',
        'https://www.pixiv.net/member.php?id=12345',
    ])
    assert download_pages.call_args[1]['starting_offset'] == 371 * 30

    download_pages.call_args[0][0](222)
    fetch_user_illustrations = client.return_value.fetch_user_illustrations
    fetch_user_illustrations.assert_called_with(12345, offset=222)


@mock.patch('pixi.commands.download_pages')
@mock.patch('pixi.commands.Client')
@mock.patch('pixi.commands.Config')
def test_bookmarks(_, client, download_pages):
    CliRunner().invoke(bookmarks)
    assert download_pages.call_count == 2


@mock.patch('pixi.commands.download_pages')
@mock.patch('pixi.commands.Client')
@mock.patch('pixi.commands.Config')
def test_bookmarks_with_visibility(_, client, download_pages):
    CliRunner().invoke(bookmarks, ['--visibility', 'public'])
    assert download_pages.call_count == 1

    client.return_value.account.id = 789
    download_pages.call_args[0][0](10)
    assert client.return_value.fetch_user_bookmarks.called_with(
        user=789,
        max_bookmark_id=10,
        visibility=Visibility.PUBLIC,
        tag=None,
    )


def test_failed(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)
        with database() as (conn, cursor):
            cursor.execute(
                """
                INSERT INTO FAILED (id, artist, title, time)
                VALUES (?, ?, ?, ?)
                """,
                (
                    20,
                    'testing',
                    'illustration',
                    '2019-01-01T01:23:45-04:00',
                )
            )

        result = runner.invoke(failed)
        assert result.output == (
            'Jan 01, 2019 01:23:45 | testing - illustration\n'
            'URL: https://www.pixiv.net/member_illust.php?mode=medium'
            '&illust_id=20\n\n'
        )


@mock.patch('pixi.commands._confirm_table_wipe')
def test_wipe(_, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)

        with database() as (conn, cursor):
            cursor.execute(
                'INSERT INTO downloaded (id, path) VALUES (1, "a")'
            )
            cursor.execute(
                'INSERT INTO FAILED (id, artist, title) VALUES (1, "a", "b")'
            )
            conn.commit()

        runner.invoke(wipe, '--table=all')

        with database() as (conn, cursor):
            cursor.execute('SELECT 1 FROM downloaded')
            assert not cursor.fetchone()
            cursor.execute('SELECT 1 FROM failed')
            assert not cursor.fetchone()


@mock.patch('pixi.commands._confirm_table_wipe')
def test_wipe_single(_, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)

        with database() as (conn, cursor):
            cursor.execute(
                'INSERT INTO downloaded (id, path) VALUES (1, "a")'
            )
            cursor.execute(
                'INSERT INTO FAILED (id, artist, title) VALUES (1, "a", "b")'
            )
            conn.commit()

        runner.invoke(wipe, '--table=failed')

        with database() as (conn, cursor):
            cursor.execute('SELECT 1 FROM downloaded')
            assert cursor.fetchone()
            cursor.execute('SELECT 1 FROM failed')
            assert not cursor.fetchone()


@mock.patch('pixi.commands._confirm_table_wipe')
def test_wipe_failed(confirm, monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)
        confirm.side_effect = click.Abort

        with database() as (conn, cursor):
            cursor.execute(
                'INSERT INTO downloaded (id, path) VALUES (1, "a")'
            )
            cursor.execute(
                'INSERT INTO FAILED (id, artist, title) VALUES (1, "a", "b")'
            )
            conn.commit()

        result = runner.invoke(wipe, '--table=all')
        assert isinstance(result.exception, SystemExit)

        with database() as (conn, cursor):
            cursor.execute('SELECT 1 FROM downloaded')
            assert cursor.fetchone()
            cursor.execute('SELECT 1 FROM failed')
            assert cursor.fetchone()


def test_confirm_table_wipe():
    result = CliRunner().invoke(
        click.command()(lambda: _confirm_table_wipe('table')),
        input='table',
    )
    assert not result.exception


def test_confirm_table_wipe_fail():
    result = CliRunner().invoke(
        click.command()(lambda: _confirm_table_wipe('table')),
        input='not table',
    )
    assert isinstance(result.exception, SystemExit)
