"""Session service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Optional

from .transport import _decode_envelope, _json
from .types import EndSessionRequest

if TYPE_CHECKING:
    from .client import BiometryClient


class SessionService:
    """Handles biometric session lifecycle."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def start(self, **kwargs: Any) -> str:
        """Begin a new biometric session and return the session ID."""
        _status, body, _headers = _json(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="POST",
            path="/api-gateway/v2/sessions",
            timeout=self._c._timeout,
            **kwargs,
        )
        data = _decode_envelope(body)
        if isinstance(data, dict):
            return str(data.get("session_id", ""))
        return ""

    def end(self, session_id: str, req: Optional[EndSessionRequest] = None, **kwargs: Any) -> None:
        """Terminate a session by ID. Pass *req* to run a SIM-swap check."""
        payload = None
        if req is not None and req.phone_number:
            payload = {"phone_number": req.phone_number}
        _json(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="POST",
            path=f"/api-gateway/v2/sessions/{session_id}/end",
            payload=payload,
            timeout=self._c._timeout,
            **kwargs,
        )
