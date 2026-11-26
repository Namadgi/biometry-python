"""Face match service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import FaceMatchInput, FileUpload
from .v2 import request_field

if TYPE_CHECKING:
    from .client import BiometryClient


class FaceMatchService:
    """Matches a live capture against a client-provided reference image."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def match(self, input: FaceMatchInput, **kwargs: Any) -> BiometryResponse:
        """Compare the live capture against the reference image."""
        files = [
            FileUpload(field_name="reference_image", file_name=input.reference_name, content=input.reference_image),
        ]
        # With use_session_video the gateway reuses the session's liveness video
        # and ignores an uploaded one, so don't upload it.
        if input.video is not None and not input.use_session_video:
            files.append(
                FileUpload(field_name="video", file_name=input.video_name or "capture", content=input.video)
            )
        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/v2/face-match",
            fields=request_field(
                user_id=input.user_id,
                session_id=input.session_id,
                use_session_video=input.use_session_video,
            ),
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )
