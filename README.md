# biometry

[![PyPI version](https://img.shields.io/pypi/v/biometry)](https://pypi.org/project/biometry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/biometry)](https://pypi.org/project/biometry/)

Python SDK for the [Biometry](https://biometrysolutions.com) platform APIs. Zero external dependencies -- uses only the Python standard library.

## Installation

```bash
pip install biometry
```

## Quick Start

```python
import biometry

client = biometry.BiometryClient(
    "your-api-key",
    user_fullname="John Doe",
)

session_id = client.sessions.start()
print("Session started:", session_id)
```

## Full Verification Flow

A typical identity verification combines session management, consent, document authentication, face enrollment, video processing, and face matching:

```python
import biometry

client = biometry.BiometryClient(
    "your-api-key",
    user_fullname="John Doe",
)

# 1. Start a biometric session
session_id = client.sessions.start()

# 2. Approve consent for the user
client.consents.approve(
    consent_id="your-consent-id",
    user_id="user-123",
    session_id=session_id,
)

# 3. Authenticate an identity document
with open("passport.jpg", "rb") as doc:
    doc_resp = client.doc_auth.check(
        doc, "passport.jpg",
        session_id=session_id,
    )
    doc_info = doc_resp.decode(biometry.DocAuthInfo)
    print(f"Document: {doc_info.document_type}, Country: {doc_info.country_code}")

# 4. Enroll the face from the document photo
with open("portrait.jpg", "rb") as face:
    client.enrollment.face(
        biometry.EnrollFaceInput(face=face, file_name="portrait.jpg"),
        session_id=session_id,
    )

# 5. Process a biometric video
with open("video.mp4", "rb") as video:
    video_resp = client.video.process(
        biometry.ProcessVideoInput(
            video=video,
            video_name="video.mp4",
            phrase="one two three four five",
        ),
        session_id=session_id,
    )
    print(f"Video score: {video_resp.score}")

# 6. Match the enrolled face against the session video
with open("portrait.jpg", "rb") as face:
    match_resp = client.face_match.match_with_session_video(
        image=face,
        image_name="portrait.jpg",
        session_id=session_id,
    )
    print(f"Match score: {match_resp.score}")

# 7. End the session
client.sessions.end(session_id)
```

## Services

| Service | Attribute | Methods |
|---------|-----------|---------|
| Sessions | `client.sessions` | `start()`, `end()` |
| Video | `client.video` | `process()` |
| Enrollment | `client.enrollment` | `face()`, `voice()` |
| Face Match | `client.face_match` | `match()`, `match_with_session_video()` |
| Doc Auth | `client.doc_auth` | `check()` |
| Consents | `client.consents` | `approve()`, `my_approvals()` |
| Images | `client.images` | `upload()`, `get()` |
| AVF | `client.avf` | `start_inference()`, `check_status()` |
| Transactions | `client.transactions` | `list()`, `count()`, `get_by_session()`, `get_samples()`, `update_tags()`, `flag()` |
| API Keys | `client.api_keys` | `mint()`, `revoke()`, `info()` |

## Per-Request Options

Every service method accepts keyword arguments that are sent as HTTP headers:

```python
resp = client.video.process(
    input,
    session_id="sess-abc",
    fullname="Jane Doe",
    device_info='{"model": "iPhone 15", "os": "iOS 18"}',
    geo_location='{"lat": -35.28, "lng": 149.13, "country": "AU"}',
    request_tags="onboarding,mobile",
    client_app="my-app",
    client_version="2.1.0",
    inhouse_docauth=True,
    inhouse_mrz=True,
)
```

| Keyword | Header | Description |
|---------|--------|-------------|
| `session_id` | `X-Session-ID` | Attach the request to a session |
| `fullname` | `X-User-Fullname` | Override the user fullname for this request |
| `action_trigger` | `X-Action-Trigger` | Custom action trigger label |
| `device_info` | `X-Device-Info` | JSON-encoded device metadata |
| `geo_location` | `X-Geo-Location` | JSON-encoded lat/lng/country/city |
| `request_tags` | `X-Request-Tags` | Comma-separated labels |
| `client_app` | `X-Client-App` | Calling application identifier |
| `client_version` | `X-Client-Version` | Calling application version |
| `inhouse_docauth` | `X-Inhouse-Docauth` | Use in-house document authentication (`True`/`False`) |
| `inhouse_mrz` | `X-Inhouse-MRZ` | Enable MRZ validation (`True`/`False`) |

## Response Headers

The `BiometryResponse` object exposes useful response headers as properties:

```python
resp = client.video.process(input, session_id=session_id)

resp.request_id        # X-Request-Id -- unique identifier for the request
resp.auto_enrolled     # X-Auto-Enroll -- True if auto face/voice enrollment was performed
resp.removed_services  # X-Removed-Services -- True if services were dropped due to missing consent
```

## Error Handling

All API errors are raised as `BiometryAPIError` with the HTTP status code and error message:

```python
from biometry import BiometryAPIError, is_not_found, is_forbidden, is_unauthorized

try:
    session_id = client.sessions.start()
except BiometryAPIError as e:
    print(f"HTTP {e.status_code}: {e.message}")

    if is_not_found(e):
        print("Resource not found")
    elif is_forbidden(e):
        print("Access denied")
    elif is_unauthorized(e):
        print("Invalid API key")
```

## Documentation

Full API reference and guides: [docs.biometrysolutions.com/sdks/python/](https://docs.biometrysolutions.com/sdks/python/)

## License

[MIT](LICENSE) -- Copyright 2026 Namadgi Pty Ltd
