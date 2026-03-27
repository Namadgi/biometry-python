"""Tests for the low-level transport layer and shared helpers."""

from __future__ import annotations

import io
import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock, patch

from biometry import (
    BiometryAPIError,
    BiometryClient,
    BiometryResponse,
    is_forbidden,
    is_not_found,
    is_unauthorized,
)
from biometry.transport import (
    _apply_call_options,
    _build_multipart_body,
    _decode_envelope,
    _json,
    _multipart,
    _multipart_raw,
    _request,
)
from biometry.types import FileUpload


# ---------------------------------------------------------------------------
# Helpers — tiny HTTP server for integration-style tests
# ---------------------------------------------------------------------------

class _Handler(BaseHTTPRequestHandler):
    """Programmable handler — set _responses on the class before use."""

    _responses: List[Dict[str, Any]] = []
    _requests: List[Dict[str, Any]] = []

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass  # silence stderr

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
            self.wfile.write(b'{"error":"no response configured"}')
            return
        resp = _Handler._responses.pop(0)
        self.send_response(resp.get("status", 200))
        for k, v in resp.get("headers", {}).items():
            self.send_header(k, v)
        self.end_headers()
        payload = resp.get("body", {})
        if isinstance(payload, bytes):
            self.wfile.write(payload)
        else:
            self.wfile.write(json.dumps(payload).encode())

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle
    do_DELETE = _handle


def _start_server() -> tuple:
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    port = server.server_address[1]
    return server, f"http://127.0.0.1:{port}"


class TransportTestCase(unittest.TestCase):
    """Base class that spins up a local HTTP server per test."""

    server: HTTPServer
    base_url: str

    @classmethod
    def setUpClass(cls) -> None:
        cls.server, cls.base_url = _start_server()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()

    def setUp(self) -> None:
        _Handler._responses.clear()
        _Handler._requests.clear()

    def _client(self, **kw: Any) -> BiometryClient:
        return BiometryClient(
            "test-api-key",
            base_url=self.base_url,
            user_fullname="Test User",
            **kw,
        )


# ---------------------------------------------------------------------------
# Transport tests
# ---------------------------------------------------------------------------

class TestDoJSON(TransportTestCase):

    def test_success(self) -> None:
        _Handler._responses.append({
            "status": 200,
            "body": {"data": {"id": "123"}, "message": "ok"},
        })
        _status, body, _headers = _json(
            base_url=self.base_url,
            api_key="test-api-key",
            user_agent="biometry-python/test",
            user_fullname="Test User",
            method="POST",
            path="/test",
            payload={"key": "val"},
        )
        self.assertEqual(_status, 200)
        req = _Handler._requests[0]
        self.assertEqual(req["headers"].get("Authorization"), "Bearer test-api-key")
        self.assertEqual(req["headers"].get("X-User-Fullname"), "Test User")
        self.assertIn("application/json", req["headers"].get("Content-Type", ""))
        data = _decode_envelope(body)
        self.assertEqual(data, {"id": "123"})

    def test_api_error(self) -> None:
        _Handler._responses.append({
            "status": 400,
            "body": {"message": "bad input"},
        })
        with self.assertRaises(BiometryAPIError) as cm:
            _json(
                base_url=self.base_url,
                api_key="test-api-key",
                user_agent="test",
                user_fullname="",
                method="POST",
                path="/test",
            )
        self.assertEqual(cm.exception.status_code, 400)
        self.assertEqual(cm.exception.message, "bad input")

    def test_nil_dst(self) -> None:
        _Handler._responses.append({
            "status": 200,
            "body": {"message": "ok"},
        })
        _status, body, _headers = _json(
            base_url=self.base_url,
            api_key="test-api-key",
            user_agent="test",
            user_fullname="",
            method="POST",
            path="/test",
        )
        self.assertEqual(_status, 200)


class TestDoMultipart(TransportTestCase):

    def test_success(self) -> None:
        _Handler._responses.append({
            "status": 200,
            "body": {"data": {"result": "ok"}},
        })
        files = [FileUpload(field_name="upload", file_name="test.bin", content=io.BytesIO(b"file-content"))]
        _status, body, _headers = _multipart(
            base_url=self.base_url,
            api_key="test-api-key",
            user_agent="test",
            user_fullname="",
            path="/upload",
            fields={"field1": "value1"},
            files=files,
        )
        self.assertEqual(_status, 200)
        req = _Handler._requests[0]
        self.assertIn("multipart/form-data", req["headers"].get("Content-Type", ""))
        data = _decode_envelope(body)
        self.assertEqual(data, {"result": "ok"})


