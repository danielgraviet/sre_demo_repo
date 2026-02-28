# Phase 6: Demo Readiness & Definition of Done

## Goal
Finalize the README, verify all make targets work end-to-end, and confirm the repo meets every item in the Definition of Done from `overview.md` section 13.

## Prerequisite
Phases 1–5 complete.

## Tasks

### 6.1 — Write `README.md`
Must include these sections:

**Quick Start**
```bash
cp .env.example .env
# Add SENTRY_DSN to .env
make setup
make seed
make run
```

**Triggering Incident B in <5 Minutes**
Step-by-step:
1. Set `FAILURE_MODE=combined` in `.env` (or `export FAILURE_MODE=combined`).
2. `make run`
3. `make load` (fires repeated requests to trigger Sentry signals)
4. Open Sentry dashboard — filter by `failure_mode=combined` and `demo_scenario=incident_b`.
5. Observe: error spike + high-latency transactions on `/api/users/profile/{user_id}`.

**Failure Mode Reference Table**

| Mode              | Cache | Query Speed | Pool Behavior | Expected Sentry Signal |
|-------------------|-------|-------------|---------------|------------------------|
| `none`            | on    | fast        | normal        | none                   |
| `cache_off`       | off   | fast        | normal        | increased DB reads     |
| `slow_query`      | off   | slow (~2s)  | normal        | latency alert          |
| `pool_saturation` | off   | normal      | exhausted     | timeout errors         |
| `combined`        | off   | slow (~2s)  | exhausted     | errors + latency spike |

**Environment Variables** — full table from section 6 of overview.md.

**Alpha Integration** — point to `fixtures/` and describe the contract.

**Running Tests**
```bash
make test
```

### 6.2 — End-to-end smoke test (manual checklist)
Work through each item before calling the repo done:

- [ ] `make setup` installs all deps cleanly on a fresh venv.
- [ ] `make seed` creates `app.db` and inserts 10 rows.
- [ ] `make run` starts Uvicorn with no errors.
- [ ] `curl http://localhost:8000/health` returns `{"status":"ok"}`.
- [ ] `curl http://localhost:8000/api/users/profile/1` returns a profile in `none` mode.
- [ ] `FAILURE_MODE=slow_query make run` → profile endpoint takes >2s.
- [ ] `FAILURE_MODE=combined make run` + `make load` → Sentry receives events.
- [ ] `make test` exits 0.
- [ ] `fixtures/recent_commits.json` and `fixtures/config_snapshot.json` are valid JSON.

### 6.3 — Final Definition of Done checklist (from overview.md §13)

- [ ] Service runs locally with one command (`make run`).
- [ ] Failure mode can be toggled deterministically via env var.
- [ ] Sentry receives clear incident signals (error spike + latency) from the failing endpoint.
- [ ] README documents how to trigger Incident B in <5 minutes.
- [ ] `make test` passes.

## Acceptance Criteria
All checkboxes in 6.2 and 6.3 are checked.
The repo is hand-off ready for the Alpha SRE demo.
