"""Biometry Python SDK — zero-dependency client for the Biometry platform APIs (API v2)."""

from .client import BiometryClient, DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from .errors import BiometryAPIError, is_forbidden, is_not_found, is_unauthorized
from .response import BiometryResponse, Decision, ResponseMeta
from .v2 import VerificationServices, request_field
from .types import (
    APIKeyInfo,
    ConsentApproval,
    UserConsents,
    DecisionChange,
    DeepfakeCheck,
    DeepfakeInput,
    DocAuthInfo,
    DocAuthInput,
    EndSessionRequest,
    EnrollFaceInput,
    EnrollVoiceInput,
    FaceMatchInput,
    FileUpload,
    Geo,
    LivenessInput,
    MRZValidation,
    Transaction,
    TransactionDevice,
    TransactionListRequest,
    VerifyInput,
)

__all__ = [
    "BiometryClient",
    "BiometryAPIError",
    "BiometryResponse",
    "Decision",
    "ResponseMeta",
    "VerificationServices",
    "request_field",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "is_not_found",
    "is_forbidden",
    "is_unauthorized",
    # Types
    "APIKeyInfo",
    "ConsentApproval",
    "UserConsents",
    "DecisionChange",
    "DeepfakeCheck",
    "DeepfakeInput",
    "DocAuthInfo",
    "DocAuthInput",
    "EndSessionRequest",
    "EnrollFaceInput",
    "EnrollVoiceInput",
    "FaceMatchInput",
    "FileUpload",
    "Geo",
    "LivenessInput",
    "MRZValidation",
    "Transaction",
    "TransactionDevice",
    "TransactionListRequest",
    "VerifyInput",
]

__version__ = "0.2.0"
