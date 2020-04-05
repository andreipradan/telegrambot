from unittest.mock import MagicMock

import pytest

from core.validators import validate_response


def test_validate_response():
    assert validate_response(MagicMock(status_code=200)) is None


def test_validate_response_not_200():
    with pytest.raises(ValueError) as e:
        validate_response(MagicMock(status_code=419))
    assert e.value.args[0] == "Got an unexpected status code: 419"
