"""
ARBAN Odds Engine Module

Provides comprehensive odds calculation and conversion functionality.
"""

from .engine import (
    # Enums
    OddsFormat,
    
    # Data classes
    Odds,
    ImpliedProbability,
    FairProbability,
    Overround,
    ExpectedValue,
    ArbitrageMargin,
    StakeAllocation,
    
    # Exceptions
    OddsError,
    InvalidOddsError,
    ConversionError,
    
    # Core functions
    decimal_to_implied_probability,
    american_to_implied_probability,
    fractional_to_implied_probability,
    convert_odds_to_probability,
    probability_to_decimal_odds,
    probability_to_american_odds,
    probability_to_fractional_odds,
    decimal_to_american,
    decimal_to_fractional,
    american_to_decimal,
    fractional_to_decimal,
    calculate_overround,
    calculate_fair_probabilities,
    calculate_expected_value,
    calculate_arbitrage_margin,
    calculate_stake_allocation,
    prediction_price_to_odds,
    odds_to_prediction_price,
    
    # Main engine class
    OddsEngine,
)

__all__ = [
    # Enums
    "OddsFormat",
    
    # Data classes
    "Odds",
    "ImpliedProbability",
    "FairProbability",
    "Overround",
    "ExpectedValue",
    "ArbitrageMargin",
    "StakeAllocation",
    
    # Exceptions
    "OddsError",
    "InvalidOddsError",
    "ConversionError",
    
    # Core functions
    "decimal_to_implied_probability",
    "american_to_implied_probability",
    "fractional_to_implied_probability",
    "convert_odds_to_probability",
    "probability_to_decimal_odds",
    "probability_to_american_odds",
    "probability_to_fractional_odds",
    "decimal_to_american",
    "decimal_to_fractional",
    "american_to_decimal",
    "fractional_to_decimal",
    "calculate_overround",
    "calculate_fair_probabilities",
    "calculate_expected_value",
    "calculate_arbitrage_margin",
    "calculate_stake_allocation",
    "prediction_price_to_odds",
    "odds_to_prediction_price",
    
    # Main engine class
    "OddsEngine",
]
