# Incident B Explainer: AI-Assisted Deploy Regression

## What issue this repo is simulating

This repo simulates a deploy regression where a user-facing endpoint starts failing because multiple performance mistakes stack on each other.

The endpoint affected is:

- `GET /api/users/profile/{user_id}`

The failure chain is:

1. The cache path is disabled or bypassed.
2. More requests hit the database directly.
3. A slow/unindexed query path is introduced.
4. Database connections are held for longer.
5. The DB connection pool fills up (pool saturation).
6. New requests wait, slow down, then error or timeout.
7. Sentry shows error spikes and latency degradation.

This is meant to represent a realistic incident where the root cause is upstream (design/config/code regression), while symptoms appear downstream (timeouts and server errors).

## Why this matters for SRE learning

This scenario teaches how to reason from symptoms back to causes:

- Symptom: high latency and timeouts.
- Resource bottleneck: exhausted DB connections.
- Triggering changes: cache removed + slow query path.

In practice, incident response should avoid stopping at "database is slow" and instead identify why load and query cost changed after deploy.

## Terminology glossary

## Cache path

A **cache path** is the fast code path where the service first checks a cache (memory/Redis/etc.) for precomputed or recently fetched data.

- Cache hit: data is returned quickly without querying the database.
- Cache miss: service falls back to DB query path.

When the cache path is disabled, every request takes the slower fallback path and DB load increases sharply.

## Unindexed query

An **unindexed query** is a database query that filters/sorts on columns without an appropriate index.

Effects:

- DB must scan many rows (often large table scans).
- Query latency grows as data volume grows.
- CPU and I/O usage increase.
- Connections stay busy longer.

In this simulation, a slow/unindexed query path makes each request costlier, amplifying DB pressure.

## Slow query path

A **slow query path** is any application branch that consistently runs expensive queries or adds artificial delay.

It can come from:

- Poor SQL patterns.
- Missing indexes.
- Additional joins/filters after a deploy.
- Explicit sleep/delay used for deterministic demo behavior.

## DB connection pool

A **DB connection pool** is a managed set of reusable database connections held by the app.

Why pools exist:

- Opening a new DB connection per request is expensive.
- Pooling improves throughput and stability.

Pool settings typically include maximum pool size and timeout behavior when no connections are available.

## Pool saturation

**Pool saturation** happens when all DB connections in the pool are in use and incoming requests cannot get one immediately.

Typical outcomes:

- Requests queue and latency increases.
- Some requests hit pool timeout and fail.
- Error rates rise (often 5xx or DB timeout exceptions).

This is the key mechanical failure in Incident B: slower queries cause longer connection hold times, which exhausts a limited pool under load.

## Timeout error

A **timeout error** means an operation exceeded the allowed waiting time.

In this context, timeouts often happen while:

- waiting for a free DB connection, or
- waiting for a slow query to complete.

Timeouts are both user-impacting symptoms and useful telemetry signals.

## Latency spike

A **latency spike** is a sharp increase in response time, often visible in p95/p99 metrics.

Why p95/p99 matter:

- Averages can hide tail slowness.
- Users feel tail latency first during incidents.

## Error spike

An **error spike** is a sudden increase in failed requests over baseline.

In this incident, error spikes usually follow latency increases once the system reaches saturation and starts timing out.

## Sentry tracing and signals

In this demo, Sentry is used to observe:

- Exceptions (timeouts, DB errors)
- Transaction latency for `/api/users/profile/{user_id}`
- Tags like `failure_mode` and `demo_scenario=incident_b`

These make it easier to connect observed symptoms to known failure mode context.

## Mental model for Incident B

Think of the system as a queueing problem:

1. Arrival rate (requests/sec) increases under load.
2. Service time per request increases (slow/unindexed query).
3. Effective capacity drops (finite DB pool).
4. Queue grows, wait times grow, then timeouts/errors appear.

Small regressions can therefore produce nonlinear incident behavior when the system is near capacity.

## What to look for during investigation

1. Did cache hit rate drop after deploy?
2. Did query latency increase for the profile endpoint?
3. Did DB pool utilization hit max?
4. Did timeout/5xx rates rise right after latency rose?
5. Do Sentry tags indicate a failure mode like `cache_off`, `slow_query`, or `combined`?

If those align in time, the likely root cause is deploy-introduced performance regression rather than random infrastructure instability.
