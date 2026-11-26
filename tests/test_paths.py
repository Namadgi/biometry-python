"""Path segments are percent-encoded; use_session_video does not upload media."""

from __future__ import annotations

import io
import json
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer
from threading import Thread
from typing import Any, ClassVar, Dict, List

from biometry import BiometryClient, FaceMatchInput, VerifyInput


class _Handler(BaseHTTPRequestHandler):
    _requests: ClassVar[List[Dict[str, Any]]] = []
    _reply: ClassVar[Any] = {}

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A002
        pass

    def _handle(self) -> None:
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length) if length else b""
        _Handler._requests.append({"path": self.path, "body": body})
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({"data": _Handler._reply, "meta": {}}).encode())

    do_GET = _handle
    do_POST = _handle
    do_PUT = _handle


class TestPaths(unittest.TestCase):
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
        _Handler._requests.clear()
        _Handler._reply = {}

    def _client(self) -> BiometryClient:
        return BiometryClient("k", base_url=self.base_url)

    def _last_path(self) -> str:
        return _Handler._requests[-1]["path"]

    def test_path_segments_are_encoded(self) -> None:
        c = self._client()
        c.sessions.end("a/b?c")
        self.assertEqual(self._last_path(), "/api-gateway/v2/sessions/a%2Fb%3Fc/end")
        c.consents.approve("t/1", "u?1")
        self.assertEqual(self._last_path(), "/api-gateway/v2/consents/t%2F1/approve/u%3F1")
        _Handler._reply = []
        c.consents.my_approvals("u/1")
        self.assertEqual(self._last_path(), "/api-gateway/v2/consents/my-approvals/u%2F1")
        _Handler._reply = {"id": "r#1", "status": "pending"}
        c.deepfake.status("r#1")
        self.assertEqual(self._last_path(), "/api-gateway/v2/deepfake/checks/r%231")

    def test_face_verify_with_session_video_sends_no_media(self) -> None:
        self._client().verification.face_verify(VerifyInput(
            user_id="u-1", session_id="sess_1", use_session_video=True, media=io.BytesIO(b"vid"),
        ))
        body = _Handler._requests[-1]["body"]
        self.assertNotIn(b'name="video"', body)
        self.assertIn(b'"use_session_video": true', body.replace(b'":true', b'": true'))

    def test_face_match_with_session_video_keeps_reference_only(self) -> None:
        self._client().face_match.match(FaceMatchInput(
            user_id="u-1", reference_image=io.BytesIO(b"img"), reference_name="r.jpg",
            session_id="sess_1", use_session_video=True, video=io.BytesIO(b"vid"),
        ))
        body = _Handler._requests[-1]["body"]
        self.assertNotIn(b'name="video"', body)
        self.assertIn(b'name="reference_image"', body)

    def test_face_verify_without_session_video_uploads_media(self) -> None:
        self._client().verification.face_verify(VerifyInput(user_id="u-1", media=io.BytesIO(b"vid")))
        self.assertIn(b'name="video"', _Handler._requests[-1]["body"])


if __name__ == "__main__":
    unittest.main()
