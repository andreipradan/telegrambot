import pytest

from core.views.base import make_json_response


class TestMakeJsonResponse:
    def test_with_no_params(self, client):
        response, status_code = make_json_response()
        assert status_code == 200
        assert response.json == {
            "count": 0,
            "data": {},
            "errors": [],
            "links": {"home": "http://example.com/"},
        }

    @pytest.mark.parametrize(
        ("data", "count"),
        [
            ([1, 2, 3, 4], 4),
            ({"a": 1}, 1),
            ("string", 1),
            *[(x, 0) for x in [[], (), {}, "", 0]],
        ],
    )
    def test_count(self, client, data, count):
        response, _ = make_json_response(data=data)
        assert response.json["count"] == count
