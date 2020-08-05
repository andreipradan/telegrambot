import os
import pytest

os.environ["SECRET_KEY"] = "test_secret_key"
os.environ["TOKEN"] = "test_token"
os.environ["DATELAZI_DATA_URL"] = "http://foodatelazi.dev"


@pytest.fixture(scope="module")
def client():
    from flask_app import app

    app.config["SERVER_NAME"] = "example.com"
    app.config["TESTING"] = True
    client = app.test_client()
    # Establish an application context before running the tests.
    ctx = app.app_context()
    ctx.push()
    yield client  # this is where the testing happens!
    ctx.pop()


@pytest.fixture(autouse=True)
def no_requests(monkeypatch):
    """Remove requests.sessions.Session.request for all tests."""
    monkeypatch.delattr("requests.sessions.Session.request")
    monkeypatch.delattr("pymongo.MongoClient")