class TestResponseHeaders(TransportTestCase):

    def test_response_envelope(self) -> None:
        _Handler._responses.append({
            "status": 200,
            "headers": {
                "X-Request-Id": "req-abc-123",
                "X-Auto-Enroll": "true",
                "X-Removed-Services": "true",
            },
            "body": {
                "data": {"id": "1"},
                "scoring_result": {"status": "approved"},
                "score": 92.5,
                "decision_reasons": ["face_match"],
                "message": "done",
            },
        })
        files = [FileUpload(field_name="f", file_name="f.bin", content=io.BytesIO(b"data"))]
        resp = _multipart_raw(
            base_url=self.base_url,
            api_key="test-api-key",
            user_agent="test",
            user_fullname="",
            path="/test",
            files=files,
        )
        self.assertIsInstance(resp, BiometryResponse)
        self.assertEqual(resp.request_id, "req-abc-123")
        self.assertTrue(resp.auto_enrolled)
        self.assertTrue(resp.removed_services)
        self.assertAlmostEqual(resp.score, 92.5)
        self.assertEqual(resp.decision_reasons, ["face_match"])
        self.assertEqual(resp.message, "done")


class TestCallOptions(TransportTestCase):

    def test_request_headers(self) -> None:
        _Handler._responses.append({"status": 200, "body": {"data": "ok"}})
        _json(
            base_url=self.base_url,
            api_key="test-api-key",
            user_agent="test",
            user_fullname="Default",
            method="POST",
            path="/test",
            fullname="Override Name",
            session_id="sess-123",
            inhouse_docauth=False,
            inhouse_mrz=True,
            device_info='{"model":"iPhone"}',
            request_tags="vip,test",
        )
        req = _Handler._requests[0]
        self.assertEqual(req["headers"].get("X-User-Fullname"), "Override Name")
        self.assertEqual(req["headers"].get("X-Session-Id"), "sess-123")
        self.assertEqual(req["headers"].get("X-Inhouse-Docauth"), "false")
        self.assertEqual(req["headers"].get("X-Inhouse-Mrz"), "true")
        self.assertEqual(req["headers"].get("X-Device-Info"), '{"model":"iPhone"}')
        self.assertEqual(req["headers"].get("X-Request-Tags"), "vip,test")


class TestErrorPredicates(unittest.TestCase):

    def test_is_not_found(self) -> None:
        err = BiometryAPIError(404, "not found", b"")
        self.assertTrue(is_not_found(err))
        self.assertFalse(is_forbidden(err))
        self.assertFalse(is_unauthorized(err))

    def test_is_forbidden(self) -> None:
        err = BiometryAPIError(403, "forbidden", b"")
        self.assertTrue(is_forbidden(err))
        self.assertFalse(is_not_found(err))

    def test_is_unauthorized(self) -> None:
        err = BiometryAPIError(401, "unauthorized", b"")
        self.assertTrue(is_unauthorized(err))
        self.assertFalse(is_not_found(err))

    def test_not_matching(self) -> None:
        err = BiometryAPIError(400, "bad request", b"")
        self.assertFalse(is_not_found(err))
        self.assertFalse(is_forbidden(err))
        self.assertFalse(is_unauthorized(err))

    def test_non_api_error(self) -> None:
        err = ValueError("nope")
        self.assertFalse(is_not_found(err))


class TestBuildMultipartBody(unittest.TestCase):

    def test_fields_and_files(self) -> None:
        body, ct = _build_multipart_body(
            {"name": "value"},
            [FileUpload(field_name="f", file_name="f.txt", content=io.BytesIO(b"hello"))],
        )
        self.assertIn("multipart/form-data; boundary=", ct)
        self.assertIn(b"name", body)
        self.assertIn(b"value", body)
        self.assertIn(b"hello", body)


if __name__ == "__main__":
    unittest.main()
