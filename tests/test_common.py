from pathlib import Path

import mock
import pytest
from click.testing import CliRunner
from pixivapi import BadApiResponse, Size

from pixi.common import (
    download_image,
    format_filename,
    parse_id,
    rename_duplicate_file,
)
from pixi.errors import DownloadFailed, InvalidURL


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


@mock.patch('pixi.common.format_filename')
def test_download_illust(format_filename):
    format_filename.return_value = '1. image'
    illustration = mock.Mock()
    illustration.client = mock

    with CliRunner().isolated_filesystem():
        download_image(illustration, directory=str(Path.cwd()))

        assert illustration.download.called_with(
            directory=Path.cwd(),
            size=Size.ORIGINAL,
            filename='1. image',
        )


@mock.patch('pixi.common.format_filename')
def test_download_illust_error(format_filename):
    format_filename.return_value = '1. image'
    illustration = mock.Mock()
    illustration.download.side_effect = BadApiResponse

    with CliRunner().isolated_filesystem():
        with pytest.raises(DownloadFailed):
            download_image(illustration, directory=str(Path.cwd()))
