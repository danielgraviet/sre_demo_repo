# Mock Service Repo — Technical Overview (For AI Coding Agents)

  ## 1) Purpose

  This repo is a **demo incident generator** for Alpha SRE.

  It should:
  1. Run a simple production-like API service.
  2. Emit realistic errors/performance issues to Sentry.
  3. Expose deterministic “failure modes” that map to Alpha’s investigation narrative.

  This repo is **not** the Alpha runtime. It is the external system that fails so Alpha can investigate it.

  ---

  ## 2) Primary Demo Story

  Simulate **Incident B (AI-Assisted Deploy Regression)**:
  1. A cache path is removed/disabled.
  2. A slow/unindexed query path is introduced.
  3. DB connections saturate under load.
  4. Sentry shows error spikes + high latency.
  5. Alpha consumes the incident context and ranks root causes.

  ---

  ## 3) Tech Stack

  - Python 3.13+
  - FastAPI + Uvicorn
  - SQLAlchemy (sync is fine for demo)
  - SQLite (default) or Postgres (optional)
  - `sentry-sdk` with FastAPI integration
  - Optional: in-memory cache (or Redis if needed)

  Keep implementation simple and deterministic.

  ---

  ## 4) Scope / Non-Goals

  ### In Scope
  - Minimal API service with one critical endpoint.
  - Sentry integration for errors + tracing/perf.
  - Feature flags/env toggles to force known failure modes.
  - Seed data and repeatable local run instructions.

  ### Out of Scope
  - Production security hardening.
  - Complex auth systems.
  - Full observability platform integrations (Datadog, Prometheus, etc.).
  - Auto-remediation logic.

  ---

  ## 5) Proposed Repo Structure

  ```text
  mock-sre-service/
  ├── app/
  │   ├── main.py                # FastAPI app + routes
  │   ├── settings.py            # env-driven config
  │   ├── sentry.py              # sentry init
  │   ├── db.py                  # engine/session setup
  │   ├── models.py              # SQLAlchemy models
  │   ├── schemas.py             # Pydantic response models
  │   ├── services/
  │   │   └── profile_service.py # business logic with toggles
  │   └── seed.py                # seed database
  ├── tests/
  │   ├── test_health.py
  │   ├── test_profile_success.py
  │   └── test_profile_failure_modes.py
  ├── .env.example
  ├── pyproject.toml
  ├── Makefile
  └── README.md
```
  ———

  ## 6) Runtime Configuration (Env Vars)

  Required:

  - SENTRY_DSN=...
  - ENV=local|demo
  - DATABASE_URL=sqlite:///./app.db (default acceptable)

  Failure toggles:

  - DISABLE_CACHE=false
  - ENABLE_SLOW_QUERY=false
  - DB_POOL_LIMIT=20
  - INJECT_TIMEOUT_ERRORS=false
  - FAILURE_MODE=none|cache_off|slow_query|pool_saturation|combined

  Use FAILURE_MODE=combined for demo day.

  ———

  ## 7) API Endpoints

  1. GET /health

  - Returns {"status":"ok"}

  2. GET /api/users/profile/{user_id}

  - Normal mode: returns quickly with profile payload.
  - Failure modes:
      - cache disabled -> increased DB reads
      - slow query path -> added latency
      - pool saturation -> timeout/error behavior under load
  - Must capture exceptions in Sentry and include trace/performance telemetry.

  3. Optional: POST /admin/failure-mode/{mode}

  - Sets in-memory mode for live demos (if enabled only in ENV=demo).

  ———

  ## 8) Sentry Integration Requirements

  - Initialize sentry_sdk at startup.
  - Enable FastAPI integration.
  - Enable tracing/performance (traces_sample_rate configurable).
  - Tag all events with:
      - service=mock-sre-service
      - failure_mode=<mode>
      - demo_scenario=incident_b
  - Capture:
      - Exceptions (timeouts, DB errors)
      - Performance degradation on /api/users/profile/{user_id}

  ———

  ## 9) Deterministic Failure Behavior

  Implement a deterministic branch in profile_service.py:

  - none: return fast healthy response.
  - cache_off: skip cache and query DB every request.
  - slow_query: artificial delay or expensive query path.
  - pool_saturation: simulate DB resource exhaustion under small pool.
  - combined: all above behaviors to create clear Sentry signal spike.

  No random behavior unless explicitly configured. Demo must be repeatable.

  ———

  ## 10) Make Commands (Required)

  - make setup -> install deps
  - make run -> start API
  - make test -> run deterministic tests
  - make verify -> lint/type/test (or test-only if lint/type not set yet)
  - make seed -> seed local DB
  - make load -> optional local load script to trigger incident quickly

  ———

  ## 11) Integration Contract with Alpha Repo

  This mock repo must expose/produce data that Alpha can consume:

  1. Sentry incident with elevated error rate and latency.
  2. Known failure mode metadata (tag/label) for validation.
  3. Optional static “recent commits” + “config snapshot” JSON fixtures, e.g.:
      - fixtures/recent_commits.json
      - fixtures/config_snapshot.json

  Alpha-side ingestion can combine:

  - live Sentry data (logs/perf)
  - mocked commit/config context from fixtures

  ———

  ## 12) Testing Requirements

  Minimum tests:

  1. health endpoint works.
  2. profile endpoint works in none mode.
  3. profile latency/error behavior changes in failure modes.
  4. Failure mode combined emits server errors or high latency predictably.
  5. Basic Sentry init test (mock DSN acceptable).

  ———

  ## 13) Definition of Done (Demo-Ready)

  Repo is done when:

  1. Service runs locally with one command.
  2. Failure mode can be toggled deterministically.
  3. Sentry receives clear incident signals from the failing endpoint.
  4. README documents exactly how to trigger Incident B in <5 minutes.
  5. Tests pass via make test.

  ———

  ## 14) Coding Constraints for AI Agents

  - Keep modules small and explicit; avoid hidden magic.
  - Prefer straightforward sync code unless async is needed.
  - Add type hints and clear docstrings.
  - Do not over-abstract; this is a demo incident generator.
  - Keep all behavior reproducible and easy to explain live.
