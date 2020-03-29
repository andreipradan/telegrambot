import pytest

from scrapers import formatters


def test_get_verbose():
    assert formatters.get_verbose("last_updated") == "Last updated"


class TestParseDetails:
    @pytest.mark.parametrize("data", [0, "", None, []])
    def test_with_empty(self, data):
        with pytest.raises(ValueError) as e:
            formatters.parse_details(data)
        assert e.value.args[0] == "data must not be null, empty, etc."

    def test_with_one_key_dict(self):
        assert formatters.parse_details({"foo": 1}) == "└ Foo: 1"

    def test_with_multiple_key_dict(self):
        assert formatters.parse_details(
            {"foo": 1, "bar": 2, "cux": 3}
        ) == "├ Foo: 1\n├ Bar: 2\n└ Cux: 3"

    def test_with_one_item_list(self):
        assert formatters.parse_details(["foo"]) == "└ foo"

    def test_with_multiple_items_list(self):
        assert formatters.parse_details(
            ["foo", "bar", "cux"]
        ) == "├ foo\n├ bar\n└ cux"


def test_parse_list_details():
    assert formatters.parse_list_details({"foo": ["bar"]}) == "\n➡️ foo\n└ bar"


def test_parse_global():
    assert formatters.parse_global({"foo": "bar"}, {"bar": ["cux"]}) == (
        "\n🦠 Romania\n└ Foo: bar\n\n➡️ bar\n└ cux\n\n"
    )
