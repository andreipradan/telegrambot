import datetime


def is_valid_date(date_text):
    try:
        datetime.datetime.strptime(date_text, "%Y-%m-%d")
    except ValueError:
        return False
    return True


def validate_response(response):
    status_code = response.status_code
    if not status_code == 200:
        raise ValueError(f"Got an unexpected status code: {status_code}")
