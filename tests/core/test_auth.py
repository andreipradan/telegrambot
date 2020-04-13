import time
from unittest import mock

import pytest

from core.auth import _authenticate, _is_authorized, _get_client_ip
from core.constants import WEBHOOK_WHITELIST


class TestAuthenticate:
    @staticmethod
    def set_auth_env_vars(monkeypatch):
        monkeypatch.setenv("AUTH_CERTS_URL", "foo_certs_url")
        monkeypatch.setenv("AUTH_AUDIENCE", "foo_audience")
        monkeypatch.setenv("AUTH_ISSUER", "foo_iss1,foo_iss2")

    def test_with_no_token(self):
        assert _authenticate("") is False

    @mock.patch("core.auth.Request")
    @mock.patch("core.auth.id_token.verify_token")
    def test_successful(self, verify_mock, request_mock, monkeypatch):
        self.set_auth_env_vars(monkeypatch)
        verify_mock.return_value = {
            "aud": "foo_audience",
            "iss": "foo_iss2",
            "exp": time.time() + 1000,
        }
        assert _authenticate("foo_token") is True
        verify_mock.assert_called_once_with(
            id_token="foo_token",
            request=request_mock(),
            certs_url="foo_certs_url",
        )

    @mock.patch("core.auth.Request")
    @mock.patch("core.auth.id_token.verify_token", side_effect=ValueError("e"))
    def test_unsuccessful(self, verify_mock, request_mock, monkeypatch):
        self.set_auth_env_vars(monkeypatch)
        assert _authenticate("foo") is False
        verify_mock.assert_called_once_with(
            id_token="foo", request=request_mock(), certs_url="foo_certs_url",
        )

    @mock.patch("core.auth.Request")
    @mock.patch("core.auth.id_token.verify_token")
    def test_with_bad_audience(self, verify_mock, request_mock, monkeypatch):
        self.set_auth_env_vars(monkeypatch)
        verify_mock.return_value = {
            "aud": "bad_audience",
            "iss": "foo_iss2",
            "exp": time.time() + 1000,
        }
        assert _authenticate("foo_token") is False
        verify_mock.assert_called_once_with(
            id_token="foo_token",
            request=request_mock(),
            certs_url="foo_certs_url",
        )

    @mock.patch("core.auth.Request")
    @mock.patch("core.auth.id_token.verify_token")
    def test_with_bad_iss(self, verify_mock, request_mock, monkeypatch):
        self.set_auth_env_vars(monkeypatch)
        verify_mock.return_value = {
            "aud": "foo_audience",
            "iss": "bad_issuer",
            "exp": time.time() + 1000,
        }
        assert _authenticate("foo_token") is False
        verify_mock.assert_called_once_with(
            id_token="foo_token",
            request=request_mock(),
            certs_url="foo_certs_url",
        )


class TestIsAuthorized:
    def test_with_whitelisted_network(self):
        assert _is_authorized("91.108.4.5") is True

    def test_with_whitelisted_ip(self):
        WEBHOOK_WHITELIST.append("192.168.0.1")
        assert _is_authorized("192.168.0.1") is True

    @mock.patch("core.auth.logger.exception")
    def test_with_invalid_item_in_whitelist(self, log_mock):
        WEBHOOK_WHITELIST.append("foo")
        assert _is_authorized("192.168.0.3") is None
        log_mock.assert_called_once_with(
            "The AUTH WHITELIST contains an item that is neither an "
            "ip address nor an ip network: foo"
        )

    def test_with_ip_not_in_whitelist(self):
        assert not _is_authorized("1.3.3.7")

    def test_with_invalid_ip_address(self):
        with pytest.raises(ValueError) as e:
            _is_authorized("foo")
        msg = "'foo' does not appear to be an IPv4 or IPv6 address"
        assert msg in str(e)


class TestGetClientIP:
    @mock.patch("core.auth.request")
    def test_with_one_ip_in_access_route(self, req):
        req.access_route = ["foo_ip"]
        assert _get_client_ip() == "foo_ip"

    @mock.patch("core.auth.request")
    def test_with_multiple_invalid_ips_in_access_route(self, req):
        req.access_route = ["foo_ip", "bar_ip"]
        assert _get_client_ip() is None

    @mock.patch("core.auth.request")
    def test_with_empty_and_invalid_ips_in_access_route(self, req):
        req.access_route = ["", "bar_ip"]
        assert _get_client_ip() is None

    @mock.patch("core.auth.request")
    def test_with_first_ip_empty_and_matched_expression(self, req):
        req.access_route = ["", "192.168.1.1"]
        assert _get_client_ip() is None

    @mock.patch("core.auth.request")
    def test_with_first_ip_empty_and_valid_other_one(self, req):
        req.access_route = ["", "86.14.11.2"]
        assert _get_client_ip() == "86.14.11.2"
