import time
from typing import Optional

import sentry_sdk
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.models import UserProfile
from app.settings import settings

# In-memory cache keyed by user_id; cleared on process restart
_cache: dict[int, UserProfile] = {}


def get_profile(user_id: int, db: Session) -> Optional[UserProfile]:
    """Fetch a UserProfile by ID with deterministic failure mode behavior."""
    sentry_sdk.set_tag("failure_mode", settings.failure_mode)

    try:
        if settings.failure_mode == "none":
            return _fetch_with_cache(user_id, db)
        elif settings.failure_mode == "cache_off":
            return _fetch_cache_off(user_id, db)
        elif settings.failure_mode == "slow_query":
            return _fetch_slow_query(user_id, db)
        elif settings.failure_mode == "pool_saturation":
            return _fetch_pool_saturation(user_id, db)
        elif settings.failure_mode == "combined":
            return _fetch_combined(user_id, db)
        else:
            return _fetch_with_cache(user_id, db)
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise


def _fetch_with_cache(user_id: int, db: Session) -> Optional[UserProfile]:
    """Normal mode: check in-memory cache first, fall back to DB."""
    if user_id in _cache:
        return _cache[user_id]
    profile = db.query(UserProfile).filter(UserProfile.id == user_id).first()
    if profile:
        _cache[user_id] = profile
    return profile


def _fetch_cache_off(user_id: int, db: Session) -> Optional[UserProfile]:
    """Cache disabled: always query DB directly."""
    sentry_sdk.add_breadcrumb(
        message="Cache bypassed — querying DB directly",
        category="cache",
        level="warning",
        data={"user_id": user_id},
    )
    return db.query(UserProfile).filter(UserProfile.id == user_id).first()


def _fetch_slow_query(user_id: int, db: Session) -> Optional[UserProfile]:
    """Slow query: artificial 2-second delay before DB fetch."""
    sentry_sdk.set_tag("slow_query", "true")
    time.sleep(2)
    return db.query(UserProfile).filter(UserProfile.id == user_id).first()


def _fetch_pool_saturation(user_id: int, db: Session) -> Optional[UserProfile]:
    """Pool saturation: hold connection briefly, then raise OperationalError."""
    time.sleep(1)
    raise OperationalError(
        statement="simulated pool saturation — connection pool exhausted",
        params=None,
        orig=Exception("pool timeout: all connections in use"),
    )


def _fetch_combined(user_id: int, db: Session) -> Optional[UserProfile]:
    """Combined: no cache + slow query delay + pool saturation error."""
    sentry_sdk.add_breadcrumb(
        message="Cache bypassed — querying DB directly",
        category="cache",
        level="warning",
        data={"user_id": user_id},
    )
    sentry_sdk.set_tag("slow_query", "true")
    time.sleep(2)
    raise OperationalError(
        statement="simulated pool saturation under combined failure mode",
        params=None,
        orig=Exception("pool timeout: all connections in use"),
    )
