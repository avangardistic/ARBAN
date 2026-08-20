"""
ARBAN Odds API Routes

Provides REST endpoints for odds calculations and conversions.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime

from ..odds import (
    OddsFormat,
    OddsEngine,
    ImpliedProbability,
    Overround,
    ExpectedValue,
    ArbitrageMargin,
    StakeAllocation,
    InvalidOddsError,
)


router = APIRouter(prefix="/odds", tags=["Odds"])


class OddsConvertRequest(BaseModel):
    """Request for odds conversion."""
    value: float = Field(..., description="Odds value")
    from_format: str = Field(..., description="Source format: decimal, american, fractional")
    to_format: str = Field(..., description="Target format: decimal, american, fractional")


class OddsConvertResponse(BaseModel):
    """Response for odds conversion."""
    original_value: float
    original_format: str
    converted_value: float
    converted_format: str


class ImpliedProbabilityRequest(BaseModel):
    """Request for implied probability calculation."""
    value: float = Field(..., description="Odds value")
    format: str = Field(..., description="Odds format: decimal, american, fractional")


class ImpliedProbabilityResponse(BaseModel):
    """Response for implied probability calculation."""
    odds_value: float
    odds_format: str
    implied_probability: float
    implied_probability_percentage: str


class OverroundRequest(BaseModel):
    """Request for overround calculation."""
    odds: List[float] = Field(..., description="List of decimal odds for all outcomes")


class OverroundResponse(BaseModel):
    """Response for overround calculation."""
    odds: List[float]
    implied_probabilities: List[float]
    total_implied_probability: float
    overround: float
    overround_percentage: float
    fair_probabilities: List[float]


class ExpectedValueRequest(BaseModel):
    """Request for expected value calculation."""
    your_probability: float = Field(..., description="Your estimated true probability")
    decimal_odds: float = Field(..., description="Offered decimal odds")


class ExpectedValueResponse(BaseModel):
    """Response for expected value calculation."""
    your_probability: float
    decimal_odds: float
    ev_decimal: float
    ev_percentage: float
    is_positive: bool


class ArbitrageRequest(BaseModel):
    """Request for arbitrage detection."""
    odds: List[float] = Field(..., description="Decimal odds for all mutually exclusive outcomes")


class ArbitrageResponse(BaseModel):
    """Response for arbitrage detection."""
    odds: List[float]
    sum_inverse_odds: float
    arbitrage_margin: float
    arbitrage_percentage: float
    has_arbitrage: bool


class StakeAllocationRequest(BaseModel):
    """Request for stake allocation calculation."""
    capital: float = Field(..., description="Total capital to deploy")
    odds: List[float] = Field(..., description="Decimal odds for all outcomes")


class StakeAllocationResponse(BaseModel):
    """Response for stake allocation calculation."""
    stakes: List[float]
    total_stake: float
    gross_payout: float
    profit: float
    roi_percentage: float
    has_arbitrage: bool


class FullAnalysisRequest(BaseModel):
    """Request for comprehensive odds analysis."""
    odds: List[float] = Field(..., description="Decimal odds for all outcomes")
    format: str = Field(default="decimal", description="Odds format")
    your_probabilities: Optional[List[float]] = Field(None, description="Your probability estimates")
    capital: Optional[float] = Field(None, description="Capital for stake allocation")


class FullAnalysisResponse(BaseModel):
    """Response for comprehensive odds analysis."""
    odds: List[str]
    implied_probabilities: List[str]
    fair_probabilities: List[str]
    overround: str
    arbitrage: dict
    expected_values: Optional[List[str]] = None
    stake_allocation: Optional[dict] = None


def parse_odds_format(format_str: str) -> OddsFormat:
    """Parse string format to OddsFormat enum."""
    format_map = {
        "decimal": OddsFormat.DECIMAL,
        "american": OddsFormat.AMERICAN,
        "fractional": OddsFormat.FRACTIONAL,
    }
    try:
        return format_map[format_str.lower()]
    except KeyError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid format: {format_str}. Must be one of: decimal, american, fractional"
        )


@router.post("/convert", response_model=OddsConvertResponse)
async def convert_odds(request: OddsConvertRequest):
    """Convert odds from one format to another."""
    try:
        from_format = parse_odds_format(request.from_format)
        to_format = parse_odds_format(request.to_format)
        
        converted = OddsEngine.convert(
            Decimal(str(request.value)),
            from_format,
            to_format
        )
        
        return OddsConvertResponse(
            original_value=request.value,
            original_format=request.from_format,
            converted_value=float(converted),
            converted_format=request.to_format
        )
    except InvalidOddsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Conversion error: {str(e)}")


@router.post("/implied-probability", response_model=ImpliedProbabilityResponse)
async def get_implied_probability(request: ImpliedProbabilityRequest):
    """Calculate implied probability from odds."""
    try:
        fmt = parse_odds_format(request.format)
        result = OddsEngine.get_implied_probability(
            Decimal(str(request.value)),
            fmt
        )
        
        return ImpliedProbabilityResponse(
            odds_value=request.value,
            odds_format=request.format,
            implied_probability=float(result.probability),
            implied_probability_percentage=str(result)
        )
    except InvalidOddsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/overround", response_model=OverroundResponse)
async def calculate_overround(request: OverroundRequest):
    """Calculate overround/vig for a set of odds."""
    try:
        decimal_odds = [Decimal(str(o)) for o in request.odds]
        overround_result = OddsEngine.get_overround(decimal_odds)
        fair_probs = OddsEngine.get_fair_probabilities(decimal_odds)
        
        return OverroundResponse(
            odds=request.odds,
            implied_probabilities=[float(p) for p in [Decimal(1)/o for o in decimal_odds]],
            total_implied_probability=float(overround_result.total_implied_probability),
            overround=float(overround_result.overround),
            overround_percentage=float(overround_result.overround_percentage),
            fair_probabilities=[float(fp.probability) for fp in fair_probs]
        )
    except InvalidOddsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/expected-value", response_model=ExpectedValueResponse)
async def calculate_expected_value(request: ExpectedValueRequest):
    """Calculate expected value for a bet."""
    try:
        result = OddsEngine.calculate_ev(
            Decimal(str(request.your_probability)),
            Decimal(str(request.decimal_odds))
        )
        
        return ExpectedValueResponse(
            your_probability=request.your_probability,
            decimal_odds=request.decimal_odds,
            ev_decimal=float(result.ev_decimal),
            ev_percentage=float(result.ev_percentage),
            is_positive=result.is_positive
        )
    except InvalidOddsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/arbitrage", response_model=ArbitrageResponse)
async def detect_arbitrage(request: ArbitrageRequest):
    """Detect arbitrage opportunity in a set of odds."""
    try:
        decimal_odds = [Decimal(str(o)) for o in request.odds]
        result = OddsEngine.detect_arbitrage(decimal_odds)
        
        return ArbitrageResponse(
            odds=request.odds,
            sum_inverse_odds=float(result.sum_inverse_odds),
            arbitrage_margin=float(result.arbitrage_margin),
            arbitrage_percentage=float(result.arbitrage_percentage),
            has_arbitrage=result.has_arbitrage
        )
    except InvalidOddsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/stakes", response_model=StakeAllocationResponse)
async def calculate_stakes(request: StakeAllocationRequest):
    """Calculate optimal stake allocation for arbitrage."""
    try:
        decimal_odds = [Decimal(str(o)) for o in request.odds]
        capital = Decimal(str(request.capital))
        
        arb_result = OddsEngine.detect_arbitrage(decimal_odds)
        if not arb_result.has_arbitrage:
            # Still return stakes but indicate no arbitrage
            stakes_result = OddsEngine.calculate_stakes(capital, decimal_odds)
            return StakeAllocationResponse(
                stakes=[float(s) for s in stakes_result.stakes],
                total_stake=float(stakes_result.total_stake),
                gross_payout=float(stakes_result.gross_payout),
                profit=float(stakes_result.profit),
                roi_percentage=float(stakes_result.roi) * 100,
                has_arbitrage=False
            )
        
        stakes_result = OddsEngine.calculate_stakes(capital, decimal_odds)
        
        return StakeAllocationResponse(
            stakes=[float(s) for s in stakes_result.stakes],
            total_stake=float(stakes_result.total_stake),
            gross_payout=float(stakes_result.gross_payout),
            profit=float(stakes_result.profit),
            roi_percentage=float(stakes_result.roi) * 100,
            has_arbitrage=True
        )
    except InvalidOddsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calculation error: {str(e)}")


@router.post("/analyze", response_model=FullAnalysisResponse)
async def full_analysis(request: FullAnalysisRequest):
    """Perform comprehensive analysis on a set of odds."""
    try:
        fmt = parse_odds_format(request.format)
        decimal_odds = [Decimal(str(o)) for o in request.odds]
        
        your_probs = None
        if request.your_probabilities:
            your_probs = [Decimal(str(p)) for p in request.your_probabilities]
        
        capital = None
        if request.capital:
            capital = Decimal(str(request.capital))
        
        result = OddsEngine.full_analysis(
            decimal_odds,
            fmt,
            your_probs,
            capital
        )
        
        return FullAnalysisResponse(**result)
    except InvalidOddsError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")


@router.get("/", response_model=dict)
async def get_odds_info():
    """Get information about the odds engine capabilities."""
    return {
        "name": "ARBAN Odds Engine",
        "version": "1.0.0",
        "supported_formats": ["decimal", "american", "fractional"],
        "capabilities": [
            "odds_conversion",
            "implied_probability",
            "fair_probability",
            "overround_vig",
            "expected_value",
            "arbitrage_detection",
            "stake_allocation"
        ],
        "endpoints": {
            "/api/v1/odds/convert": "Convert between odds formats",
            "/api/v1/odds/implied-probability": "Calculate implied probability",
            "/api/v1/odds/overround": "Calculate bookmaker overround/vig",
            "/api/v1/odds/expected-value": "Calculate expected value",
            "/api/v1/odds/arbitrage": "Detect arbitrage opportunities",
            "/api/v1/odds/stakes": "Calculate optimal stake allocation",
            "/api/v1/odds/analyze": "Comprehensive odds analysis"
        }
    }
