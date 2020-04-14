import time
from unittest import mock

import pytest

from core.auth import _authenticate
from core.auth import _is_authorized
from core.auth import _get_client_ip
from core.auth import header_auth
from core.auth import whitelist_auth
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


class TestHeaderAuth:
    def test_with_disabled_header_auth(self, monkeypatch):
        monkeypatch.setenv("DISABLE_HEADER_AUTH", "True")
        func = mock.Mock(return_value="foo response")
        decorated_func = header_auth(func)
        response = decorated_func("foo_arg", foo=1, bar=2)
        func.assert_called_with("foo_arg", foo=1, bar=2)
        assert response == "foo response"

    @mock.patch("core.auth.abort")
    @mock.patch("core.auth.request")
    def test_with_no_auth_header(self, request_mock, abort_mock):
        request_mock.headers.get.return_value = None
        func = mock.Mock()
        decorated_func = header_auth(func)
        response = decorated_func("foo_arg", foo=1, bar=2)
        request_mock.headers.get.assert_called_once_with("Authorization")
        assert not func.called
        abort_mock.assert_called_once_with(403)
        assert response == abort_mock()

    @mock.patch("core.auth._authenticate")
    @mock.patch("core.auth.abort")
    @mock.patch("core.auth.request")
    def test_with_authentication_failed(self, req, abort_mock, auth_mock):
        auth_mock.return_value = False

        func = mock.Mock()
        decorated_func = header_auth(func)
        response = decorated_func("foo_arg", foo=1, bar=2)

        assert not func.called
        req.headers.get.assert_called_once_with("Authorization")
        abort_mock.assert_called_once_with(403)
        assert response == abort_mock()

    @mock.patch("core.auth._authenticate")
    @mock.patch("core.auth.abort")
    @mock.patch("core.auth.request")
    def test_auth_successful(self, req, abort_mock, auth_mock):
        auth_mock.return_value = True

        func = mock.Mock(return_value="result_foo")
        decorated_func = header_auth(func)
        response = decorated_func("foo_arg", foo=1, bar=2)

        req.headers.get.assert_called_once_with("Authorization")
        assert not abort_mock.called
        func.assert_called_once_with("foo_arg", bar=2, foo=1)
        assert response == "result_foo"


class TestWhitelistAuth:
    @mock.patch("core.auth.abort")
    @mock.patch("core.auth._is_authorized")
    @mock.patch("core.auth._get_client_ip")
    def test_with_unauthorized_ip(self, get_ip, is_authorized, abort_mock):
        get_ip.return_value = "ip_foo"
        is_authorized.return_value = False

        func = mock.Mock()
        decorated_func = whitelist_auth(func)
        response = decorated_func("foo_arg", foo=1, bar=2)

        assert not func.called
        get_ip.assert_called_once_with()
        is_authorized.assert_called_once_with("ip_foo")
        abort_mock.assert_called_once_with(403)
        assert response == abort_mock()

    @mock.patch("core.auth.abort")
    @mock.patch("core.auth._is_authorized")
    @mock.patch("core.auth._get_client_ip")
    @mock.patch("core.auth.request")
    def test_with_authorized_ip(self, req, get_ip, is_authorized, abort_mock):
        get_ip.return_value = "ip_foo"
        is_authorized.return_value = True

        func = mock.Mock(return_value="response_foo")
        decorated_func = whitelist_auth(func)
        response = decorated_func("foo_arg", foo=1, bar=2)

        func.assert_called_once_with(req, "foo_arg", foo=1, bar=2)
        get_ip.assert_called_once_with()
        is_authorized.assert_called_once_with("ip_foo")
        assert response == "response_foo"
        assert not abort_mock.called
