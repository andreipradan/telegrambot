from unittest.mock import MagicMock

import pytest

from core.validators import validate_response, is_valid_date


def test_is_valid_date():
    assert is_valid_date("foo") is False
    assert is_valid_date("2020-01-01") is True


def test_validate_response():
    assert validate_response(MagicMock(status_code=200)) is None


def test_validate_response_not_200():
    with pytest.raises(ValueError) as e:
        validate_response(MagicMock(status_code=419))
    assert e.value.args[0] == "Got an unexpected status code: 419"
