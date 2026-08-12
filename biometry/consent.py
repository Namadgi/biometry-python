"""Consent service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, List

from .transport import _apply_call_options, _build_base_headers, _decode_envelope, _request
from .types import ConsentApproval

if TYPE_CHECKING:
    from .client import BiometryClient


class ConsentService:
    """Handles consent approvals (API-key-authenticated only)."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def approve(self, consent_id: str, user_id: str, **kwargs: Any) -> None:
        """Approve a consent for a user."""
        headers = _build_base_headers(
            self._c._api_key, self._c._user_agent, self._c._user_fullname
        )
        _apply_call_options(headers, kwargs)

        _request(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="POST",
            path=f"/api-gateway/v2/consents/{consent_id}/approve/{user_id}",
            extra_headers=headers,
            timeout=self._c._timeout,
        )

    def my_approvals(self, user_id: str, **kwargs: Any) -> List[ConsentApproval]:
        """Return the consent approvals for a user."""
        headers = _build_base_headers(
            self._c._api_key, self._c._user_agent, self._c._user_fullname
        )
        _apply_call_options(headers, kwargs)

        _status, body, _headers = _request(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="GET",
            path=f"/api-gateway/v2/consents/my-approvals/{user_id}",
            extra_headers=headers,
            timeout=self._c._timeout,
        )
        data = _decode_envelope(body)
        if isinstance(data, list):
            return [ConsentApproval(**item) for item in data]
        return []
