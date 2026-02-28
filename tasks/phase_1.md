# Phase 1: Project Scaffolding & Dependencies

## Goal
Bootstrap the repo structure, install all dependencies, and add the Makefile so every subsequent phase has a working foundation.

## Tasks

### 1.1 — Update `pyproject.toml`
Add all required dependencies:
- `fastapi`
- `uvicorn[standard]`
- `sqlalchemy`
- `sentry-sdk[fastapi]`
- `pydantic-settings`
- `python-dotenv`

Dev/test deps:
- `pytest`
- `httpx` (for FastAPI TestClient)
- `pytest-asyncio` (if async tests are needed)

### 1.2 — Create directory structure
```
app/
app/services/
tests/
fixtures/
```

Create empty `__init__.py` files in `app/` and `app/services/` and `tests/`.

### 1.3 — Create `.env.example`
Document every env var with safe defaults:
```
SENTRY_DSN=
ENV=local
DATABASE_URL=sqlite:///./app.db
DISABLE_CACHE=false
ENABLE_SLOW_QUERY=false
DB_POOL_LIMIT=20
INJECT_TIMEOUT_ERRORS=false
FAILURE_MODE=none
```

### 1.4 — Create `Makefile`
Implement all required targets:
- `make setup`  → `pip install -e .[dev]` (or uv equivalent)
- `make run`    → `uvicorn app.main:app --reload`
- `make seed`   → `python -m app.seed`
- `make test`   → `pytest tests/`
- `make verify` → `make test` (lint/type optional at this stage)
- `make load`   → curl loop or Python script hitting `/api/users/profile/1` repeatedly

## Acceptance Criteria
- `make setup` installs without errors.
- Directory tree matches the structure in `overview.md` section 5.
- `.env.example` covers every var from section 6.
- `make run` fails gracefully (app modules don't exist yet) rather than silently.
