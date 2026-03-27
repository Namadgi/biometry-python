"""Face match service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, BinaryIO

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import FileUpload

if TYPE_CHECKING:
    from .client import BiometryClient


class FaceMatchService:
    """Handles face matching between images and videos."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def match(
        self,
        image: BinaryIO,
        image_name: str,
        video: BinaryIO,
        video_name: str,
        **kwargs: Any,
    ) -> BiometryResponse:
        """Compare faces from an uploaded image and video."""
        files = [
            FileUpload(field_name="image", file_name=image_name, content=image),
            FileUpload(field_name="video", file_name=video_name, content=video),
        ]

        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/match-faces",
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )

    def match_with_session_video(
        self,
        image: BinaryIO,
        image_name: str,
        session_id: str,
        **kwargs: Any,
    ) -> BiometryResponse:
        """Compare a face image against the video from a previous session.

        This avoids re-uploading the video.
        """
        files = [
            FileUpload(field_name="image", file_name=image_name, content=image),
        ]

        # Inject the special headers for prefilled video.
        kwargs.setdefault("session_id", session_id)

        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/match-faces",
            files=files,
            timeout=self._c._timeout,
            _extra_headers={"X-Use-Prefilled-Video": "true"},
            **kwargs,
        )
