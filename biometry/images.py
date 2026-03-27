"""Image service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, BinaryIO

from .transport import _decode_envelope, _multipart, _request, _apply_call_options, _build_base_headers
from .types import FileUpload, ImageGetResponse, ImageUploadResponse

if TYPE_CHECKING:
    from .client import BiometryClient


class ImageService:
    """Handles face image upload and retrieval."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def upload(
        self,
        email: str,
        image: BinaryIO,
        file_name: str,
        **kwargs: Any,
    ) -> ImageUploadResponse:
        """Upload a face image associated with an email."""
        fields = {"email": email}
        files = [
            FileUpload(field_name="image", file_name=file_name, content=image),
        ]

        _status, body, _headers = _multipart(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/images",
            fields=fields,
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )
        data = _decode_envelope(body, ImageUploadResponse)
        return data  # type: ignore[return-value]

    def get(self, email: str, **kwargs: Any) -> ImageGetResponse:
        """Retrieve the image URL for a given email."""
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
            path=f"/api-gateway/images/{email}",
            extra_headers=headers,
            timeout=self._c._timeout,
        )
        data = _decode_envelope(body, ImageGetResponse)
        return data  # type: ignore[return-value]
