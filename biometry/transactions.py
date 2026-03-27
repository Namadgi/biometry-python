"""Transaction service for the Biometry SDK."""

from __future__ import annotations

import json
from dataclasses import asdict
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from .transport import (
    _apply_call_options,
    _build_base_headers,
    _decode_envelope,
    _json,
    _request,
)
from .types import Transaction, TransactionListRequest

if TYPE_CHECKING:
    from .client import BiometryClient


def _list_request_to_dict(req: TransactionListRequest) -> Dict[str, Any]:
    """Convert a TransactionListRequest to a JSON-safe dict, omitting empty fields."""
    d: Dict[str, Any] = {}
    if req.project_id:
        d["project_id"] = req.project_id
    if req.session_id:
        d["session_id"] = req.session_id
    if req.user_fullname:
        d["user_fullname"] = req.user_fullname
    if req.from_date:
        d["from_date"] = req.from_date
    if req.to_date:
        d["to_date"] = req.to_date
    if req.status_code is not None:
        d["status_code"] = req.status_code
    if req.decision:
        d["decision"] = req.decision
    if req.action:
        d["action"] = req.action
    if req.flag:
        d["flag"] = req.flag
    if req.page:
        d["page"] = req.page
    if req.page_size:
        d["page_size"] = req.page_size
    if req.sort_by:
        d["sort_by"] = req.sort_by
    if req.sort_order:
        d["sort_order"] = req.sort_order
    return d


class TransactionService:
    """Handles transaction queries."""

    def __init__(self, client: BiometryClient) -> None:
        self._c = client

    def list(self, req: TransactionListRequest, **kwargs: Any) -> List[Transaction]:
        """Return transactions matching the given filters."""
        _status, body, _headers = _json(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="POST",
            path="/api-transactions/transactions/list",
            payload=_list_request_to_dict(req),
            timeout=self._c._timeout,
            **kwargs,
        )
        data = _decode_envelope(body)
        if not data or not isinstance(data, list):
            return []
        return [Transaction(**item) for item in data]

    def count(self, req: TransactionListRequest, **kwargs: Any) -> int:
        """Return the number of transactions matching the given filters."""
        _status, body, _headers = _json(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="POST",
            path="/api-transactions/transactions/count",
            payload=_list_request_to_dict(req),
            timeout=self._c._timeout,
            **kwargs,
        )
        data = _decode_envelope(body)
        if isinstance(data, dict):
            return int(data.get("count", 0))
        return 0

    def get_by_session(self, session_id: str, **kwargs: Any) -> List[Transaction]:
        """Return all transactions for a session."""
        headers = _build_base_headers(
            self._c._api_key, self._c._user_agent, self._c._user_fullname
        )
        _apply_call_options(headers, kwargs)

        _status, body, _resp_headers = _request(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="GET",
            path=f"/api-transactions/transactions/sessions/{session_id}",
            extra_headers=headers,
            timeout=self._c._timeout,
        )
        data = _decode_envelope(body)
        if not data or not isinstance(data, list):
            return []
        return [Transaction(**item) for item in data]

    def get_samples(self, id: str, **kwargs: Any) -> Any:
        """Return sample data for a transaction."""
        headers = _build_base_headers(
            self._c._api_key, self._c._user_agent, self._c._user_fullname
        )
        _apply_call_options(headers, kwargs)

        _status, body, _resp_headers = _request(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="GET",
            path=f"/api-transactions/transactions/{id}/samples",
            extra_headers=headers,
            timeout=self._c._timeout,
        )
        return _decode_envelope(body)

    def update_tags(self, id: str, tags: List[str], **kwargs: Any) -> None:
        """Update the tags on a transaction."""
        _json(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="PUT",
            path=f"/api-transactions/transactions/{id}/tags",
            payload={"tags": tags},
            timeout=self._c._timeout,
            **kwargs,
        )

    def flag(self, id: str, flag: str, **kwargs: Any) -> None:
        """Set the fraud flag on a transaction."""
        _json(
            base_url=self._c._base_url,
            api_key=self._c._api_key,
            user_agent=self._c._user_agent,
            user_fullname=self._c._user_fullname,
            method="PUT",
            path=f"/api-transactions/transactions/{id}/flag",
            payload={"flag": flag},
            timeout=self._c._timeout,
            **kwargs,
        )
