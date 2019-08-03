import pytest

from pixi.common import parse_id
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
