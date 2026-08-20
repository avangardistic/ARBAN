from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_ENV: str = "development"
    APP_NAME: str = "ARBAN"
    APP_VERSION: str = "0.1.0"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://arban:arban@postgres:5432/arban"

    # Redis
    REDIS_URL: str = "redis://redis:6379/0"

    # Scanner
    SCAN_INTERVAL_SECONDS: int = 5
    MAX_QUOTE_AGE_SECONDS: int = 5

    # Arbitrage thresholds (percentage)
    MIN_ARBITRAGE_ROI: float = 0.5
    MIN_NET_ROI: float = 0.25

    # Providers
    POLYMARKET_ENABLED: bool = True
    KALSHI_ENABLED: bool = True
    LIMITLESS_ENABLED: bool = True
    CRYPTO_COM_ENABLED: bool = True

    POLYMARKET_API_URL: str = ""
    KALSHI_API_URL: str = ""
    LIMITLESS_API_URL: str = ""
    CRYPTO_COM_API_URL: str = ""

    # Fees
    POLYMARKET_FEE_RATE: float = 0.0
    KALSHI_FEE_RATE: float = 0.0
    LIMITLESS_FEE_RATE: float = 0.0
    CRYPTO_COM_FEE_RATE: float = 0.0
    NETWORK_FEE_ESTIMATE: float = 0.0

    # Rate limiting
    REQUEST_TIMEOUT_SECONDS: int = 10
    MAX_RETRIES: int = 3
    RATE_LIMIT_PER_SECOND: int = 10

    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
