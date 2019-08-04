from pathlib import Path

import pytest
from click.testing import CliRunner

from pixi.common import check_duplicate, format_filename, parse_id
from pixi.errors import InvalidURL


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


def test_check_duplicate_exists():
    with CliRunner().isolated_filesystem():
        path = Path.cwd() / 'file.jpg'
        path.touch()
        path.with_name('file (1).jpg').touch()
        new_path = check_duplicate(path)
        assert new_path == Path.cwd() / 'file (2).jpg'


def test_check_duplicate_doesnt_exist():
    with CliRunner().isolated_filesystem():
        path = Path.cwd() / 'file.jpg'
        new_path = check_duplicate(path)
        assert new_path == Path.cwd() / 'file.jpg'


def test_format_filename():
    assert 'id. title' == format_filename('id', 'title')
