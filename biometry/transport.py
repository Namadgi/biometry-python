"""Low-level HTTP transport for the Biometry SDK.

Uses only stdlib ``urllib.request`` — no third-party dependencies.
"""

from __future__ import annotations

import io
import json
import uuid
from typing import Any, BinaryIO, Dict, List, Optional, Tuple
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .errors import _parse_api_error
from .response import BiometryResponse
from .types import FileUpload

# Header names used for per-call metadata options.
#
# Note: identity/session/trigger/document-provider/prefilled-video selection are
# NOT headers in API v2 gateway operations — they are fields of the per-call
# input objects (carried in the JSON ``request`` part) and the gateway strips
# the corresponding headers. ``session_id``/``fullname``/``action_trigger``
# remain here only for the non-gateway services (transactions, API keys), which
# are unaffected by the v2 migration.
_CALL_OPTION_HEADERS = {
    "session_id": "X-Session-ID",
    "fullname": "X-User-Fullname",
    "action_trigger": "X-Action-Trigger",
    "device_info": "X-Device-Info",
    "geo_location": "X-Geo-Location",
    "request_tags": "X-Request-Tags",
    "client_app": "X-Client-App",
    "client_version": "X-Client-Version",
}


def _apply_call_options(headers: Dict[str, str], kwargs: Dict[str, Any]) -> None:
    """Mutate *headers* with any recognised call-option kwargs."""
    for kwarg_key, header_name in _CALL_OPTION_HEADERS.items():
        value = kwargs.pop(kwarg_key, None)
        if value is None:
            continue
        if isinstance(value, bool):
            headers[header_name] = "true" if value else "false"
        else:
            headers[header_name] = str(value)


def _build_base_headers(
    api_key: str,
    user_agent: str,
    user_fullname: str,
) -> Dict[str, str]:
    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "User-Agent": user_agent,
    }
    if user_fullname:
        headers["X-User-Fullname"] = user_fullname
    return headers


# ---------------------------------------------------------------------------
# Core request helper
# ---------------------------------------------------------------------------

def _request(
    *,
    base_url: str,
    api_key: str,
    user_agent: str,
    user_fullname: str,
    method: str,
    path: str,
    body: Optional[bytes] = None,
    extra_headers: Optional[Dict[str, str]] = None,
    timeout: float = 30.0,
) -> Tuple[int, bytes, Dict[str, str]]:
    """Execute an HTTP request and return (status, body, headers)."""
    headers = _build_base_headers(api_key, user_agent, user_fullname)
    if extra_headers:
        headers.update(extra_headers)

    url = base_url.rstrip("/") + path
    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req, timeout=timeout) as resp:
            resp_body = resp.read()
            resp_headers = {k: v for k, v in resp.getheaders()}
            return resp.status, resp_body, resp_headers
    except HTTPError as exc:
        resp_body = exc.read()
        raise _parse_api_error(exc.code, resp_body) from None


def _decode_envelope(body: bytes, dst_type: Optional[type] = None) -> Any:
    """Decode the standard ``{"data": ...}`` envelope.

    Returns the decoded *data* field.  If *dst_type* is a dataclass, the
    data dict is unpacked into it.
    """
    if not body:
        return None
    payload = json.loads(body)
    data = payload.get("data")
    if data is None or dst_type is None:
        return data
    if isinstance(data, dict):
        return dst_type(**data)
    return data


# ---------------------------------------------------------------------------
# JSON helper
# ---------------------------------------------------------------------------

def _json(
    *,
    base_url: str,
    api_key: str,
    user_agent: str,
    user_fullname: str,
    method: str,
    path: str,
    payload: Any = None,
    timeout: float = 30.0,
    **kwargs: Any,
) -> Tuple[int, bytes, Dict[str, str]]:
    """Send a JSON-encoded request and return the raw response tuple."""
    extra: Dict[str, str] = {}
    _apply_call_options(extra, kwargs)

    body: Optional[bytes] = None
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        extra["Content-Type"] = "application/json"

    return _request(
        base_url=base_url,
        api_key=api_key,
        user_agent=user_agent,
        user_fullname=user_fullname,
        method=method,
        path=path,
        body=body,
        extra_headers=extra,
        timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Multipart helpers
# ---------------------------------------------------------------------------

def _build_multipart_body(
    fields: Optional[Dict[str, str]],
    files: List[FileUpload],
) -> Tuple[bytes, str]:
    """Build a multipart/form-data body and return (body_bytes, content_type)."""
    boundary = uuid.uuid4().hex
    parts: list[bytes] = []

    if fields:
        for name, value in fields.items():
            parts.append(
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="{name}"\r\n'
                f"\r\n"
                f"{value}\r\n".encode("utf-8")
            )

    for f in files:
        content = f.content.read() if hasattr(f.content, "read") else f.content
        if isinstance(content, str):
            content = content.encode("utf-8")
        parts.append(
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="{f.field_name}"; filename="{f.file_name}"\r\n'
            f"Content-Type: application/octet-stream\r\n"
            f"\r\n".encode("utf-8")
            + content
            + b"\r\n"
        )

    parts.append(f"--{boundary}--\r\n".encode("utf-8"))
    body = b"".join(parts)
    content_type = f"multipart/form-data; boundary={boundary}"
    return body, content_type


def _multipart(
    *,
    base_url: str,
    api_key: str,
    user_agent: str,
    user_fullname: str,
    path: str,
    fields: Optional[Dict[str, str]] = None,
    files: List[FileUpload],
    method: str = "POST",
    timeout: float = 30.0,
    _extra_headers: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> Tuple[int, bytes, Dict[str, str]]:
    """Send a multipart/form-data request and return the raw response tuple."""
    extra: Dict[str, str] = {}
    if _extra_headers:
        extra.update(_extra_headers)
    _apply_call_options(extra, kwargs)

    body, content_type = _build_multipart_body(fields, files)
    extra["Content-Type"] = content_type

    return _request(
        base_url=base_url,
        api_key=api_key,
        user_agent=user_agent,
        user_fullname=user_fullname,
        method=method,
        path=path,
        body=body,
        extra_headers=extra,
        timeout=timeout,
    )


def _bytes(
    *,
    base_url: str,
    api_key: str,
    user_agent: str,
    user_fullname: str,
    method: str,
    path: str,
    timeout: float = 30.0,
    **kwargs: Any,
) -> bytes:
    """Send a request and return the raw response body bytes (for endpoints that
    return a non-JSON payload such as an image's octet-stream)."""
    extra: Dict[str, str] = {}
    _apply_call_options(extra, kwargs)
    _status, body, _headers = _request(
        base_url=base_url,
        api_key=api_key,
        user_agent=user_agent,
        user_fullname=user_fullname,
        method=method,
        path=path,
        extra_headers=extra,
        timeout=timeout,
    )
    return body


def _multipart_raw(
    *,
    base_url: str,
    api_key: str,
    user_agent: str,
    user_fullname: str,
    path: str,
    fields: Optional[Dict[str, str]] = None,
    files: List[FileUpload],
    timeout: float = 30.0,
    _extra_headers: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> BiometryResponse:
    """Send a multipart/form-data POST and return a BiometryResponse envelope."""
    _status, body, headers = _multipart(
        base_url=base_url,
        api_key=api_key,
        user_agent=user_agent,
        user_fullname=user_fullname,
        path=path,
        fields=fields,
        files=files,
        timeout=timeout,
        _extra_headers=_extra_headers,
        **kwargs,
    )
    return BiometryResponse._from_json(body, headers)
