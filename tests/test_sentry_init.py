from unittest.mock import patch

from app.sentry import init_sentry
from app.settings import settings


def test_sentry_init_with_empty_dsn_does_not_raise():
    original = settings.sentry_dsn
    settings.sentry_dsn = ""
    try:
        init_sentry()  # must be a no-op — no exception
    finally:
        settings.sentry_dsn = original


def test_sentry_init_with_mock_dsn():
    original = settings.sentry_dsn
    settings.sentry_dsn = "https://fake@o0.ingest.sentry.io/0"
    try:
        with patch("sentry_sdk.init") as mock_init:
            init_sentry()
            mock_init.assert_called_once()
            call_kwargs = mock_init.call_args.kwargs
            assert call_kwargs["dsn"] == "https://fake@o0.ingest.sentry.io/0"
    finally:
        settings.sentry_dsn = original
