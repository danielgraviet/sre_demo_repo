import time
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

from app.main import app
from app.settings import settings


def test_cache_off_mode_still_returns_profile(client):
    settings.failure_mode = "cache_off"
    r = client.get("/api/users/profile/1")
    assert r.status_code == 200
    assert r.json()["id"] == 1
    assert r.headers["x-failure-mode"] == "cache_off"


def test_slow_query_mode_adds_latency(client):
    settings.failure_mode = "slow_query"
    start = time.monotonic()
    r = client.get("/api/users/profile/1")
    elapsed = time.monotonic() - start
    assert r.status_code == 200
    assert elapsed > 1.5, f"Expected >1.5s latency, got {elapsed:.2f}s"


def test_pool_saturation_mode_returns_error_under_load():
    settings.failure_mode = "pool_saturation"
    with TestClient(app) as c:
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(c.get, "/api/users/profile/1") for _ in range(5)]
            responses = [f.result() for f in futures]
    status_codes = [r.status_code for r in responses]
    assert any(code != 200 for code in status_codes), f"Expected at least one non-200, got {status_codes}"


def test_combined_mode_returns_server_error_or_high_latency(client):
    settings.failure_mode = "combined"
    start = time.monotonic()
    r = client.get("/api/users/profile/1")
    elapsed = time.monotonic() - start
    assert r.status_code >= 500 or elapsed > 1.5, (
        f"Expected 5xx or >1.5s latency; got status={r.status_code}, elapsed={elapsed:.2f}s"
    )
