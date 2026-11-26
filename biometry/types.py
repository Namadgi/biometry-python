"""Data types for the Biometry SDK.

All types are plain dataclasses with no external dependencies.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, BinaryIO, Dict, List, Optional


# ---------------------------------------------------------------------------
# Session types
# ---------------------------------------------------------------------------

@dataclass
class EndSessionRequest:
    """Request body for ending a session."""
    phone_number: str = ""


# ---------------------------------------------------------------------------
# Verification types
# ---------------------------------------------------------------------------

@dataclass
class LivenessInput:
    """Input for a liveness check (face liveness, active speaker, visual speech)."""
    user_id: str = ""
    video: BinaryIO = None  # type: ignore[assignment]
    file_name: str = ""
    phrase: str = ""
    vocabulary: str = ""
    trigger: str = ""
    session_id: str = ""
    exclude_services: Optional[List[str]] = None


@dataclass
class VerifyInput:
    """Input for face or voice verification against the user's enrolled template."""
    user_id: str = ""
    # Video (face) or audio/video (voice). May be None when use_session_video is True.
    media: Optional[BinaryIO] = None
    file_name: str = ""
    phrase: str = ""
    vocabulary: str = ""
    session_id: str = ""
    use_session_video: bool = False


# ---------------------------------------------------------------------------
# Face-match types
# ---------------------------------------------------------------------------

@dataclass
class FaceMatchInput:
    """Input for a face-match request."""
    user_id: str = ""
    reference_image: BinaryIO = None  # type: ignore[assignment]
    reference_name: str = ""
    # Live capture. May be None when use_session_video is True.
    video: Optional[BinaryIO] = None
    video_name: str = ""
    session_id: str = ""
    use_session_video: bool = False


# ---------------------------------------------------------------------------
# DocAuth input
# ---------------------------------------------------------------------------

@dataclass
class DocAuthInput:
    """Input for a document authenticity check."""
    document: BinaryIO = None  # type: ignore[assignment]
    file_name: str = ""
    session_id: str = ""
    provider: str = ""  # "inhouse" | "idscan"
    mrz_provider: str = ""  # "inhouse" | "idscan"


# ---------------------------------------------------------------------------
# Enrollment types
# ---------------------------------------------------------------------------

@dataclass
class EnrollFaceInput:
    """Input for face enrollment."""
    user_id: str = ""
    face: BinaryIO = None  # type: ignore[assignment]
    file_name: str = ""
    is_document: bool = False


@dataclass
class EnrollVoiceInput:
    """Input for voice enrollment."""
    user_id: str = ""
    voice: BinaryIO = None  # type: ignore[assignment]
    file_name: str = ""
    phrase: str = ""
    vocabulary: str = ""


# ---------------------------------------------------------------------------
# Deepfake types
# ---------------------------------------------------------------------------

@dataclass
class DeepfakeInput:
    """Input for submitting a deepfake check."""
    user_id: str = ""
    video: BinaryIO = None  # type: ignore[assignment]
    file_name: str = ""
    session_id: str = ""


@dataclass
class DeepfakeCheck:
    """State of an asynchronous deepfake check."""
    id: str = ""
    status: str = ""  # pending | processing | completed | failed
    score: Optional[float] = None
    prediction: Optional[str] = None
    message: Optional[str] = None
    created_at: Optional[int] = None  # unix seconds
    completed_at: Optional[int] = None  # unix seconds


# ---------------------------------------------------------------------------
# Consent types
# ---------------------------------------------------------------------------

@dataclass
class UserConsents:
    """The user's authorization and storage consent."""
    user_id: str = ""
    authorization: bool = False
    storage: bool = False


@dataclass
class ConsentApproval:
    """A user's consent approval."""
    id: str = ""
    consent_version_id: str = ""
    user_id: str = ""
    is_approved: bool = False
    created_at: str = ""


# ---------------------------------------------------------------------------
# Transaction types
# ---------------------------------------------------------------------------

@dataclass
class TransactionDevice:
    """Device information from a transaction."""
    device_type: str = ""
    device_os: str = ""


@dataclass
class DecisionChange:
    """A change in transaction decision."""
    from_decision: str = ""
    to: str = ""
    reason: str = ""
    changed_by: str = ""
    changed_at: str = ""


@dataclass
class Geo:
    """Geographic location data."""
    ip: str = ""
    lat: float = 0.0
    lng: float = 0.0
    country: str = ""
    city: str = ""


@dataclass
class Transaction:
    """A biometric transaction record."""
    id: str = ""
    session_id: str = ""
    flag: str = ""
    device: Optional[TransactionDevice] = None
    project_id: str = ""
    api_key_id: str = ""
    status_code: int = 0
    is_success: bool = False
    body_byte_size: int = 0
    used_services: List[str] = field(default_factory=list)
    received_at: str = ""
    answered_at: str = ""
    action: str = ""
    app_version: str = ""
    duration: int = 0
    decision: str = ""
    decision_history: List[DecisionChange] = field(default_factory=list)
    geo: Optional[Geo] = None
    tags: List[str] = field(default_factory=list)
    input_metadata: Any = None
    output_metadata: Any = None
    rules_version: int = 0


@dataclass
class TransactionListRequest:
    """Filters for listing transactions."""
    project_id: str = ""
    session_id: str = ""
    user_fullname: str = ""
    from_date: str = ""
    to_date: str = ""
    status_code: Optional[int] = None
    decision: str = ""
    action: str = ""
    flag: str = ""
    page: int = 0
    page_size: int = 0
    sort_by: str = ""
    sort_order: str = ""


# ---------------------------------------------------------------------------
# API Key types
# ---------------------------------------------------------------------------

@dataclass
class APIKeyInfo:
    """Information about an API key."""
    id: str = ""
    project_id: str = ""
    name: str = ""
    state: str = ""
    selected_services: List[str] = field(default_factory=list)
    created_at: str = ""
    expires_at: str = ""


# ---------------------------------------------------------------------------
# DocAuth types
# ---------------------------------------------------------------------------

@dataclass
class MRZValidation:
    """MRZ check results."""
    has_mrz: bool = False
    raw_mrz: str = ""
    check_digits_valid: bool = False
    fields_match: bool = False
    discrepancies: List[str] = field(default_factory=list)
    validation_performed: bool = False


@dataclass
class DocAuthInfo:
    """Extracted document information."""
    document_type: str = ""
    country_code: str = ""
    nationality_code: str = ""
    nationality_name: str = ""
    sex: str = ""
    first_name: str = ""
    father_name: str = ""
    last_name: str = ""
    expiry_date: str = ""
    document_number: str = ""
    birth_date: str = ""
    portrait_photo: str = ""
    signature: str = ""
    document_category: str = ""
    issuing_state: str = ""
    front_document_type_id: str = ""
    contains_rfid: bool = False
    face_image_base64: str = ""
    current_result: str = ""
    mrz_validation: Optional[MRZValidation] = None


# ---------------------------------------------------------------------------
# File upload helper
# ---------------------------------------------------------------------------

@dataclass
class FileUpload:
    """A file to be uploaded via multipart."""
    field_name: str = ""
    file_name: str = ""
    content: BinaryIO = None  # type: ignore[assignment]
