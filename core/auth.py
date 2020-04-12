import logging
import re
from functools import wraps
from ipaddress import ip_address
from ipaddress import ip_network

from flask import abort
from flask import request

from core import database
from core.constants import AUTH


logger = logging.getLogger(__name__)


def _authenticate(token):
    return bool(database.get_collection("auth").find_one({"token": token}))


def _get_client_ip():
    access_route = request.access_route

    if len(access_route) == 1:
        return access_route[0]
    expression = """
        (^(?!(?:[0-9]{1,3}\.){3}[0-9]{1,3}$).*$)|  # will match non valid ipV4
        (^127\.0\.0\.1)|  # will match 127.0.0.1
        (^10\.)|  # will match 10.0.0.0 - 10.255.255.255 IP-s
        (^172\.1[6-9]\.)|  # will match 172.16.0.0 - 172.19.255.255 IP-s
        (^172\.2[0-9]\.)|  # will match 172.20.0.0 - 172.29.255.255 IP-s
        (^172\.3[0-1]\.)|  # will match 172.30.0.0 - 172.31.255.255 IP-s
        (^192\.168\.)  # will match 192.168.0.0 - 192.168.255.255 IP-s
    """
    regex = re.compile(expression, re.X)
    for ip in access_route:
        if not ip:
            continue
        if regex.search(ip):
            continue
        return ip


def _is_authorized(ip):
    ip = ip_address(ip)
    for item in AUTH["WHITELIST"]:
        try:
            if ip == ip_address(item):
                return True
        except ValueError:
            try:
                if ip in ip_network(item):
                    return True
            except ValueError:
                logger.exception(
                    "The AUTH WHITELIST contains an item that is neither an "
                    f"ip address nor an ip network: {item}"
                )


def header_auth(func):
    @wraps(func)
    def _decorator(*args, **kwargs):
        token = request.headers.get(AUTH["HEADER_NAME"].title())
        if token and _authenticate(token):
            logger.info("Authenticated with header")
            return func(*args, **kwargs)
        return abort(403)

    return _decorator


def whitelist_auth(func):
    @wraps(func)
    def _decorator(*args, **kwargs):
        ip = _get_client_ip()
        if _is_authorized(ip):
            return func(request, *args, **kwargs)
        return abort(403)

    return _decorator
