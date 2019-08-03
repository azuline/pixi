import mock

from pixi.config import Config


@mock.patch('pixi.config._validate_config')
def test_singleton(validate_config):
    validate_config.return_value = True
    config1 = Config()
    config2 = Config()
    assert config1 is config2
