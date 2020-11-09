from dataclasses import dataclass
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner
from pixivapi import LoginError

from pixi.client import Client, _PixivClient
from pixi.errors import GoAuthenticate


@dataclass
class RequestResponse:
    headers = {"Content-Length": 3072}

    def iter_content(*args, **kwargs):
        return iter([b"a", b"b"])


@mock.patch("pixi.client.Config")
@mock.patch("pixi.client._PixivClient.authenticate")
def test_get_client_no_refresh_token(_, config):
    config.return_value = {"pixi": {"refresh_token": False}}
    with pytest.raises(GoAuthenticate):
        Client()


@mock.patch("pixi.client.Config")
@mock.patch("pixi.client._PixivClient.authenticate")
def test_get_client_crappy_refresh_token(authenticate, config):
    config.return_value = {"pixi": {"refresh_token": True}}
    authenticate.side_effect = LoginError
    with pytest.raises(GoAuthenticate):
        Client()


@mock.patch("pixi.client.Config")
@mock.patch("pixi.client._PixivClient.authenticate")
def test_working_get_client(authenticate, config):
    Client()


@mock.patch("pixi.client.Config")
@mock.patch("pixi.client._PixivClient.authenticate")
def test_get_client_no_authentication(authenticate, config):
    config.return_value = {"pixi": {"refresh_token": False}}
    authenticate.side_effect = LoginError
    Client(authenticate=False)


@mock.patch("pixi.client.ceil")
@mock.patch("pixi.client.rename_duplicate_file")
def test_client_download(rename_duplicate_file, ceil):
    with CliRunner().isolated_filesystem():
        destination = Path.cwd() / "filename.jpg"
        rename_duplicate_file.return_value = destination
        ceil.return_value = 3

        _PixivClient.authenticate = None
        client = _PixivClient(authenticate=False)
        client.session.get = lambda *a, **k: RequestResponse()
        client.download("haha not a url", destination)

        with destination.open("r") as f:
            assert "ab" == f.read()


@mock.patch("pixi.client.rename_duplicate_file")
def test_client_download_file_deletion(rename_duplicate_file):
    with CliRunner().isolated_filesystem():
        destination = mock.Mock()
        destination.open.side_effect = Exception
        rename_duplicate_file.return_value = destination

        _PixivClient.authenticate = None
        client = _PixivClient(authenticate=False)
        client.session.get = lambda *a, **k: RequestResponse()
        with pytest.raises(Exception):
            client.download("haha not a url", destination)

        destination.unlink.assert_called()
