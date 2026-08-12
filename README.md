# Biometry Python SDK

Zero-dependency Python client for the [Biometry](https://biometrysolutions.com) platform APIs, targeting the **API v2** gateway (`/api-gateway/v2`). Uses only the standard library.

## Installation

```bash
pip install biometry
```

Requires Python 3.9+.

## Quick start

```python
from biometry import BiometryClient, LivenessInput, EnrollFaceInput

client = BiometryClient("YOUR_API_KEY")

# Sessions
session_id = client.sessions.start()

# Enrollment (identify the user with an opaque user_id)
with open("face.jpg", "rb") as f:
    client.enrollment.face(EnrollFaceInput(user_id="user-123", face=f, file_name="face.jpg"))

# Liveness check
with open("video.mp4", "rb") as v:
    resp = client.verification.liveness(LivenessInput(
        user_id="user-123", video=v, file_name="video.mp4", phrase="12345678",
        session_id=session_id,
    ))
    if resp.decision:
        print(resp.decision.status)  # "pass" | "fail" | "refer"

client.sessions.end(session_id)
```

## API v2 notes

- **Identity** is an opaque `user_id` you supply on each call's input object (carried in the JSON `request` part), not a header.
- **Verification** is split into `client.verification.liveness` / `face_verify` / `voice_verify` (the v1 `process-video` split).
- **Responses** are the v2 success envelope, exposed as `resp.data`, `resp.decision` (`status`/`score`/`reasons`), and `resp.meta`.
- **Errors** raise `BiometryAPIError` with `status_code`, `code`, and `message`.
- `client.transactions` and `client.api_keys` target separate services and are unchanged.

See `CHANGELOG.md` for the full v1 → v2 migration notes.

## License

MIT
