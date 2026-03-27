"""Anti-video-forgery service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, BinaryIO

from .transport import (
    _apply_call_options,
    _build_base_headers,
    _decode_envelope,
    _multipart,
    _request,
)
from .types import AVFInferenceResponse, AVFStatusResponse, FileUpload

if TYPE_CHECKING:
    from .client import BiometryClient


class AVFService:
    """Handles anti-video-forgery inference."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def start_inference(
        self,
        video: BinaryIO,
        video_name: str,
        **kwargs: Any,
    ) -> AVFInferenceResponse:
        """Submit a video for anti-forgery analysis."""
        files = [
            FileUpload(field_name="video", file_name=video_name, content=video),
        ]

        _status, body, _headers = _multipart(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/avf/infer",
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )
        data = _decode_envelope(body, AVFInferenceResponse)
        return data  # type: ignore[return-value]

    def check_status(self, request_id: str, **kwargs: Any) -> AVFStatusResponse:
        """Check the status of an AVF inference request."""
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
            path=f"/api-gateway/avf/status/{request_id}",
            extra_headers=headers,
            timeout=self._c._timeout,
        )
        data = _decode_envelope(body, AVFStatusResponse)
        return data  # type: ignore[return-value]
