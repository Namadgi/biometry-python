"""Root Biometry SDK client."""

from __future__ import annotations

from typing import Optional

from .apikeys import APIKeyService
from .avf import AVFService
from .consent import ConsentService
from .docauth import DocAuthService
from .enrollment import EnrollmentService
from .facematch import FaceMatchService
from .images import ImageService
from .sessions import SessionService
from .transactions import TransactionService
from .video import VideoService

# Defaults
DEFAULT_BASE_URL = "https://api.biometrysolutions.com"
DEFAULT_TIMEOUT = 30.0
_USER_AGENT = "biometry-python/0.1.0"


class BiometryClient:
    """Root Biometry SDK client.

    Exposes service-specific sub-clients as public attributes.

    Example::

        client = BiometryClient("your-api-key-jwt", user_fullname="John Doe")
        session_id = client.sessions.start()
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        user_fullname: str = "",
        user_agent: str = _USER_AGENT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._user_fullname = user_fullname
        self._user_agent = user_agent
        self._timeout = timeout

        # Service sub-clients
        self.sessions = SessionService(self)
        self.video = VideoService(self)
        self.enrollment = EnrollmentService(self)
        self.face_match = FaceMatchService(self)
        self.doc_auth = DocAuthService(self)
        self.consents = ConsentService(self)
        self.images = ImageService(self)
        self.avf = AVFService(self)
        self.transactions = TransactionService(self)
        self.api_keys = APIKeyService(self)
