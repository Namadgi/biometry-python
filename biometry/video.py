"""Video service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import FileUpload, ProcessVideoInput

if TYPE_CHECKING:
    from .client import BiometryClient


class VideoService:
    """Handles biometric video processing."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def process(self, input: ProcessVideoInput, **kwargs: Any) -> BiometryResponse:
        """Send a video for biometric verification.

        Returns the full :class:`BiometryResponse` envelope which includes
        scoring results, score, and decision reasons.
        """
        fields = {"phrase": input.phrase}
        if input.vocabulary:
            fields["vocabulary"] = input.vocabulary
        if input.trigger:
            fields["trigger"] = input.trigger

        files = [
            FileUpload(field_name="video", file_name=input.video_name, content=input.video),
        ]

        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/process-video",
            fields=fields,
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )
