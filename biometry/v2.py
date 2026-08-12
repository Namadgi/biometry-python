"""Helpers for building API v2 gateway requests."""

from __future__ import annotations

import json
from typing import Dict, List, Optional


class VerificationServices:
    """Services that can be excluded from the liveness pipeline."""

    FACE_LIVENESS = "face_liveness_detection"
    ACTIVE_SPEAKER = "active_speaker_detection"
    VISUAL_SPEECH = "visual_speech_recognition"
    FACE_RECOGNITION = "face_recognition"
    VOICE_RECOGNITION = "voice_recognition"


def request_field(
    *,
    user_id: Optional[str] = None,
    session_id: Optional[str] = None,
    phrase: Optional[str] = None,
    vocabulary: Optional[str] = None,
    trigger: Optional[str] = None,
    use_session_video: Optional[bool] = None,
    provider: Optional[str] = None,
    mrz_provider: Optional[str] = None,
    is_document: Optional[bool] = None,
    exclude_services: Optional[List[str]] = None,
) -> Dict[str, str]:
    """Build the multipart ``request`` form field for API v2 gateway endpoints.

    The gateway decodes this JSON part and derives the internal identity,
    session, and service-selection headers from it (those headers are stripped
    from the incoming request, so this is the only supported way to pass them).
    Empty/false values are dropped to keep the payload lean.
    """
    req: Dict[str, object] = {}
    for key, value in (
        ("user_id", user_id),
        ("session_id", session_id),
        ("phrase", phrase),
        ("vocabulary", vocabulary),
        ("trigger", trigger),
        ("use_session_video", use_session_video),
        ("provider", provider),
        ("mrz_provider", mrz_provider),
        ("is_document", is_document),
    ):
        if value is None or value == "" or value is False:
            continue
        req[key] = value
    if exclude_services:
        req["services"] = {"exclude": exclude_services}
    return {"request": json.dumps(req)}
