# biometry

[![PyPI version](https://img.shields.io/pypi/v/biometry)](https://pypi.org/project/biometry/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/biometry)](https://pypi.org/project/biometry/)

Python SDK for the [Biometry](https://biometrysolutions.com) identity verification platform. It calls the Biometry API v2 (`/api-gateway/v2`). Zero external dependencies: it uses only the Python standard library.

## Installation

```bash
pip install biometry
```

Requires Python 3.10+.

## Quick Start

```python
from biometry import BiometryClient

client = BiometryClient("YOUR_API_KEY")

session_id = client.sessions.start()
print("Session started:", session_id)
```

Every biometric call takes a `user_id`: your own opaque, stable key for the end user (not their name or email).

## Full Verification Flow

Enroll the user's face, then verify them in a session: liveness on a video, face verification on the same video, and a face match against their document.

```python
from biometry import (
    BiometryClient,
    DocAuthInput,
    EnrollFaceInput,
    FaceMatchInput,
    LivenessInput,
    VerifyInput,
)

client = BiometryClient("YOUR_API_KEY")
user_id = "user-123"

# 1. Enroll the face. Enrollment needs the user's authorization and
#    storage consent (see Consent below).
with open("face.jpg", "rb") as face:
    client.enrollment.face(EnrollFaceInput(user_id=user_id, face=face, file_name="face.jpg"))

# 2. Start a session
session_id = client.sessions.start()

# 3. Check the identity document
with open("passport.jpg", "rb") as doc:
    client.doc_auth.check(DocAuthInput(document=doc, file_name="passport.jpg", session_id=session_id))

# 4. Liveness on a video of the user reading the challenge phrase
with open("selfie.mp4", "rb") as video:
    client.verification.liveness(LivenessInput(
        user_id=user_id,
        video=video,
        file_name="selfie.mp4",
        phrase="one two three four five six seven",
        session_id=session_id,
    ))

# 5. Face verification on the same video
client.verification.face_verify(VerifyInput(
    user_id=user_id,
    session_id=session_id,
    use_session_video=True,
))

# 6. Face match: document photo against the session video
with open("passport.jpg", "rb") as passport:
    match = client.face_match.match(FaceMatchInput(
        user_id=user_id,
        reference_image=passport,
        reference_name="passport.jpg",
        session_id=session_id,
        use_session_video=True,
    ))
if match.decision:
    print("Face match decision:", match.decision.status)

# 7. End the session
client.sessions.end(session_id)
```

In a session, face verification and face match must use the liveness media: the same file, or `use_session_video`.

## Consent

Face and voice enrollment and `images.upload()` need the user's **authorization** and **storage** consent, recorded with `PUT /api-gateway/v2/users/{user_id}/consents`.

`consents.approve()` and `consents.my_approvals()` manage your project's custom consent templates. They do **not** unlock enrollment.

## Services

| Service | Accessor | Methods | API v2 |
|---------|----------|---------|--------|
| Sessions | `client.sessions` | `start()`, `end()` | `/v2/sessions` |
| Verification | `client.verification` | `liveness()`, `face_verify()`, `voice_verify()` | `/v2/liveness`, `/v2/face-verify`, `/v2/voice-verify` |
| Enrollment | `client.enrollment` | `face()`, `voice()` | `/v2/enrollments/face`, `/v2/enrollments/voice` |
| Face Match | `client.face_match` | `match()` | `/v2/face-match` |
| Document Auth | `client.doc_auth` | `check()` | `/v2/documents/check` |
| Deepfake | `client.deepfake` | `submit()`, `status()` | `/v2/deepfake/checks` |
| Images | `client.images` | `upload()`, `get()` | `/v2/users/{user_id}/reference-image` |
| Consents | `client.consents` | `approve()`, `my_approvals()` | `/v2/consents` (custom templates) |
| Transactions | `client.transactions` | `list()`, `count()`, `get_by_session()`, `get_samples()`, `update_tags()`, `flag()` | `/api-transactions` (not part of v2) |
| API Keys | `client.api_keys` | `mint()`, `revoke()`, `info()` | `/api-projects` (not part of v2) |

`LivenessInput.exclude_services` skips checks by name; use the `VerificationServices` constants (`FACE_LIVENESS`, `ACTIVE_SPEAKER`, `VISUAL_SPEECH`, ...).

## Per-Request Options

Every service method accepts keyword arguments that map to request metadata headers:

```python
resp = client.verification.liveness(
    input,
    device_info='{"model": "Pixel 8"}',
    geo_location='{"lat": -35.28, "lng": 149.13}',
    request_tags="onboarding,mobile",
    client_app="my-app",
    client_version="2.1.0",
)
```

| Keyword | Header | Description |
|---------|--------|-------------|
| `device_info` | `X-Device-Info` | JSON device metadata |
| `geo_location` | `X-Geo-Location` | JSON geographic location |
| `request_tags` | `X-Request-Tags` | Comma-separated request labels |
| `client_app` | `X-Client-App` | Calling application identifier |
| `client_version` | `X-Client-Version` | Calling application version |

User, session and trigger are fields on the input objects, not headers.

## Responses

Calls that return `BiometryResponse` carry the API v2 envelope `{ data, decision, meta }`:

```python
resp = client.verification.liveness(input)

resp.decision     # Decision(status, score, reasons); None when no scoring system applies
resp.data         # endpoint-specific payload
resp.request_id   # request trace ID
```

## Error Handling

API errors raise `BiometryAPIError`, with the HTTP status, the v2 error code and the message:

```python
from biometry import BiometryAPIError, is_forbidden, is_not_found, is_unauthorized

try:
    client.verification.liveness(input)
except BiometryAPIError as e:
    print(e.status_code, e.code, e.message)
    if is_unauthorized(e):
        ...  # 401 -- bad or expired API key
    if is_forbidden(e):
        ...  # 403 -- insufficient permissions
    if is_not_found(e):
        ...  # 404 -- resource not found
```

See [CHANGELOG.md](CHANGELOG.md) for the v1 → v2 migration notes.

## Documentation

Full API reference and integration guides: **[docs.biometrysolutions.com/sdks/python](https://docs.biometrysolutions.com/sdks/python/)**.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
