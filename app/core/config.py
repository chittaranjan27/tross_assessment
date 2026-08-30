from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # API Settings
    api_title: str = "LinkedIn Profile API"
    api_version: str = "1.0.0"
    log_level: str = "INFO"
    api_key: Optional[str] = None

    # LinkedIn Auth
    linkedin_session_cookie: str = ""
    linkedin_csrf_token: str = ""
    linkedin_user_agent: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"
    )

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    cache_ttl_seconds: int = 21600

    # Provider Settings
    upstream_timeout_seconds: int = 20
    rate_limit_requests_per_minute: int = 60

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )


settings = Settings()
