from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter(prefix="/markets")


class MarketResponse(BaseModel):
    provider: str
    market_id: str
    event_id: str
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    status: str
    outcomes: List[dict]


@router.get("/markets", response_model=List[MarketResponse])
async def list_markets(
    provider: Optional[str] = Query(None, description="Filter by provider"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=200),
):
    """List all markets with optional filters."""
    # MVP: Return empty list
    # Real implementation would query database
    return []


@router.get("/markets/{market_id}", response_model=MarketResponse)
async def get_market(market_id: str, provider: str = Query(...)):
    """Get a specific market by ID and provider."""
    # MVP: Return 404
    # Real implementation would query database
    raise HTTPException(status_code=404, detail="Market not found")
