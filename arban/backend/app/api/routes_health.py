from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint."""
    from .config import get_settings
    settings = get_settings()
    
    return HealthResponse(
        status="ok",
        version=settings.APP_VERSION,
    )


class ProviderHealthResponse(BaseModel):
    polymarket: str = "UNKNOWN"
    kalshi: str = "UNKNOWN"
    limitless: str = "UNKNOWN"
    crypto_com: str = "UNKNOWN"


@router.get("/health/providers", response_model=ProviderHealthResponse)
async def provider_health_check():
    """Check health status of all providers."""
    # In MVP, return UNKNOWN for all
    # Real implementation would ping each provider
    return ProviderHealthResponse(
        polymarket="UNKNOWN",
        kalshi="UNKNOWN",
        limitless="UNKNOWN",
        crypto_com="UNKNOWN",
    )
