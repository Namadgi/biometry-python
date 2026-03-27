"""Document authentication service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, BinaryIO

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import FileUpload

if TYPE_CHECKING:
    from .client import BiometryClient


class DocAuthService:
    """Handles document authentication."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def check(
        self,
        document: BinaryIO,
        file_name: str,
        **kwargs: Any,
    ) -> BiometryResponse:
        """Verify the authenticity of a document image (jpg, jpeg, or png)."""
        files = [
            FileUpload(field_name="document", file_name=file_name, content=document),
        ]

        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/docauth/check",
            files=files,
            timeout=self._c._timeout,
            **kwargs,
        )
