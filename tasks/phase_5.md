# Phase 5: Fixtures & Alpha Integration Contract

## Goal
Produce the static JSON fixtures that the Alpha SRE repo can consume alongside live Sentry data to reconstruct the full Incident B narrative.

## Prerequisite
Phase 3 complete (failure modes and routes defined, so commit/config context is known).

## Tasks

### 5.1 — `fixtures/recent_commits.json`
Create a static JSON array representing a fake git log around the time of "the bad deploy".
Each entry should include:
```json
{
  "sha": "<7-char hash>",
  "author": "<name>",
  "timestamp": "<ISO 8601>",
  "message": "<commit message>",
  "files_changed": ["<path>", ...]
}
```
Required commits to tell the Incident B story (minimum 5 entries):
1. A commit that **removes the cache layer** (`profile_service.py` changed).
2. A commit that **introduces an unindexed query** (db or models touched).
3. A commit that **reduces DB pool size** (settings or db.py touched).
4. An innocent unrelated commit (padding).
5. The "hotfix attempt" commit (partial revert that didn't help).

### 5.2 — `fixtures/config_snapshot.json`
Create a static JSON object capturing the "current" runtime config at the time of the incident:
```json
{
  "captured_at": "<ISO 8601>",
  "env": "demo",
  "failure_mode": "combined",
  "disable_cache": true,
  "enable_slow_query": true,
  "db_pool_limit": 2,
  "inject_timeout_errors": true,
  "database_url": "sqlite:///./app.db",
  "sentry_dsn": "<redacted>"
}
```

### 5.3 — Wire fixtures into README
Add a section in `README.md` (created in Phase 6) describing:
- Where the fixture files live.
- How Alpha should load them (static file read or HTTP endpoint).
- Which fixture fields map to which Sentry tags for correlation.

## Acceptance Criteria
- `fixtures/recent_commits.json` is valid JSON with ≥5 entries.
- `fixtures/config_snapshot.json` is valid JSON and reflects `FAILURE_MODE=combined` state.
- Both files can be parsed with `python -c "import json; json.load(open('fixtures/recent_commits.json'))"`.
