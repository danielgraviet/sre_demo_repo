# Phase 3: Business Logic, API Routes & Seed Data

## Goal
Implement the profile service with all failure modes, wire up FastAPI routes, and seed the database with repeatable test data.

## Prerequisite
Phase 2 complete (settings, db, models, schemas, sentry all importable).

## Tasks

### 3.1 — `app/services/profile_service.py`
Implement `get_profile(user_id: int, db: Session) -> UserProfile` with a deterministic branch on `settings.failure_mode`:

| Mode              | Behavior |
|-------------------|----------|
| `none`            | Fetch from in-memory dict cache first; fall back to DB if missing. Return quickly. |
| `cache_off`       | Skip cache entirely; always query DB. Increment Sentry breadcrumb noting cache bypass. |
| `slow_query`      | Add `time.sleep(2)` OR run a deliberately expensive query (e.g., `SELECT * FROM user_profiles` with no index filter). Set Sentry tag `slow_query=true`. |
| `pool_saturation` | Acquire DB session, sleep briefly to hold the connection, then query. With a small pool this causes timeouts under load. Raise `OperationalError` when the wait exceeds threshold. |
| `combined`        | Apply all three above: no cache + slow query + pool hold. Most signals fired to Sentry. |

Rules:
- **No random behavior.** All branches are deterministic given the same `FAILURE_MODE`.
- Capture all exceptions with `sentry_sdk.capture_exception(e)` before re-raising.
- Set `sentry_sdk.set_tag("failure_mode", settings.failure_mode)` at the top of each call.
- Return `None` (or raise `HTTPException 404`) when the user is not found.

In-memory cache implementation: a module-level `dict` keyed by `user_id`. Cleared on process restart.

### 3.2 — `app/seed.py`
- Create all tables via `Base.metadata.create_all(engine)`.
- Insert 10 deterministic `UserProfile` rows (ids 1–10, fixed usernames/emails).
- Skip insertion if a row with that `id` already exists (idempotent).
- Runnable as `python -m app.seed` or via `make seed`.

### 3.3 — `app/main.py`
Build the FastAPI app:

**Startup:**
- Call `init_sentry()` on app startup (use `@app.on_event("startup")` or lifespan context).
- Call `Base.metadata.create_all(bind=engine)` to ensure tables exist.

**Routes:**

1. `GET /health`
   - Returns `{"status": "ok"}`.
   - No DB hit.

2. `GET /api/users/profile/{user_id}`
   - Calls `get_profile(user_id, db)`.
   - Returns `UserProfileResponse`.
   - On `404`: returns `{"detail": "User not found"}` with status 404.
   - On any other exception: logs to Sentry (already done in service), returns 500.
   - Adds response header `X-Failure-Mode: <current mode>` for easy debugging.

3. `POST /admin/failure-mode/{mode}` *(only active when `settings.env == "demo"`)*
   - Accepts `mode` in `{none, cache_off, slow_query, pool_saturation, combined}`.
   - Updates `settings.failure_mode` in-memory for the running process.
   - Returns `{"failure_mode": "<new mode>"}`.
   - Returns 403 if `ENV != demo`.

## Acceptance Criteria
- `make run` starts Uvicorn with no import errors.
- `GET /health` returns 200 `{"status":"ok"}`.
- `GET /api/users/profile/1` returns a profile in `none` mode.
- Setting `FAILURE_MODE=slow_query` causes >2s latency on the profile endpoint.
- Setting `FAILURE_MODE=combined` causes Sentry to receive error/perf events (verify in Sentry dashboard or mock DSN logs).
- `make seed` is idempotent (run twice, no duplicate key errors).
