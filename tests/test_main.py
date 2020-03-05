import pytest
import _pytest.fixtures as pytest_fixtures


def test_config(config_dict: pytest_fixtures.FixtureFunctionMarker) -> None:
    assert isinstance(config_dict, dict)
