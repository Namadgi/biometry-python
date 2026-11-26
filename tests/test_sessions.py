"""Tests for the sessions service."""

from __future__ import annotations

import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, List

from biometry import BiometryClient, EndSessionRequest


class _Handler(BaseHTTPRequestHandler):
    _responses: List[Dict[str, Any]] = []
    _requests: List[Dict[str, Any]] = []

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass

    def _handle(self) -> None:
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length else b""
        _Handler._requests.append({
            "method": self.command,
            "path": self.path,
            "headers": dict(self.headers),
            "body": body,
        })
        if not _Handler._responses:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'{"error":"no response"}')
            return
        resp = _Handler._responses.pop(0)
        self.send_response(resp.get("status", 200))
        self.end_headers()
        payload = resp.get("body", {})
        self.wfile.write(json.dumps(payload).encode() if not isinstance(payload, bytes) else payload)

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle
    do_DELETE = _handle


class TestSessionService(unittest.TestCase):
    server: HTTPServer
    base_url: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.server = HTTPServer(("127.0.0.1", 0), _Handler)
        Thread(target=cls.server.serve_forever, daemon=True).start()
        port = cls.server.server_address[1]
        cls.base_url = f"http://127.0.0.1:{port}"

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()

    def setUp(self) -> None:
        _Handler._responses.clear()
        _Handler._requests.clear()

    def _client(self) -> BiometryClient:
        return BiometryClient("test-api-key", base_url=self.base_url)

    def test_start(self) -> None:
        _Handler._responses.append({
            "status": 200,
            "body": {"data": {"session_id": "session-abc"}, "meta": {}},
        })
        sid = self._client().sessions.start()
        self.assertEqual(sid, "session-abc")
        req = _Handler._requests[0]
        self.assertEqual(req["method"], "POST")
        self.assertTrue(req["path"].endswith("/api-gateway/v2/sessions"))

    def test_end(self) -> None:
        _Handler._responses.append({"status": 200, "body": {"meta": {}}})
        self._client().sessions.end("sess-123", EndSessionRequest(phone_number="+1234567890"))
        req = _Handler._requests[0]
        self.assertEqual(req["method"], "POST")
        self.assertTrue(req["path"].endswith("/api-gateway/v2/sessions/sess-123/end"))
        body = json.loads(req["body"])
        self.assertEqual(body["phone_number"], "+1234567890")


if __name__ == "__main__":
    unittest.main()
