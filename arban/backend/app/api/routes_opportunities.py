from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/opportunities")


class ArbitrageLeg(BaseModel):
    provider: str
    market_id: str
    outcome: str
    side: str  # "buy" or "sell"
    price: float
    size: float
    cost: float


class ArbitrageOpportunity(BaseModel):
    id: str
    type: str  # "binary" or "multi_outcome"
    classification: str  # "THEORETICAL", "POTENTIAL", "EXECUTABLE", "GUARANTEED"
    event_name: str
    providers: List[str]
    legs: List[ArbitrageLeg]
    capital_required: float
    gross_profit: float
    gross_roi: float
    net_profit: Optional[float] = None
    net_roi: Optional[float] = None
    liquidity: float
    confidence: float
    detected_at: datetime
    status: str


@router.get("/opportunities", response_model=List[ArbitrageOpportunity])
async def list_opportunities(
    provider: Optional[str] = Query(None),
    min_roi: float = Query(0.0, ge=0),
    classification: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
):
    """List arbitrage opportunities with filters."""
    # MVP: Return empty list
    # Real implementation would query database and run scanner
    return []


@router.get("/opportunities/{opportunity_id}", response_model=ArbitrageOpportunity)
async def get_opportunity(opportunity_id: str):
    """Get detailed information about a specific opportunity."""
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Opportunity not found")
