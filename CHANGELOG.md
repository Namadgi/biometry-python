# Changelog

## 0.2.0 (BM-338)

Migrated the SDK to the **Biometry API v2** gateway (`/api-gateway/v2`). This is a breaking release.

### Breaking changes

- **Identity model:** biometric calls now take an opaque `user_id` on their input objects, serialized into the API v2 JSON `request` part. The `user_fullname` constructor argument is removed (identity is per-call), and the gateway strips identity headers on v2.
- **`client.video` removed**, replaced by **`client.verification`** with `liveness`, `face_verify`, and `voice_verify` (the v1 `process-video` split), each taking a typed input.
- **`client.avf` → `client.deepfake`** (`submit` / `status`), targeting `/v2/deepfake/checks`; response type `AVFInferenceResponse`/`AVFStatusResponse` → `DeepfakeCheck`.
- **`enrollment.face` / `enrollment.voice`** take `EnrollFaceInput` / `EnrollVoiceInput` with `user_id`; voice enrollment is now a single file + phrase (was a list).
- **`face_match.match`** takes `FaceMatchInput` (`reference_image` + optional `video`, `use_session_video`); `match_with_session_video` folded into `use_session_video`.
- **`doc_auth.check`** takes `DocAuthInput`; the `inhouse_docauth` / `inhouse_mrz` call options are replaced by `provider` / `mrz_provider` (`"inhouse" | "idscan"`).
- **`images`** now manages the user reference image: `upload(user_id, image, file_name)` → `PUT /v2/users/{id}/reference-image`; `get(user_id)` returns raw image `bytes`.
- **`sessions.start`** targets `POST /v2/sessions` and reads `data.session_id`; `sessions.end` targets `POST /v2/sessions/{id}/end`.
- **`consents`** approvals target `/v2/consents/*`.
- **Response envelope** is now `{ data, decision, meta }`: `BiometryResponse.score` / `scoring_result` / `decision_reasons` / `auto_enrolled` / `removed_services` replaced by `.decision` (`status`/`score`/`reasons`) and `.meta`.
- **Errors:** `BiometryAPIError` now carries `code` from the v2 error envelope; the parser handles v2 (`{error:{code,message}}`), field-error arrays, and the legacy shape.

### Unchanged

- `transactions` (`/api-transactions`) and `api_keys` (`/api-projects`) are separate services, untouched by the gateway v2 migration.
- Request-metadata call options (`device_info`, `geo_location`, `request_tags`, `client_app`, `client_version`) still apply as headers.
