"""Root Biometry SDK client."""

from __future__ import annotations

from .apikeys import APIKeyService
from .consent import ConsentService
from .deepfake import DeepfakeService
from .docauth import DocAuthService
from .enrollment import EnrollmentService
from .facematch import FaceMatchService
from .images import ImageService
from .sessions import SessionService
from .transactions import TransactionService
from .verification import VerificationService

# Defaults
DEFAULT_BASE_URL = "https://api.biometrysolutions.com"
DEFAULT_TIMEOUT = 30.0
_USER_AGENT = "biometry-python/0.2.0"


class BiometryClient:
    """Root Biometry SDK client, targeting the Biometry API v2 gateway
    (/api-gateway/v2).

    Exposes service-specific sub-clients as public attributes. Biometric
    operations identify the end user with an opaque, customer-provided
    ``user_id`` supplied on each call's input (not a header).

    Example::

        client = BiometryClient("your-api-key-jwt")
        session_id = client.sessions.start()
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        user_agent: str = _USER_AGENT,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        # Identity is per-call (user_id in the request part); no default header.
        self._user_fullname = ""
        self._user_agent = user_agent
        self._timeout = timeout

        # Service sub-clients
        self.sessions = SessionService(self)
        self.verification = VerificationService(self)
        self.enrollment = EnrollmentService(self)
        self.face_match = FaceMatchService(self)
        self.doc_auth = DocAuthService(self)
        self.consents = ConsentService(self)
        self.images = ImageService(self)
        self.deepfake = DeepfakeService(self)
        self.transactions = TransactionService(self)
        self.api_keys = APIKeyService(self)
