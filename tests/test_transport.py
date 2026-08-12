"""Tests for the low-level transport layer and the v2 gateway services."""

from __future__ import annotations

import io
import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, Dict, List

from biometry import (
    BiometryAPIError,
    BiometryClient,
    BiometryResponse,
    EnrollFaceInput,
    LivenessInput,
    VerificationServices,
    is_forbidden,
    is_not_found,
    is_unauthorized,
)
from biometry.transport import (
    _build_multipart_body,
    _decode_envelope,
    _json,
    _multipart,
    _multipart_raw,
)
from biometry.types import FileUpload


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
    Thread(target=server.serve_forever, daemon=True).start()
    port = server.server_address[1]
    return server, f"http://127.0.0.1:{port}"


class TransportTestCase(unittest.TestCase):
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
        return BiometryClient("test-api-key", base_url=self.base_url, **kw)


class TestDoJSON(TransportTestCase):

    def test_success(self) -> None:
        _Handler._responses.append({"status": 200, "body": {"data": {"id": "123"}, "meta": {}}})
        _status, body, _headers = _json(
            base_url=self.base_url, api_key="test-api-key", user_agent="biometry-python/test",
            user_fullname="", method="POST", path="/test", payload={"key": "val"},
        )
        self.assertEqual(_status, 200)
        req = _Handler._requests[0]
        self.assertEqual(req["headers"].get("Authorization"), "Bearer test-api-key")
        self.assertIn("application/json", req["headers"].get("Content-Type", ""))
        self.assertEqual(_decode_envelope(body), {"id": "123"})

    def test_v2_error_envelope(self) -> None:
        _Handler._responses.append({
            "status": 422,
            "body": {"error": {"code": "face_not_detected", "message": "no face detected"}, "meta": {"request_id": "r9"}},
        })
        with self.assertRaises(BiometryAPIError) as cm:
            _json(base_url=self.base_url, api_key="k", user_agent="t", user_fullname="", method="POST", path="/test")
        self.assertEqual(cm.exception.status_code, 422)
        self.assertEqual(cm.exception.code, "face_not_detected")
        self.assertEqual(cm.exception.message, "no face detected")

    def test_legacy_error_shape(self) -> None:
        _Handler._responses.append({"status": 400, "body": {"error": "bad input"}})
        with self.assertRaises(BiometryAPIError) as cm:
            _json(base_url=self.base_url, api_key="k", user_agent="t", user_fullname="", method="POST", path="/test")
        self.assertEqual(cm.exception.message, "bad input")
        self.assertEqual(cm.exception.code, "")


class TestMultipartRequestPart(TransportTestCase):

    def test_enroll_face_request_part(self) -> None:
        _Handler._responses.append({"status": 200, "body": {"data": {"enrolled": True}, "meta": {}}})
        resp = self._client().enrollment.face(EnrollFaceInput(
            user_id="user-1", face=io.BytesIO(b"img"), file_name="f.jpg", is_document=True,
        ))
        self.assertEqual(resp.data["enrolled"], True)
        req = _Handler._requests[0]
        self.assertTrue(req["path"].endswith("/api-gateway/v2/enrollments/face"))
        raw = req["body"]
        self.assertIn(b'name="request"', raw)
        self.assertIn(b'"user_id": "user-1"', raw)
        self.assertIn(b'"is_document": true', raw)
        self.assertIn(b'name="face"', raw)

    def test_liveness_exclude_services(self) -> None:
        _Handler._responses.append({"status": 200, "body": {"data": {}, "meta": {}}})
        self._client().verification.liveness(LivenessInput(
            user_id="user-1", video=io.BytesIO(b"vid"), file_name="v.mp4", phrase="one two",
            exclude_services=[VerificationServices.VOICE_RECOGNITION],
        ))
        raw = _Handler._requests[0]["body"]
        self.assertIn(b'"exclude": ["voice_recognition"]', raw)
        self.assertIn(b'name="video"', raw)


class TestResponseEnvelope(TransportTestCase):

    def test_decision_and_meta(self) -> None:
        _Handler._responses.append({
            "status": 200,
            "body": {
                "data": {"id": "1"},
                "decision": {"status": "pass", "score": 92.5, "reasons": ["face_match"]},
                "meta": {"request_id": "req-abc-123", "message": "done"},
            },
        })
        files = [FileUpload(field_name="f", file_name="f.bin", content=io.BytesIO(b"data"))]
        resp = _multipart_raw(
            base_url=self.base_url, api_key="k", user_agent="t", user_fullname="", path="/test", files=files,
        )
        self.assertIsInstance(resp, BiometryResponse)
        self.assertEqual(resp.decision.status, "pass")
        self.assertAlmostEqual(resp.decision.score, 92.5)
        self.assertEqual(resp.decision.reasons, ["face_match"])
        self.assertEqual(resp.meta.message, "done")
        self.assertEqual(resp.request_id, "req-abc-123")


class TestReferenceImage(TransportTestCase):

    def test_upload_is_put(self) -> None:
        _Handler._responses.append({"status": 200, "body": {"meta": {}}})
        self._client().images.upload("user-1", io.BytesIO(b"img"), "ref.jpg")
        req = _Handler._requests[0]
        self.assertEqual(req["method"], "PUT")
        self.assertTrue(req["path"].endswith("/api-gateway/v2/users/user-1/reference-image"))

    def test_get_returns_bytes(self) -> None:
        _Handler._responses.append({"status": 200, "body": bytes([0x89, 0x50, 0x4e, 0x47])})
        data = self._client().images.get("user-1")
        self.assertEqual(data, bytes([0x89, 0x50, 0x4e, 0x47]))


class TestCallOptions(TransportTestCase):

    def test_metadata_headers(self) -> None:
        _Handler._responses.append({"status": 200, "body": {"data": "ok", "meta": {}}})
        _json(
            base_url=self.base_url, api_key="k", user_agent="t", user_fullname="", method="POST", path="/test",
            device_info='{"model":"iPhone"}', request_tags="vip,test", client_app="demo",
        )
        req = _Handler._requests[0]
        self.assertEqual(req["headers"].get("X-Device-Info"), '{"model":"iPhone"}')
        self.assertEqual(req["headers"].get("X-Request-Tags"), "vip,test")
        self.assertEqual(req["headers"].get("X-Client-App"), "demo")


class TestErrorPredicates(unittest.TestCase):

    def test_predicates(self) -> None:
        self.assertTrue(is_not_found(BiometryAPIError(404, "x", b"")))
        self.assertTrue(is_forbidden(BiometryAPIError(403, "x", b"")))
        self.assertTrue(is_unauthorized(BiometryAPIError(401, "x", b"")))
        self.assertFalse(is_not_found(BiometryAPIError(400, "x", b"")))
        self.assertFalse(is_not_found(ValueError("nope")))


class TestBuildMultipartBody(unittest.TestCase):

    def test_fields_and_files(self) -> None:
        body, ct = _build_multipart_body(
            {"name": "value"},
            [FileUpload(field_name="f", file_name="f.txt", content=io.BytesIO(b"hello"))],
        )
        self.assertIn("multipart/form-data; boundary=", ct)
        self.assertIn(b"value", body)
        self.assertIn(b"hello", body)


if __name__ == "__main__":
    unittest.main()
