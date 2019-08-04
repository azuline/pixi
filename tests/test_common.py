import unittest.mock as umock

import mock
import pytest
from pixivapi import LoginError

from pixi.common import get_client, parse_id
from pixi.errors import GoAuthenticate, InvalidURL


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


@mock.patch('pixi.common.Config')
@mock.patch('pixi.common.Client')
def test_get_client_no_refresh_token(_, config):
    config.return_value = {'pixi': {'refresh_token': False}}
    with pytest.raises(GoAuthenticate):
        get_client()


@umock.patch('pixi.common.Config')
@umock.patch('pixi.common.Client')
def test_get_client_crappy_refresh_token(client, config):
    config.return_value = {'pixi': {'refresh_token': True}}
    client.return_value.authenticate.side_effect = LoginError
    with pytest.raises(GoAuthenticate):
        get_client()


@umock.patch('pixi.common.Config')
@umock.patch('pixi.common.Client')
def test_working_get_client(client, config):
    get_client()
