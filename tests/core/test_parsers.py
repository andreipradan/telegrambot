from unittest.mock import MagicMock
import pytest
from core.parsers import parse_diff
from core.parsers import parse_name


class TestParseDiff:
    @pytest.mark.parametrize("data", [{"foo": 1}, "bar", None, [], {}])
    def test_no_old_version(self, data):
        assert parse_diff(data, None) == data

    def test_same_values(self):
        data = {"abc": 1, "cde": 2}
        assert parse_diff(data, data) == data

    def test_different_keys(self):
        data = {"abc": 1, "cde": 2}
        old_values = {"fgh": 123, "ijk": 456}
        assert parse_diff(data, old_values) == data

    @pytest.mark.parametrize(
        ("data", "old_data", "results"),
        [
            (
                {"abc": 123, "def": 456},
                {"abc": 125, "def": 449},
                {"abc": "123 (-2)", "def": "456 (+7)"},
            ),
            (
                {"abc": 123, "def": 456, "jkl": 678},
                {"abc": 123, "def": 451},
                {"abc": 123, "def": "456 (+5)", "jkl": 678},
            ),
        ],
    )
    def test_different_values(self, data, old_data, results):
        assert parse_diff(data, old_data) == results


@pytest.mark.parametrize(
    ("user", "result"),
    [
        (MagicMock(first_name="foo", last_name="bar"), "foo bar"),
        (MagicMock(first_name=None, last_name="bar"), "bar"),
        (MagicMock(first_name=None, last_name=None, username="cux"), "cux"),
    ],
)
def test_parse_name(user, result):
    assert parse_name(user) == result
