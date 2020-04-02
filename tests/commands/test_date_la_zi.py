import pytest
import requests
import responses

from scrapers.date_la_zi import histogram

URL = "https://api1.datelazi.ro/api/v2/data/ui-data/"


@responses.activate
@pytest.mark.parametrize("status_code", [400, 401, 403, 404, 500, 503, 504])
def test_raises_on_non_200_response(status_code):
    responses.add(
        responses.GET, URL, status=status_code, json={"error": "error"},
    )
    with pytest.raises(requests.exceptions.HTTPError):
        assert histogram()
    assert len(responses.calls) == 1
    assert responses.calls[0].request.url == URL
    assert responses.calls[0].response.text == '{"error": "error"}'
