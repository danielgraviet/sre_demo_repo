import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

from app.settings import settings


def init_sentry() -> None:
    """Initialize Sentry SDK. No-op when SENTRY_DSN is empty."""
    if not settings.sentry_dsn:
        return

    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        integrations=[
            FastApiIntegration(),
            SqlalchemyIntegration(),
        ],
        traces_sample_rate=1.0,
        environment=settings.env,
    )

    sentry_sdk.set_tag("service", "mock-sre-service")
    sentry_sdk.set_tag("demo_scenario", "incident_b")
