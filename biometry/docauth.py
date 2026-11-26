"""Document authentication service for the Biometry SDK."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .response import BiometryResponse
from .transport import _multipart_raw
from .types import DocAuthInput, FileUpload
from .v2 import request_field

if TYPE_CHECKING:
    from .client import BiometryClient


class DocAuthService:
    """Handles document authentication."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def check(self, input: DocAuthInput, **kwargs: Any) -> BiometryResponse:
        """Verify the authenticity of a document image (jpg, jpeg, or png)."""
        return _multipart_raw(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            path="/api-gateway/v2/documents/check",
            fields=request_field(
                session_id=input.session_id,
                provider=input.provider,
                mrz_provider=input.mrz_provider,
            ),
            files=[FileUpload(field_name="document", file_name=input.file_name, content=input.document)],
            timeout=self._c._timeout,
            **kwargs,
        )
