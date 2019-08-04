import mock
import pytest
from pixivapi import LoginError

from pixi.client import Client
from pixi.errors import GoAuthenticate


@mock.patch('pixi.client.Config')
@mock.patch('pixi.client._PixivClient.authenticate')
def test_get_client_no_refresh_token(_, config):
    config.return_value = {'pixi': {'refresh_token': False}}
    with pytest.raises(GoAuthenticate):
        Client()


@mock.patch('pixi.client.Config')
@mock.patch('pixi.client._PixivClient.authenticate')
def test_get_client_crappy_refresh_token(authenticate, config):
    config.return_value = {'pixi': {'refresh_token': True}}
    authenticate.side_effect = LoginError
    with pytest.raises(GoAuthenticate):
        Client()


@mock.patch('pixi.client.Config')
@mock.patch('pixi.client._PixivClient.authenticate')
def test_working_get_client(authenticate, config):
    Client()


@mock.patch('pixi.client.Config')
@mock.patch('pixi.client._PixivClient.authenticate')
def test_get_client_no_authentication(authenticate, config):
    config.return_value = {'pixi': {'refresh_token': False}}
    authenticate.side_effect = LoginError
    Client(authenticate=False)
