"""Consent service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Dict, List, Optional
from urllib.parse import quote

from .transport import _apply_call_options, _build_base_headers, _decode_envelope, _json, _request
from .types import ConsentApproval, UserConsents

if TYPE_CHECKING:
    from .client import BiometryClient


class ConsentService:
    """Records user consent (``give``, ``revoke``, ``status``) and custom
    consent template approvals (``approve``, ``my_approvals``)."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def give(
        self,
        user_id: str,
        *,
        authorization: bool = True,
        storage: bool = True,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> UserConsents:
        """Record that the user consents to Biometry processing
        (*authorization*) and/or storing (*storage*) their biometric data:
        ``PUT /v2/users/{user_id}/consents``. Both default to ``True``.

        Face and voice enrollment require both consents and fail with 403
        without them; ``images.upload`` requires authorization consent.
        Collect the user's agreement in your app first. Giving a consent the
        user already gave is a no-op.

        *session_id* optionally links the consent to a session, so it shows
        with that session in the Console.

        Returns the user's consent state after the change. Raises
        ``ValueError`` before any request if both are ``False``.
        """
        return self._set(user_id, True, authorization, storage, session_id, kwargs)

    def revoke(
        self,
        user_id: str,
        *,
        authorization: bool = True,
        storage: bool = True,
        session_id: Optional[str] = None,
        **kwargs: Any,
    ) -> UserConsents:
        """Withdraw the user's *authorization* and/or *storage* consent (both
        default to ``True``, i.e. withdraw both). Enrollment fails with 403
        afterwards until ``give`` is called again. Revoking a consent the user
        never gave is a no-op.

        Returns the user's consent state after the change. Raises
        ``ValueError`` before any request if both are ``False``.
        """
        return self._set(user_id, False, authorization, storage, session_id, kwargs)

    def status(self, user_id: str, **kwargs: Any) -> UserConsents:
        """Return the user's authorization and storage consent:
        ``GET /v2/users/{user_id}/consents``. A user who never gave consent
        has both ``False``."""
        return self._send("GET", user_id, None, kwargs)

    def _set(
        self,
        user_id: str,
        given: bool,
        authorization: bool,
        storage: bool,
        session_id: Optional[str],
        kwargs: Dict[str, Any],
    ) -> UserConsents:
        if not authorization and not storage:
            raise ValueError("at least one of authorization or storage must be True")
        payload: Dict[str, Any] = {}
        if authorization:
            payload["authorization"] = given
        if storage:
            payload["storage"] = given
        if session_id:
            payload["session_id"] = session_id
        return self._send("PUT", user_id, payload, kwargs)

    def _send(
        self, method: str, user_id: str, payload: Optional[Dict[str, Any]], kwargs: Dict[str, Any]
    ) -> UserConsents:
        _status, body, _headers = _json(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method=method,
            path=f"/api-gateway/v2/users/{quote(user_id, safe='')}/consents",
            payload=payload,
            timeout=self._c._timeout,
            **kwargs,
        )
        data = _decode_envelope(body)
        if not isinstance(data, dict):
            data = {}
        return UserConsents(
            user_id=str(data.get("user_id", "")),
            authorization=bool(data.get("authorization", False)),
            storage=bool(data.get("storage", False)),
        )

    def approve(self, consent_id: str, user_id: str, **kwargs: Any) -> None:
        """Record the user's approval of one of your project's custom consent
        templates. It does not give the authorization and storage consent
        that enrollment requires; use ``give`` for that."""
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
        """Return the user's custom consent template approvals."""
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
