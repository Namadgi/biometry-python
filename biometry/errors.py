"""Error types for the Biometry SDK."""

from __future__ import annotations

import json


class BiometryAPIError(Exception):
    """Raised for any HTTP 4xx/5xx response from the API."""

    def __init__(self, status_code: int, message: str, raw_body: bytes) -> None:
        self.status_code = status_code
        self.message = message
        self.raw_body = raw_body
        super().__init__(f"biometry: HTTP {status_code}: {message}")


def _parse_api_error(status_code: int, body: bytes) -> BiometryAPIError:
    """Parse an API error response body into a BiometryAPIError."""
    message = ""
    try:
        data = json.loads(body)
        error_field = data.get("error")
        if isinstance(error_field, str):
            message = error_field
        else:
            message = data.get("message", "")
    except (json.JSONDecodeError, ValueError):
        pass
    if not message:
        message = body.decode("utf-8", errors="replace")
    return BiometryAPIError(status_code, message, body)


def is_not_found(err: BaseException) -> bool:
    """Return True if *err* is a 404 API response."""
    return isinstance(err, BiometryAPIError) and err.status_code == 404


def is_forbidden(err: BaseException) -> bool:
    """Return True if *err* is a 403 API response."""
    return isinstance(err, BiometryAPIError) and err.status_code == 403


def is_unauthorized(err: BaseException) -> bool:
    """Return True if *err* is a 401 API response."""
    return isinstance(err, BiometryAPIError) and err.status_code == 401
