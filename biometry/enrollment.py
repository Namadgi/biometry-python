"""Enrollment service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import EnrollFaceInput, EnrollVoiceInput, FileUpload

if TYPE_CHECKING:
    from .client import BiometryClient


class EnrollmentService:
    """Handles face and voice enrollment."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def face(self, input: EnrollFaceInput, **kwargs: Any) -> BiometryResponse:
        """Enroll a face image for recognition."""
        fields: dict[str, str] = {}
        if input.is_document:
            fields["is_document"] = "true"

        files = [
            FileUpload(field_name="face", file_name=input.file_name, content=input.face),
        ]

        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/enroll/face",
            fields=fields,
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )

    def voice(self, input: EnrollVoiceInput, **kwargs: Any) -> BiometryResponse:
        """Enroll voice recordings for recognition."""
        fields: dict[str, str] = {
            "phrase": ",".join(input.phrases),
        }
        if input.vocabulary:
            fields["vocabulary"] = input.vocabulary

        files = [
            FileUpload(field_name="voice", file_name=f.file_name, content=f.content)
            for f in input.files
        ]

        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/enroll/voice",
            fields=fields,
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )
