"""Enrollment service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import EnrollFaceInput, EnrollVoiceInput, FileUpload
from .v2 import request_field

if TYPE_CHECKING:
    from .client import BiometryClient


class EnrollmentService:
    """Handles face and voice enrollment."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def face(self, input: EnrollFaceInput, **kwargs: Any) -> BiometryResponse:
        """Enroll a face image for recognition."""
        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/v2/enrollments/face",
            fields=request_field(user_id=input.user_id, is_document=input.is_document),
            files=[FileUpload(field_name="face", file_name=input.file_name, content=input.face)],
            timeout=self._c._timeout,
            **kwargs,
        )

    def voice(self, input: EnrollVoiceInput, **kwargs: Any) -> BiometryResponse:
        """Enroll a voice recording for recognition."""
        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/v2/enrollments/voice",
            fields=request_field(user_id=input.user_id, phrase=input.phrase, vocabulary=input.vocabulary),
            files=[FileUpload(field_name="voice", file_name=input.file_name, content=input.voice)],
            timeout=self._c._timeout,
            **kwargs,
        )
