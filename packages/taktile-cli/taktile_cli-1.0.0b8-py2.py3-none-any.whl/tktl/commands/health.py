import requests
from pyarrow.flight import (  # type: ignore
    FlightCancelledError,
    FlightClient,
    FlightUnauthenticatedError,
    FlightUnavailableError,
)

from tktl.core.clients.http_client import interpret_response
from tktl.core.config import settings as tktl_settings
from tktl.core.exceptions import APIClientException
from tktl.core.utils import concatenate_urls


def check_rest_health():
    healthz_url = concatenate_urls(tktl_settings.LOCAL_REST_ENDPOINT, "healthz")
    interpret_response(requests.get(healthz_url), model=None, ping=True)


def check_grpc_health():
    try:
        client = FlightClient(
            tls_root_certs=None, location=tktl_settings.LOCAL_ARROW_ENDPOINT,
        )
        client.wait_for_available(timeout=1)
    except FlightUnauthenticatedError:
        return True
    except (FlightCancelledError, FlightUnavailableError) as e:
        error_str = f"Service is not running properly: {repr(e.detail)}"
        raise APIClientException(detail=error_str, status_code=e.status_code)
