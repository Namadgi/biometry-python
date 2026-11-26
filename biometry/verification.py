"""Verification service for the Biometry SDK.

API v2 splits the v1 process-video call into three focused operations:
liveness, face_verify, and voice_verify.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import FileUpload, LivenessInput, VerifyInput
from .v2 import request_field

if TYPE_CHECKING:
    from .client import BiometryClient


class VerificationService:
    """Handles biometric verification."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def liveness(self, input: LivenessInput, **kwargs: Any) -> BiometryResponse:
        """Run the liveness pipeline on the submitted video."""
        fields = request_field(
            user_id=input.user_id,
            phrase=input.phrase,
            vocabulary=input.vocabulary,
            trigger=input.trigger,
            session_id=input.session_id,
            exclude_services=input.exclude_services,
        )
        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/v2/liveness",
            fields=fields,
            files=[FileUpload(field_name="video", file_name=input.file_name, content=input.video)],
            timeout=self._c._timeout,
            **kwargs,
        )

    def face_verify(self, input: VerifyInput, **kwargs: Any) -> BiometryResponse:
        """Verify the face against the user's enrolled face template."""
        return self._verify("/api-gateway/v2/face-verify", "video", input, **kwargs)

    def voice_verify(self, input: VerifyInput, **kwargs: Any) -> BiometryResponse:
        """Verify the voice against the user's enrolled voice template."""
        return self._verify("/api-gateway/v2/voice-verify", "voice", input, **kwargs)

    def _verify(self, path: str, file_field: str, input: VerifyInput, **kwargs: Any) -> BiometryResponse:
        fields = request_field(
            user_id=input.user_id,
            phrase=input.phrase,
            vocabulary=input.vocabulary,
            session_id=input.session_id,
            use_session_video=input.use_session_video,
        )
        files = []
        # With use_session_video the gateway reuses the session's liveness video
        # and ignores an uploaded one, so don't upload it.
        if input.media is not None and not input.use_session_video:
            files = [FileUpload(field_name=file_field, file_name=input.file_name or "capture", content=input.media)]
        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path=path,
            fields=fields,
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )
