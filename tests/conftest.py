import pytest

from flask_app import app


@pytest.fixture(scope="module")
def test_client():
    testing_client = app.test_client()
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield testing_client  # this is where the testing happens!
    ctx.pop()
