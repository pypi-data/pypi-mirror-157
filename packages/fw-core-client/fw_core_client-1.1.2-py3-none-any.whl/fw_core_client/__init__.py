"""Flywheel Core HTTP API Client."""
try:
    from importlib.metadata import version
except ImportError:  # pragma: no cover
    from importlib_metadata import version  # type: ignore

from fw_http_client import ConnectionError  # pylint: disable=redefined-builtin
from fw_http_client import ClientError, ServerError, errors

from .client import CoreClient
from .config import CoreConfig

__version__ = version(__name__)
__all__ = [
    "CoreClient",
    "CoreConfig",
    "errors",
    "ConnectionError",
    "ClientError",
    "ServerError",
]
