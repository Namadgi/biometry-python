"""Reference image service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, BinaryIO

from .transport import _bytes, _multipart
from .types import FileUpload

if TYPE_CHECKING:
    from .client import BiometryClient


class ImageService:
    """Manages a user's reference image (used by face-match)."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def upload(self, user_id: str, image: BinaryIO, file_name: str, **kwargs: Any) -> None:
        """Store the reference image for the given user.

        Requires an approved consent for the user.
        """
        _multipart(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path=f"/api-gateway/v2/users/{user_id}/reference-image",
            files=[FileUpload(field_name="image", file_name=file_name, content=image)],
            method="PUT",
            timeout=self._c._timeout,
            **kwargs,
        )

    def get(self, user_id: str, **kwargs: Any) -> bytes:
        """Download the stored reference image bytes for the given user."""
        return _bytes(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="GET",
            path=f"/api-gateway/v2/users/{user_id}/reference-image",
            timeout=self._c._timeout,
            **kwargs,
        )
