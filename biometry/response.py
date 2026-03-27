"""Response envelope for the Biometry SDK."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Type, TypeVar

T = TypeVar("T")


@dataclass
class BiometryResponse:
    """Full API response envelope.

    Used for endpoints like process-video and match-faces that return
    scoring data alongside the result.
    """

    data: Any = None
    scoring_result: Any = None
    score: float = 0.0
    decision_reasons: List[str] = field(default_factory=list)
    message: str = ""
    headers: Dict[str, str] = field(default_factory=dict)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def decode(self, cls: Type[T]) -> T:
        """Deserialise the *data* field into a dataclass instance of *cls*.

        The class must accept keyword arguments matching the JSON keys.
        """
        if self.data is None:
            raise ValueError("response contains no data")
        if isinstance(self.data, dict):
            return cls(**self.data)  # type: ignore[call-arg]
        raise TypeError(f"cannot decode data of type {type(self.data).__name__}")

    @property
    def request_id(self) -> str:
        """Return the ``X-Request-Id`` response header value."""
        return self.headers.get("X-Request-Id", "") or self.headers.get("x-request-id", "")

    @property
    def auto_enrolled(self) -> bool:
        """Return True if auto face/voice enrollment was performed."""
        val = self.headers.get("X-Auto-Enroll", "") or self.headers.get("x-auto-enroll", "")
        return val.lower() == "true"

    @property
    def removed_services(self) -> bool:
        """Return True if services were dropped due to missing consent."""
        val = self.headers.get("X-Removed-Services", "") or self.headers.get("x-removed-services", "")
        return val.lower() == "true"

    @classmethod
    def _from_json(cls, body: bytes, headers: Dict[str, str]) -> "BiometryResponse":
        """Build a response from raw JSON bytes and HTTP headers."""
        payload = json.loads(body) if body else {}
        reasons = payload.get("decision_reasons") or []
        return cls(
            data=payload.get("data"),
            scoring_result=payload.get("scoring_result"),
            score=float(payload.get("score", 0)),
            decision_reasons=list(reasons),
            message=payload.get("message", ""),
            headers=headers,
        )
