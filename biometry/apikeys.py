"""API key service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .transport import (
    _apply_call_options,
    _build_base_headers,
    _decode_envelope,
    _request,
)
from .types import APIKeyInfo

if TYPE_CHECKING:
    from .client import BiometryClient


class APIKeyService:
    """Manages API keys via the public endpoints."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def mint(self, **kwargs: Any) -> APIKeyInfo:
        """Create a new API key."""
        headers = _build_base_headers(
            self._c._api_key, self._c._user_agent, self._c._user_fullname
        )
        _apply_call_options(headers, kwargs)

        _status, body, _resp_headers = _request(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="POST",
            path="/api-projects/public/apikeys",
            extra_headers=headers,
            timeout=self._c._timeout,
        )
        data = _decode_envelope(body, APIKeyInfo)
        return data  # type: ignore[return-value]

    def revoke(self, key_id: str, **kwargs: Any) -> None:
        """Delete an API key by ID."""
        headers = _build_base_headers(
            self._c._api_key, self._c._user_agent, self._c._user_fullname
        )
        _apply_call_options(headers, kwargs)

        _request(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="DELETE",
            path=f"/api-projects/public/apikeys/{key_id}",
            extra_headers=headers,
            timeout=self._c._timeout,
        )

    def info(self, **kwargs: Any) -> APIKeyInfo:
        """Return information about the current API key."""
        headers = _build_base_headers(
            self._c._api_key, self._c._user_agent, self._c._user_fullname
        )
        _apply_call_options(headers, kwargs)

        _status, body, _resp_headers = _request(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="GET",
            path="/api-projects/public/apikeys",
            extra_headers=headers,
            timeout=self._c._timeout,
        )
        data = _decode_envelope(body, APIKeyInfo)
        return data  # type: ignore[return-value]
