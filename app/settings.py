from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    sentry_dsn: str = ""
    env: str = "local"
    database_url: str = "sqlite:///./app.db"
    disable_cache: bool = False
    enable_slow_query: bool = False
    db_pool_limit: int = 20
    inject_timeout_errors: bool = False
    failure_mode: str = "none"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
