from configparser import ConfigParser
from pathlib import Path
from unittest import mock

import pytest
from click.testing import CliRunner

from pixi import make_app_directories
from pixi.config import Config, _validate_config, write_default_config
from pixi.errors import InvalidConfig


@mock.patch("pixi.config._validate_config")
def test_singleton(validate_config):
    config1 = Config()
    config2 = Config()
    assert config1 is config2


def test_validate_config_successful():
    with CliRunner().isolated_filesystem():
        test_dir = Path.cwd() / "tmp"
        test_dir.mkdir()
        _validate_config({"pixi": {"download_directory": str(test_dir)}})


@pytest.mark.parametrize(
    "config, error",
    [
        ({}, "Empty file"),
        ({"pixi": {}}, "Download directory not configured"),
        (
            {"pixi": {"download_directory": "/tmp/a/b/c/d/e/f/g"}},
            "Download directory does not exist or is not writeable",
        ),
    ],
)
def test_validate_config_failure(config, error):
    with pytest.raises(InvalidConfig) as e:
        _validate_config(config)

    assert str(e.value) == error


def test_validate_config_not_writeable():
    with CliRunner().isolated_filesystem():
        with pytest.raises(InvalidConfig) as e:
            test_dir = Path.cwd() / "tmp"
            test_dir.mkdir(mode=0o000)
            _validate_config({"pixi": {"download_directory": test_dir}})

    assert str(e.value) == ("Download directory does not exist or is not writeable")


def test_save_config(monkeypatch):
    with CliRunner().isolated_filesystem():
        mock_config = Path.cwd() / "config.ini"
        monkeypatch.setattr("pixi.config.CONFIG_PATH", mock_config)

        config = Config()
        config["pixi"] = {"test": "balls"}
        config.save()

        parser = ConfigParser()
        parser.read(mock_config)
        assert parser["pixi"]["test"] == "balls"


def test_create_app_directories(monkeypatch):
    with CliRunner().isolated_filesystem():
        mock_dir = Path.cwd() / "cfgdir"
        mock_dir2 = Path.cwd() / "datadir"
        monkeypatch.setattr("pixi.CONFIG_DIR", mock_dir)
        monkeypatch.setattr("pixi.DATA_DIR", mock_dir2)
        make_app_directories()
        assert mock_dir.is_dir()


def test_write_default_config(monkeypatch):
    with CliRunner().isolated_filesystem():
        mock_config = Path.cwd() / "config.ini"
        monkeypatch.setattr("pixi.config.CONFIG_PATH", mock_config)
        write_default_config()

        parser = ConfigParser()
        parser.read(mock_config)
        assert "pixi" in parser.sections()


def test_dont_write_default_config(monkeypatch):
    with CliRunner().isolated_filesystem():
        mock_config = Path.cwd() / "config.ini"
        with mock_config.open("w") as f:
            f.write("filler")
        monkeypatch.setattr("pixi.config.CONFIG_PATH", mock_config)
        write_default_config()
        with mock_config.open("r") as f:
            assert f.read() == "filler"
