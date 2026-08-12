"""Response envelope for the Biometry SDK."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")


@dataclass
class Decision:
    """Scoring decision computed for a request when a scoring system applies."""

    status: str = ""
    score: Optional[float] = None
    reasons: List[str] = field(default_factory=list)


@dataclass
class ResponseMeta:
    """Response metadata attached to every API v2 response."""

    request_id: str = ""
    message: str = ""


@dataclass
class BiometryResponse:
    """Full API v2 success envelope.

    Used for verification endpoints (liveness, face-verify, voice-verify,
    face-match, documents/check) that may carry a scoring decision alongside
    the raw service data.
    """

    data: Any = None
    decision: Optional[Decision] = None
    meta: ResponseMeta = field(default_factory=ResponseMeta)
    headers: Dict[str, str] = field(default_factory=dict)

    def decode(self, cls: Type[T]) -> T:
        """Deserialise the *data* field into a dataclass instance of *cls*."""
        if self.data is None:
            raise ValueError("response contains no data")
        if isinstance(self.data, dict):
            return cls(**self.data)  # type: ignore[call-arg]
        raise TypeError(f"cannot decode data of type {type(self.data).__name__}")

    @property
    def request_id(self) -> str:
        """Return the request ID, preferring the envelope meta then the header."""
        if self.meta.request_id:
            return self.meta.request_id
        return self.headers.get("X-Request-Id", "") or self.headers.get("x-request-id", "")

    @classmethod
    def _from_json(cls, body: bytes, headers: Dict[str, str]) -> "BiometryResponse":
        """Build a response from raw JSON bytes and HTTP headers."""
        payload = json.loads(body) if body else {}
        decision_raw = payload.get("decision")
        decision = None
        if isinstance(decision_raw, dict):
            decision = Decision(
                status=decision_raw.get("status", ""),
                score=decision_raw.get("score"),
                reasons=list(decision_raw.get("reasons") or []),
            )
        meta_raw = payload.get("meta") or {}
        meta = ResponseMeta(
            request_id=meta_raw.get("request_id", ""),
            message=meta_raw.get("message", ""),
        )
        return cls(
            data=payload.get("data"),
            decision=decision,
            meta=meta,
            headers=headers,
        )
