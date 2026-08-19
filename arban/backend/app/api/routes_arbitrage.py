from fastapi import APIRouter, Query
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter(prefix="/arbitrage")


class BinaryArbitrageResult(BaseModel):
    event_name: str
    yes_provider: str
    yes_price: float
    no_provider: str
    no_price: float
    total_cost: float
    gross_profit: float
    gross_roi: float
    is_arbitrage: bool


class MultiOutcomeArbitrageResult(BaseModel):
    event_name: str
    outcomes: List[Dict[str, float]]  # {outcome_name: price}
    total_cost: float
    gross_profit: float
    gross_roi: float
    is_arbitrage: bool


@router.get("/arbitrage/binary", response_model=List[BinaryArbitrageResult])
async def detect_binary_arbitrage(
    min_roi: float = Query(0.0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Detect binary arbitrage opportunities."""
    # MVP: Return empty list
    return []


@router.get(
    "/arbitrage/multi-outcome", response_model=List[MultiOutcomeArbitrageResult]
)
async def detect_multi_outcome_arbitrage(
    min_roi: float = Query(0.0, ge=0),
    limit: int = Query(50, ge=1, le=200),
):
    """Detect multi-outcome arbitrage opportunities."""
    # MVP: Return empty list
    return []
