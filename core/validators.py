def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f"Got an unexpected status code: {status_code}")
