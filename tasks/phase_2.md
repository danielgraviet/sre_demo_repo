# Phase 2: Core App Infrastructure

## Goal
Build the foundational modules — settings, database, models, schemas, and Sentry init — before any route logic is written.

## Prerequisite
Phase 1 complete (deps installed, directory structure exists).

## Tasks

### 2.1 — `app/settings.py`
Use `pydantic-settings` (`BaseSettings`) to load all env vars:

| Field               | Type    | Default                    |
|---------------------|---------|----------------------------|
| `sentry_dsn`        | `str`   | `""`                       |
| `env`               | `str`   | `"local"`                  |
| `database_url`      | `str`   | `"sqlite:///./app.db"`     |
| `disable_cache`     | `bool`  | `False`                    |
| `enable_slow_query` | `bool`  | `False`                    |
| `db_pool_limit`     | `int`   | `20`                       |
| `inject_timeout_errors` | `bool` | `False`               |
| `failure_mode`      | `str`   | `"none"`                   |

Expose a module-level `settings = Settings()` singleton.

### 2.2 — `app/db.py`
- Create a SQLAlchemy engine from `settings.database_url`.
- Set `pool_size` from `settings.db_pool_limit` (skip for SQLite which doesn't use connection pools — handle gracefully).
- Create a `SessionLocal` factory using `sessionmaker`.
- Expose a `get_db()` FastAPI dependency that yields a session and closes it.
- Expose `Base = declarative_base()`.

### 2.3 — `app/models.py`
Define a single `UserProfile` table with columns:
- `id` (Integer, primary key)
- `username` (String, not null)
- `email` (String, not null)
- `bio` (Text, nullable)
- `created_at` (DateTime, default=now)

### 2.4 — `app/schemas.py`
Define Pydantic response models:
- `UserProfileResponse` — mirrors `UserProfile` model fields plus `id`.
- `HealthResponse` — `{"status": str}`.
- `ErrorResponse` — `{"detail": str}`.

### 2.5 — `app/sentry.py`
- Function `init_sentry()` that calls `sentry_sdk.init(...)` only when `settings.sentry_dsn` is non-empty.
- Enable `FastAPIIntegration`, `SqlalchemyIntegration`.
- Set `traces_sample_rate=1.0` (or make configurable via settings).
- Add default tags/scope:
  - `service = "mock-sre-service"`
  - `demo_scenario = "incident_b"`
- Add `failure_mode` tag dynamically (updated at request time, not init time).

## Acceptance Criteria
- `from app.settings import settings` works and reads from `.env`.
- `from app.db import get_db, Base` works.
- `from app.models import UserProfile` works.
- `from app.schemas import UserProfileResponse` works.
- `from app.sentry import init_sentry` works without raising when DSN is empty.
