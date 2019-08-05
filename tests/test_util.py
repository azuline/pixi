from pathlib import Path
from shutil import copyfile

import mock
import pytest
from click.testing import CliRunner
from pixivapi import BadApiResponse, Size

from pixi.database import database
from pixi.errors import DownloadFailed, DuplicateImage, InvalidURL
from pixi.util import (
    check_duplicate,
    clear_failed,
    download_image,
    format_filename,
    mark_failed,
    parse_id,
    record_download,
    rename_duplicate_file,
    resolve_track_download,
)


@pytest.mark.parametrize(
    'string', [
        '13',
        'https://www.pixiv.net/member_illust.php?mode=medium&illust_id=13',
    ]
)
def test_parse_id(string):
    assert 13 == parse_id(
        string=string,
        path='/member_illust.php',
        param='illust_id',
    )


@pytest.mark.parametrize(
    'string', [
        'notevenavalidurlLOL',
        'https://notpixiv.net/member_illust.php?illust_id=1111',
        'https://www.pixiv.net/badpath.php?illust_id=1111',
        'https://www.pixiv.net/member_illust.php?bad_param=1111',
    ]
)
def test_parse_id_invalid_url(string):
    with pytest.raises(InvalidURL):
        parse_id(
            string=string,
            path='/member_illust.php',
            param='illust_id',
        )


def test_rename_duplicate_file_exists():
    with CliRunner().isolated_filesystem():
        path = Path.cwd() / 'file.jpg'
        path.touch()
        path.with_name('file (1).jpg').touch()
        new_path = rename_duplicate_file(path)
        assert new_path == Path.cwd() / 'file (2).jpg'


def test_rename_duplicate_file_doesnt_exist():
    with CliRunner().isolated_filesystem():
        path = Path.cwd() / 'file.jpg'
        new_path = rename_duplicate_file(path)
        assert new_path == Path.cwd() / 'file.jpg'


def test_format_filename():
    assert 'id. title' == format_filename('id', 'title')


@pytest.mark.parametrize(
    'track_download, directory, result', [
        (True, True, True),
        (None, True, False),
        (None, False, True),
    ]
)
def test_resolve_track_download(track_download, directory, result):
    assert result == resolve_track_download(track_download, directory)


@mock.patch('pixi.util.format_filename')
@mock.patch('pixi.util.Config')
@mock.patch('pixi.util.check_duplicate')
@mock.patch('pixi.util.clear_failed')
@mock.patch('pixi.util.record_download')
def test_download_illust(_, __, ___, ____, format_filename):
    format_filename.return_value = '1. image'
    illustration = mock.Mock()
    illustration.client = mock
    illustration.meta_pages = False

    with CliRunner().isolated_filesystem():
        download_image(illustration, directory=str(Path.cwd()))

        assert illustration.download.called_with(
            directory=Path.cwd(),
            size=Size.ORIGINAL,
            filename='1. image',
        )


@mock.patch('pixi.util.format_filename')
@mock.patch('pixi.util.Config')
@mock.patch('pixi.util.check_duplicate')
@mock.patch('pixi.util.mark_failed')
def test_download_illust_error(_, __, ___, format_filename):
    format_filename.return_value = '1. image'
    illustration = mock.Mock()
    illustration.download.side_effect = BadApiResponse

    with CliRunner().isolated_filesystem():
        with pytest.raises(DownloadFailed):
            download_image(illustration, directory=str(Path.cwd()), tries=2)
        assert illustration.download.call_count == 2


@mock.patch('pixi.util.format_filename')
@mock.patch('pixi.util.check_duplicate')
@mock.patch('pixi.util.Config')
@mock.patch('pixi.util.mark_failed')
def test_download_duplicate(_, __, check_duplicate, format_filename):
    illustration = mock.Mock()
    check_duplicate.side_effect = DuplicateImage

    with CliRunner().isolated_filesystem():
        download_image(illustration, directory=str(Path.cwd()))
        illustration.download.assert_not_called()


def test_mark_failed(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)

        illustration = mock.Mock(
            id=99,
            user=mock.Mock(account='dazuling'),
            title='cat whiskers',
        )
        mark_failed(illustration)

        with database() as (conn, cursor):
            cursor.execute(
                """
                SELECT id FROM failed WHERE id = ? AND artist = ? AND title = ?
                """,
                (
                    99,
                    'dazuling',
                    'cat whiskers',
                )
            )
            assert cursor.fetchone()['id'] == 99


def test_clear_failed(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)

        with database() as (conn, cursor):
            cursor.execute(
                """
                INSERT INTO failed (id, artist, title) VALUES (?, ?, ?)
                """,
                (
                    99,
                    'dazuling',
                    'cat whiskers',
                )
            )

        clear_failed(99)

        with database() as (conn, cursor):
            cursor.execute('SELECT 1 FROM failed WHERE id = ?', (99, ))
            assert not cursor.fetchone()


def test_record_download(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)

        record_download(99, '/haha/a/path')

        with database() as (conn, cursor):
            cursor.execute(
                """
                SELECT id FROM downloaded WHERE id = ? AND path = ?
                """,
                (
                    99,
                    '/haha/a/path',
                )
            )
            assert cursor.fetchone()['id'] == 99


def test_check_duplicate_positive(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)

        with database() as (conn, cursor):
            cursor.execute(
                """
                INSERT INTO downloaded (id, path) VALUES (?, ?)
                """,
                (
                    99,
                    '/haha/a/path',
                )
            )

        with pytest.raises(DuplicateImage):
            check_duplicate(99)


def test_check_duplicate_negative(monkeypatch):
    runner = CliRunner()
    with runner.isolated_filesystem():
        db_path = Path.cwd() / 'db.sqlite3'
        copyfile(Path(__file__).parent / 'test.db', db_path)
        monkeypatch.setattr('pixi.database.DATABASE_PATH', db_path)

        with database() as (conn, cursor):
            cursor.execute(
                """
                INSERT INTO downloaded (id, path) VALUES (?, ?)
                """,
                (
                    99,
                    '/haha/a/path',
                )
            )

        check_duplicate(98)
