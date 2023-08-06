"""Flywheel client errors."""
# pylint: disable=wildcard-import,unused-wildcard-import,redefined-builtin
from fw_http_client import ClientError, NotFound, ServerError
from requests.exceptions import *

__all__ = ["ClientError", "NotFound", "ServerError"]
