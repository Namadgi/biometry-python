"""Tests for the v2 user consent calls (give / revoke / status)."""

from __future__ import annotations

import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, List

from biometry import BiometryAPIError, BiometryClient, UserConsents


class _Handler(BaseHTTPRequestHandler):
    _responses: List[Dict[str, Any]] = []
    _requests: List[Dict[str, Any]] = []

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass

    def _handle(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        _Handler._requests.append({
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers),
            "body": body,
        })
        resp = _Handler._responses.pop(0) if _Handler._responses else {"status": 500, "body": {}}
        self.send_response(resp.get("status", 200))
        self.end_headers()
        self.wfile.write(json.dumps(resp.get("body", {})).encode())

    do_GET = _handle
    do_PUT = _handle


def _ok(user_id: str, authorization: bool, storage: bool) -> Dict[str, Any]:
    return {
        "status": 200,
        "body": {
            "data": {"user_id": user_id, "authorization": authorization, "storage": storage},
            "meta": {},
        },
    }


class TestUserConsents(unittest.TestCase):
    server: HTTPServer
    base_url: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base_url = f"http://127.0.0.1:{cls.server.server_address[1]}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()

    def setUp(self) -> None:
        _Handler._responses.clear()
        _Handler._requests.clear()

    def _client(self) -> BiometryClient:
        return BiometryClient("test-api-key", base_url=self.base_url)

    def test_give_defaults_to_both(self) -> None:
        _Handler._responses.append(_ok("user-123", True, True))
        state = self._client().consents.give("user-123")
        self.assertEqual(state, UserConsents(user_id="user-123", authorization=True, storage=True))
        req = _Handler._requests[0]
        self.assertEqual(req["method"], "PUT")
        self.assertEqual(req["path"], "/api-gateway/v2/users/user-123/consents")
        self.assertEqual(req["headers"].get("Content-Type"), "application/json")
        self.assertEqual(json.loads(req["body"]), {"authorization": True, "storage": True})

    def test_revoke_selected_only_with_session(self) -> None:
        _Handler._responses.append(_ok("user-123", True, False))
        state = self._client().consents.revoke("user-123", authorization=False, session_id="sess_1")
        self.assertFalse(state.storage)
        req = _Handler._requests[0]
        self.assertEqual(req["method"], "PUT")
        self.assertEqual(json.loads(req["body"]), {"storage": False, "session_id": "sess_1"})
        # session_id goes in the body, not the legacy X-Session-ID header
        self.assertNotIn("X-Session-Id", req["headers"])

    def test_nothing_selected_sends_no_request(self) -> None:
        consents = self._client().consents
        with self.assertRaises(ValueError):
            consents.give("user-123", authorization=False, storage=False)
        with self.assertRaises(ValueError):
            consents.revoke("user-123", authorization=False, storage=False)
        self.assertEqual(_Handler._requests, [])

    def test_status_encodes_user_id(self) -> None:
        _Handler._responses.append(_ok("a/b", True, False))
        state = self._client().consents.status("a/b")
        self.assertEqual(state, UserConsents(user_id="a/b", authorization=True, storage=False))
        req = _Handler._requests[0]
        self.assertEqual(req["method"], "GET")
        self.assertEqual(req["path"], "/api-gateway/v2/users/a%2Fb/consents")
        self.assertEqual(req["body"], b"")

    def test_api_error(self) -> None:
        _Handler._responses.append({
            "status": 409,
            "body": {"error": {"code": "session_closed", "message": "session is closed"}},
        })
        with self.assertRaises(BiometryAPIError) as ctx:
            self._client().consents.give("user-123", session_id="sess_1")
        self.assertEqual(ctx.exception.status_code, 409)
        self.assertEqual(ctx.exception.code, "session_closed")


if __name__ == "__main__":
    unittest.main()
