from unittest import mock

import pytest

from core.auth import _authenticate, _is_authorized, _get_client_ip
from core.constants import AUTH


def test_authenticate_successful():
    with mock.patch("core.database.get_collection"):
        assert _authenticate("foo_token") is True


def test_authenticate_unsuccessful():
    with mock.patch("core.database.get_collection") as get_mock:
        get_mock().find_one.return_value = None
        assert _authenticate("foo") is False


def test_is_authorized_with_whitelisted_network():
    assert _is_authorized("91.108.4.5") is True


def test_is_authorized_with_whitelisted_ip():
    AUTH["WHITELIST"].append("192.168.0.1")
    assert _is_authorized("192.168.0.1") is True


@mock.patch("core.auth.logger.exception")
def test_is_authorized_with_invalid_item_in_whitelist(log_mock):
    AUTH["WHITELIST"].append("foo")
    assert _is_authorized("192.168.0.3") is None
    log_mock.assert_called_once_with(
        "The AUTH WHITELIST contains an item that is neither an "
        "ip address nor an ip network: foo"
    )


def test_is_authorized_with_ip_not_in_whitelist():
    assert not _is_authorized("1.3.3.7")


def test_is_authorized_with_invalid_ip_address():
    with pytest.raises(ValueError) as e:
        _is_authorized("foo")
    msg = "'foo' does not appear to be an IPv4 or IPv6 address"
    assert msg in str(e)


@mock.patch("core.auth.request")
def test_get_client_ip_with_one_ip_in_access_route(req):
    req.access_route = ["foo_ip"]
    assert _get_client_ip() == "foo_ip"


@mock.patch("core.auth.request")
def test_get_client_ip_with_multiple_invalid_ips_in_access_route(req):
    req.access_route = ["foo_ip", "bar_ip"]
    assert _get_client_ip() is None


@mock.patch("core.auth.request")
def test_get_client_ip_with_empty_and_invalid_ips_in_access_route(req):
    req.access_route = ["", "bar_ip"]
    assert _get_client_ip() is None


@mock.patch("core.auth.request")
def test_get_client_ip_with_first_ip_empty_and_matched_expression(req):
    req.access_route = ["", "192.168.1.1"]
    assert _get_client_ip() is None


@mock.patch("core.auth.request")
def test_get_client_ip_with_first_ip_empty_and_valid_other_one(req):
    req.access_route = ["", "86.14.11.2"]
    assert _get_client_ip() == "86.14.11.2"
