"""Biometry Python SDK — zero-dependency client for the Biometry platform APIs."""

from .client import BiometryClient, DEFAULT_BASE_URL, DEFAULT_TIMEOUT
from .errors import BiometryAPIError, is_forbidden, is_not_found, is_unauthorized
from .response import BiometryResponse
from .types import (
    APIKeyInfo,
    AVFInferenceResponse,
    AVFStatusResponse,
    ConsentApproval,
    DecisionChange,
    DocAuthInfo,
    EndSessionRequest,
    EnrollFaceInput,
    EnrollVoiceInput,
    FileUpload,
    Geo,
    ImageGetResponse,
    ImageUploadResponse,
    MRZValidation,
    ProcessVideoInput,
    Transaction,
    TransactionDevice,
    TransactionListRequest,
    VoiceFile,
)

__all__ = [
    "BiometryClient",
    "BiometryAPIError",
    "BiometryResponse",
    "DEFAULT_BASE_URL",
    "DEFAULT_TIMEOUT",
    "is_not_found",
    "is_forbidden",
    "is_unauthorized",
    # Types
    "APIKeyInfo",
    "AVFInferenceResponse",
    "AVFStatusResponse",
    "ConsentApproval",
    "DecisionChange",
    "DocAuthInfo",
    "EndSessionRequest",
    "EnrollFaceInput",
    "EnrollVoiceInput",
    "FileUpload",
    "Geo",
    "ImageGetResponse",
    "ImageUploadResponse",
    "MRZValidation",
    "ProcessVideoInput",
    "Transaction",
    "TransactionDevice",
    "TransactionListRequest",
    "VoiceFile",
]

__version__ = "0.1.0"
