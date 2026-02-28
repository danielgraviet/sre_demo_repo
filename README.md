# Mock SRE Service

A demo incident generator for **Alpha SRE**. Runs a production-like FastAPI service that emits realistic errors and performance degradation to Sentry, enabling Alpha to investigate **Incident B (AI-Assisted Deploy Regression)**.

---

## Incident B Flow (Visual)

![Incident B non-technical flow](assets/incident-b-flow.svg)

---

## Quick Start

```bash
cp .env.example .env
# Optional: add your SENTRY_DSN to .env for live Sentry signals
make setup
make seed
make run
```

Service is available at `http://localhost:8000`.

---

## Triggering Incident B in <5 Minutes

1. Set the failure mode in your environment:
   ```bash
   export FAILURE_MODE=combined
   ```
   Or edit `.env` and set `FAILURE_MODE=combined`.

2. Start the service:
   ```bash
   make run
   ```

3. Fire repeated requests to generate Sentry signals:
   ```bash
   make load
   ```

4. Open your Sentry dashboard and filter by:
   - `failure_mode = combined`
   - `demo_scenario = incident_b`

5. Observe: **error spike** (500s from pool exhaustion) + **high-latency transactions** (~2s) on `GET /api/users/profile/{user_id}`.

---

## Failure Mode Reference

| Mode              | Cache | Query Speed | Pool Behavior | Expected Sentry Signal          |
|-------------------|-------|-------------|---------------|---------------------------------|
| `none`            | on    | fast        | normal        | none                            |
| `cache_off`       | off   | fast        | normal        | increased DB reads (breadcrumb) |
| `slow_query`      | off   | slow (~2s)  | normal        | latency alert                   |
| `pool_saturation` | off   | normal      | exhausted     | timeout / 500 errors            |
| `combined`        | off   | slow (~2s)  | exhausted     | errors + latency spike          |

Toggle the mode without restarting the server (requires `ENV=demo`):

```bash
curl -X POST http://localhost:8000/admin/failure-mode/combined
```

---

## Environment Variables

| Variable               | Default                  | Description                                          |
|------------------------|--------------------------|------------------------------------------------------|
| `SENTRY_DSN`           | *(empty)*                | Sentry DSN — leave empty to disable Sentry           |
| `ENV`                  | `local`                  | Runtime environment (`local` or `demo`)              |
| `DATABASE_URL`         | `sqlite:///./app.db`     | SQLAlchemy database URL                              |
| `DISABLE_CACHE`        | `false`                  | Force cache off (overridden by `FAILURE_MODE`)       |
| `ENABLE_SLOW_QUERY`    | `false`                  | Force slow query path (overridden by `FAILURE_MODE`) |
| `DB_POOL_LIMIT`        | `20`                     | Max DB connection pool size                          |
| `INJECT_TIMEOUT_ERRORS`| `false`                  | Inject timeout errors into responses                 |
| `FAILURE_MODE`         | `none`                   | Active failure mode (see table above)                |

---

## API Endpoints

| Method | Path                              | Description                                     |
|--------|-----------------------------------|-------------------------------------------------|
| GET    | `/health`                         | Health check — always returns `{"status":"ok"}` |
| GET    | `/api/users/profile/{user_id}`    | Fetch user profile (failure modes apply here)   |
| POST   | `/admin/failure-mode/{mode}`      | Set failure mode at runtime (`ENV=demo` only)   |

The profile endpoint adds an `X-Failure-Mode` response header for easy inspection.

---

## Make Targets

| Target        | Command                  | Description                              |
|---------------|--------------------------|------------------------------------------|
| `make setup`  | `uv sync --extra dev`    | Install all dependencies                 |
| `make seed`   | `python -m app.seed`     | Create tables and seed 10 user profiles  |
| `make run`    | `uvicorn app.main:app`   | Start the API server with hot-reload     |
| `make test`   | `pytest tests/ -v`       | Run the full test suite                  |
| `make verify` | `make test`              | Alias for `make test`                    |
| `make load`   | curl loop (50 requests)  | Fire 50 requests to trigger Sentry spike |

---

## Running Tests

```bash
make test
```

Tests use an isolated in-memory SQLite database — no `.env` or live Sentry DSN required.

---

## Alpha Integration

The `fixtures/` directory contains static JSON files that Alpha can consume alongside live Sentry data to reconstruct the full Incident B narrative.

### `fixtures/recent_commits.json`

A fake git log of the deploy that introduced the regression. Fields:

| Field           | Maps to Sentry tag / context          |
|-----------------|---------------------------------------|
| `sha`           | Sentry release / commit reference     |
| `timestamp`     | Incident timeline anchor              |
| `message`       | Root cause description                |
| `files_changed` | Correlate with `failure_mode` toggles |

Key commits in the story:
- `b71e4d8` — removes the cache layer (`profile_service.py`)
- `c95a017` — introduces an unindexed full table scan (`models.py`, `db.py`)
- `d40f3b2` — reduces `DB_POOL_LIMIT` to 2 (`settings.py`)
- `e18c5a9` — partial hotfix that did not resolve the incident

### `fixtures/config_snapshot.json`

The runtime configuration captured at the time of the incident. Key fields:

| Field          | Sentry tag             |
|----------------|------------------------|
| `failure_mode` | `failure_mode`         |
| `env`          | `environment`          |
| `captured_at`  | Incident timestamp     |

### Loading the fixtures

```python
import json

commits = json.load(open("fixtures/recent_commits.json"))
config  = json.load(open("fixtures/config_snapshot.json"))
```

Both files are plain JSON — no auth or runtime dependency required.

---

## Project Structure

```
app/
├── main.py                 # FastAPI app + routes
├── settings.py             # Env-driven config (pydantic-settings)
├── sentry.py               # Sentry SDK init
├── db.py                   # Engine, session, Base
├── models.py               # UserProfile SQLAlchemy model
├── schemas.py              # Pydantic response schemas
├── seed.py                 # Seed database with 10 users
└── services/
    └── profile_service.py  # Business logic + failure mode branches
tests/
├── conftest.py
├── test_health.py
├── test_profile_success.py
├── test_profile_failure_modes.py
└── test_sentry_init.py
fixtures/
├── recent_commits.json     # Fake deploy history for Incident B
└── config_snapshot.json    # Runtime config at incident time
```
