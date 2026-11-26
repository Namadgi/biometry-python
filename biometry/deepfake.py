"""Deepfake / anti-video-forgery service for the Biometry SDK."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, Dict

from .transport import _bytes, _multipart, _seg
from .types import DeepfakeCheck, DeepfakeInput, FileUpload
from .v2 import request_field

if TYPE_CHECKING:
    from .client import BiometryClient

_CHECK_FIELDS = {"id", "status", "score", "prediction", "message", "created_at", "completed_at"}


def _to_check(data: Any) -> DeepfakeCheck:
    """Build a DeepfakeCheck from the envelope data, ignoring unknown keys."""
    if not isinstance(data, dict):
        return DeepfakeCheck()
    return DeepfakeCheck(**{k: v for k, v in data.items() if k in _CHECK_FIELDS})


class DeepfakeService:
    """Handles asynchronous deepfake / anti-video-forgery checks."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def submit(self, input: DeepfakeInput, **kwargs: Any) -> DeepfakeCheck:
        """Send a video for deepfake analysis and return the created check."""
        _status, body, _headers = _multipart(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/v2/deepfake/checks",
            fields=request_field(user_id=input.user_id, session_id=input.session_id),
            files=[FileUpload(field_name="video", file_name=input.file_name, content=input.video)],
            timeout=self._c._timeout,
            **kwargs,
        )
        payload = json.loads(body) if body else {}
        return _to_check(payload.get("data"))

    def status(self, request_id: str, **kwargs: Any) -> DeepfakeCheck:
        """Retrieve the current state and results of a deepfake check."""
        body = _bytes(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="GET",
            path=f"/api-gateway/v2/deepfake/checks/{_seg(request_id)}",
            timeout=self._c._timeout,
            **kwargs,
        )
        payload = json.loads(body) if body else {}
        return _to_check(payload.get("data"))
