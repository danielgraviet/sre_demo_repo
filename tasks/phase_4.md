# Phase 4: Tests

## Goal
Write the minimum test suite required by the overview so `make test` passes cleanly and failure mode behavior is provably deterministic.

## Prerequisite
Phase 3 complete (all routes and service logic implemented).

## Tasks

### 4.1 — `tests/conftest.py`
- Create an in-memory SQLite test database (separate from `app.db`).
- Override the `get_db` FastAPI dependency to use the test DB.
- Expose a `client` fixture using `httpx` / `TestClient`.
- Seed the test DB with at least one `UserProfile` row (user_id=1).

### 4.2 — `tests/test_health.py`
Tests:
- `test_health_returns_ok` → `GET /health` returns 200, body is `{"status":"ok"}`.

### 4.3 — `tests/test_profile_success.py`
Tests (all run with `FAILURE_MODE=none`):
- `test_profile_returns_200_for_valid_user` → status 200, response matches schema.
- `test_profile_returns_404_for_missing_user` → user_id=9999 returns 404.
- `test_response_header_contains_failure_mode` → `X-Failure-Mode` header is present.

### 4.4 — `tests/test_profile_failure_modes.py`
Tests:
- `test_cache_off_mode_still_returns_profile` → `FAILURE_MODE=cache_off`, user_id=1, expect 200.
- `test_slow_query_mode_adds_latency` → `FAILURE_MODE=slow_query`, measure elapsed time > 1.5s.
- `test_pool_saturation_mode_returns_error_under_load` → `FAILURE_MODE=pool_saturation`, send 5 concurrent requests, expect at least one non-200 response (timeout/500).
- `test_combined_mode_returns_server_error_or_high_latency` → `FAILURE_MODE=combined`, at least one of: status 5xx OR elapsed > 1.5s.

### 4.5 — `tests/test_sentry_init.py`
Tests:
- `test_sentry_init_with_empty_dsn_does_not_raise` → `init_sentry()` with `SENTRY_DSN=""` completes without exception.
- `test_sentry_init_with_mock_dsn` → `init_sentry()` with a fake DSN string doesn't raise at import time.

## Notes
- Use `monkeypatch` or direct `settings` mutation to toggle `failure_mode` between tests.
- Do NOT use `@pytest.mark.asyncio` unless the app is actually async; sync TestClient is preferred.
- Tests must be deterministic — no flaky sleeps. Use `time.monotonic()` for latency assertions.

## Acceptance Criteria
- `make test` exits with code 0.
- All 10+ tests pass without requiring a live Sentry DSN.
- No test takes longer than 10 seconds individually.
