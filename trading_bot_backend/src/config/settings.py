from functools import lru_cache
from typing import List, Optional, Literal, Union

from pydantic import Field, AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Uses .env file when present. Do not commit real secrets; use .env and .env.example.
    Accepts extra environment variables without failing validation to improve deploy safety.
    """
    # Allow extra env vars so unexpected keys do not break startup.
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App/Server URLs and CORS
    backend_url: Optional[Union[AnyUrl, str]] = Field(
        default=None, alias="BACKEND_URL", description="Public backend base URL"
    )
    frontend_url: Optional[Union[AnyUrl, str]] = Field(
        default=None, alias="FRONTEND_URL", description="Frontend base URL"
    )
    ws_url: Optional[Union[AnyUrl, str]] = Field(
        default=None, alias="WS_URL", description="WebSocket base URL"
    )
    site_url: Optional[Union[AnyUrl, str]] = Field(
        default=None, alias="SITE_URL", description="Site URL used for redirects"
    )

    # Backwards-compatible existing CORS setting + new aliases
    CORS_ALLOW_ORIGINS: List[str] = Field(
        default_factory=lambda: ["*"],
        description="Allowed CORS origins (CSV or list)",
        alias="ALLOW_ORIGINS",
    )
    allowed_origins: Optional[Union[List[str], str]] = Field(
        default=None, alias="ALLOW_ORIGINS", description="Alias for CORS allow origins"
    )
    allowed_headers: Optional[Union[List[str], str]] = Field(
        default=None, alias="ALLOW_HEADERS", description="CORS allowed headers"
    )
    allowed_methods: Optional[Union[List[str], str]] = Field(
        default=None, alias="ALLOW_METHODS", description="CORS allowed methods"
    )
    cors_max_age: int = Field(default=600, alias="CORS_MAX_AGE", description="CORS preflight max age (seconds)")
    cookie_domain: Optional[str] = Field(default=None, alias="COOKIE_DOMAIN", description="Cookie domain")
    trust_proxy: bool = Field(default=False, alias="TRUST_PROXY", description="Trust proxy headers (X-Forwarded-*)")
    host: str = Field(default="0.0.0.0", alias="HOST", description="App host binding")
    uvicorn_host: str = Field(default="0.0.0.0", alias="UVICORN_HOST", description="Uvicorn host binding")
    uvicorn_workers: int = Field(default=1, alias="UVICORN_WORKERS", description="Uvicorn workers")
    node_env: Literal["development", "production", "test"] = Field(
        default="development", alias="NODE_ENV", description="Node-style environment"
    )
    request_timeout_ms: int = Field(default=30000, alias="REQUEST_TIMEOUT_MS", description="Request timeout (ms)")
    rate_limit_window_s: int = Field(default=60, alias="RATE_LIMIT_WINDOW_S", description="Rate limit window (s)")
    rate_limit_max: int = Field(default=100, alias="RATE_LIMIT_MAX", description="Rate limit max requests per window")
    port: int = Field(default=3001, alias="PORT", description="App port")

    # Existing App controls
    ENV: str = Field(default="development", description="Environment name")
    LOG_LEVEL: str = Field(default="INFO", description="Log level for structured logging")
    SCHEDULER_ENABLED: bool = Field(default=True, description="Enable periodic trading loop scheduler")
    SCHEDULER_INTERVAL_SECONDS: int = Field(default=300, description="Interval for trading loop in seconds")

    # Database (MySQL)
    MYSQL_URL: str = Field(..., description="MySQL host or full SQLAlchemy URL. If host provided, we construct DSN.")
    MYSQL_USER: str = Field(..., description="MySQL username")
    MYSQL_PASSWORD: str = Field(..., description="MySQL password")
    MYSQL_DB: str = Field(..., description="Database name")
    MYSQL_PORT: int = Field(default=3306, description="MySQL port")

    # Broker (Zerodha/KiteConnect)
    ZERODHA_API_KEY: Optional[str] = Field(default=None, description="KiteConnect API Key")
    ZERODHA_API_SECRET: Optional[str] = Field(default=None, description="KiteConnect API Secret")
    ZERODHA_REDIRECT_URL: Optional[str] = Field(default=None, description="OAuth redirect URL for login flow")
    ZERODHA_ACCESS_TOKEN: Optional[str] = Field(default=None, description="Kite access token (post-login)")

    # NewsAPI
    NEWSAPI_KEY: Optional[str] = Field(default=None, description="NewsAPI.org API key")
    NEWSAPI_LANGUAGE: str = Field(default="en", description="Language filter for news")

    # Risk management
    MAX_DAILY_LOSS: float = Field(default=1000.0, description="Max allowed daily loss")
    MAX_TRADE_RISK: float = Field(default=250.0, description="Max risk per trade")
    POSITION_SIZE: int = Field(default=1, description="Default position size (lots or units)")
    SYMBOLS: List[str] = Field(default_factory=lambda: ["NIFTY", "BANKNIFTY"], description="Symbols universe")

    # PUBLIC_INTERFACE
    def sqlalchemy_dsn(self) -> str:
        """
        Build SQLAlchemy DSN with PyMySQL driver if a full URL is not provided.

        Returns:
            str: SQLAlchemy DSN string.
        """
        if self.MYSQL_URL.startswith("mysql"):
            return self.MYSQL_URL
        host = self.MYSQL_URL
        return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{host}:{self.MYSQL_PORT}/{self.MYSQL_DB}"


@lru_cache
# PUBLIC_INTERFACE
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()


# Note: avoid instantiating at import time to keep lazy loading.
# Use get_settings() in call sites to access settings.

# PUBLIC_INTERFACE
def get_settings_summary() -> dict:
    """Return a sanitized summary of settings (for health and debugging)."""
    s = get_settings()
    return {
        "ENV": s.ENV,
        "LOG_LEVEL": s.LOG_LEVEL,
        "SCHEDULER_ENABLED": s.SCHEDULER_ENABLED,
        "SCHEDULER_INTERVAL_SECONDS": s.SCHEDULER_INTERVAL_SECONDS,
        "DB": f"{s.MYSQL_DB}@{s.MYSQL_URL}:{s.MYSQL_PORT}",
        "CORS_ALLOW_ORIGINS": s.CORS_ALLOW_ORIGINS,
        "SYMBOLS": s.SYMBOLS,
        "NewsAPI_configured": bool(s.NEWSAPI_KEY),
        "Zerodha_configured": bool(s.ZERODHA_API_KEY and s.ZERODHA_API_SECRET),
    }
