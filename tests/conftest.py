import pytest

from flask_app import app

app.config["SERVER_NAME"] = "example.com"
app.config["TESTING"] = True


@pytest.fixture(scope="module")
def test_client():
    client = app.test_client()
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()
