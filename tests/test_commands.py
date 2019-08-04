from pathlib import Path

import mock
from click.testing import CliRunner

from pixi.commands import auth, config, image
from pixi.errors import DownloadError, PixiError
from pixivapi import BadApiResponse, LoginError, Size


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


@mock.patch('pixi.commands.get_client')
@mock.patch('pixi.commands.parse_id')
@mock.patch('pixi.commands.format_filename')
def test_download_image(format_filename, parse_id, get_client):
    parse_id.return_value = 1
    format_filename.return_value = '1. image'

    runner = CliRunner()
    with runner.isolated_filesystem():
        CliRunner().invoke(image, ['1', '-d', Path.cwd()])
        fetch_illustration = get_client.return_value.fetch_illustration
        assert fetch_illustration.return_value.called_with(
            directory=Path.cwd(),
            size=Size.ORIGINAL,
            filename='1. image',
        )


@mock.patch('pixi.commands.get_client')
@mock.patch('pixi.commands.parse_id')
@mock.patch('pixi.commands.format_filename')
def test_download_image_error(format_filename, parse_id, get_client):
    parse_id.return_value = 1
    format_filename.return_value = '1. image'
    get_client.return_value.fetch_illustration.side_effect = BadApiResponse

    runner = CliRunner()
    with runner.isolated_filesystem():
        result = CliRunner().invoke(image, ['1', '-d', Path.cwd()])
        assert isinstance(result.exception, DownloadError)
