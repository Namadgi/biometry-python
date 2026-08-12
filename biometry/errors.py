"""Error types for the Biometry SDK."""

from __future__ import annotations

import json


class BiometryAPIError(Exception):
    """Raised for any HTTP 4xx/5xx response from the API."""

    def __init__(self, status_code: int, message: str, raw_body: bytes, code: str = "") -> None:
        self.status_code = status_code
        #: Machine-readable error code from the API v2 error envelope
        #: (e.g. "invalid_request", "face_not_detected"). Empty for legacy responses.
        self.code = code
        self.message = message
        self.raw_body = raw_body
        if code:
            super().__init__(f"biometry: HTTP {status_code} [{code}]: {message}")
        else:
            super().__init__(f"biometry: HTTP {status_code}: {message}")


def _parse_api_error(status_code: int, body: bytes) -> BiometryAPIError:
    """Parse an API error response body into a BiometryAPIError."""
    code = ""
    message = ""
    try:
        data = json.loads(body)
        error_field = data.get("error")
        if isinstance(error_field, dict):
            # API v2 error envelope: {"error": {"code", "message"}, "meta": {...}}.
            code = error_field.get("code", "") or ""
            msg = error_field.get("message")
            if isinstance(msg, str):
                message = msg
            elif msg is not None:
                message = json.dumps(msg)
        elif isinstance(error_field, str):
            # Legacy shape: {"error": "message"}.
            message = error_field
        if not message:
            message = data.get("message", "") or ""
    except (json.JSONDecodeError, ValueError, AttributeError):
        pass
    if not message:
        message = body.decode("utf-8", errors="replace")
    return BiometryAPIError(status_code, message, body, code)


def is_not_found(err: BaseException) -> bool:
    """Return True if *err* is a 404 API response."""
    return isinstance(err, BiometryAPIError) and err.status_code == 404


def is_forbidden(err: BaseException) -> bool:
    """Return True if *err* is a 403 API response."""
    return isinstance(err, BiometryAPIError) and err.status_code == 403


def is_unauthorized(err: BaseException) -> bool:
    """Return True if *err* is a 401 API response."""
    return isinstance(err, BiometryAPIError) and err.status_code == 401
