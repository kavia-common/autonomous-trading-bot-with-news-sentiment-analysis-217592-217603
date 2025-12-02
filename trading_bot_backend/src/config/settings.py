from functools import lru_cache
from typing import List, Optional

from pydantic import Field
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

    # App
    ENV: str = Field(default="development", description="Environment name")
    LOG_LEVEL: str = Field(default="INFO", description="Log level for structured logging")
    CORS_ALLOW_ORIGINS: List[str] = Field(default_factory=lambda: ["*"], description="Allowed CORS origins (CSV or list)")
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


settings = get_settings()


# PUBLIC_INTERFACE
def get_settings_summary() -> dict:
    """Return a sanitized summary of settings (for health and debugging)."""
    return {
        "ENV": settings.ENV,
        "LOG_LEVEL": settings.LOG_LEVEL,
        "SCHEDULER_ENABLED": settings.SCHEDULER_ENABLED,
        "SCHEDULER_INTERVAL_SECONDS": settings.SCHEDULER_INTERVAL_SECONDS,
        "DB": f"{settings.MYSQL_DB}@{settings.MYSQL_URL}:{settings.MYSQL_PORT}",
        "CORS_ALLOW_ORIGINS": settings.CORS_ALLOW_ORIGINS,
        "SYMBOLS": settings.SYMBOLS,
        "NewsAPI_configured": bool(settings.NEWSAPI_KEY),
        "Zerodha_configured": bool(settings.ZERODHA_API_KEY and settings.ZERODHA_API_SECRET),
    }
