import pytest
import requests
import responses

from commands.date_la_zi import histogram
from core import constants


def mock_request(**kwargs):
    responses.add(
        responses.GET,
        constants.URLS["romania"],
        status=kwargs.pop("status_code", 200),
        json={"error": "error"},
    )


@responses.activate
@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500, 503, 504])
def test_raises_on_non_200_response(status_code):
    mock_request(status_code=status_code)
    with pytest.raises(requests.exceptions.HTTPError):
        assert histogram()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == constants.URLS["romania"]
    assert responses.calls[0].response.text == '{"error": "error"}'
