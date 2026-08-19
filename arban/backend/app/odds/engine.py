"""
ARBAN Odds Engine

Comprehensive odds calculation and conversion engine supporting:
- Decimal odds
- American odds (positive and negative)
- Fractional odds
- Implied probability
- Fair probability (normalized)
- Overround/Vig calculation
- Expected Value (EV)
- Arbitrage detection and stake allocation

All calculations use Decimal for precision.
"""

from decimal import Decimal, ROUND_HALF_UP, DivisionByZero, InvalidOperation
from typing import Tuple, List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum
import math


class OddsFormat(Enum):
    """Supported odds formats."""
    DECIMAL = "decimal"
    AMERICAN = "american"
    FRACTIONAL = "fractional"


@dataclass
class Odds:
    """Represents odds in any format."""
    value: Decimal
    format: OddsFormat
    
    def __str__(self) -> str:
        if self.format == OddsFormat.DECIMAL:
            return f"{self.value:.2f}"
        elif self.format == OddsFormat.AMERICAN:
            sign = "+" if self.value > 0 else ""
            return f"{sign}{int(self.value)}"
        else:  # FRACTIONAL
            return str(self.value)


@dataclass
class ImpliedProbability:
    """Implied probability from odds."""
    probability: Decimal
    source_odds: Odds
    
    def percentage(self) -> float:
        return float(self.probability * 100)
    
    def __str__(self) -> str:
        return f"{self.percentage():.2f}%"


@dataclass
class FairProbability:
    """Normalized fair probability after removing overround."""
    probability: Decimal
    original_probability: Decimal
    normalization_factor: Decimal
    
    def percentage(self) -> float:
        return float(self.probability * 100)
    
    def __str__(self) -> str:
        return f"{self.percentage():.2f}%"


@dataclass
class Overround:
    """Bookmaker overround/vig calculation."""
    total_implied_probability: Decimal
    overround: Decimal
    overround_percentage: Decimal
    
    def __str__(self) -> str:
        return f"{float(self.overround_percentage):.2f}%"


@dataclass
class ExpectedValue:
    """Expected value calculation result."""
    ev_decimal: Decimal
    ev_percentage: Decimal
    is_positive: bool
    
    def __str__(self) -> str:
        sign = "+" if self.is_positive else ""
        return f"{sign}{float(self.ev_percentage):.2f}%"


@dataclass
class ArbitrageMargin:
    """Arbitrage margin calculation."""
    sum_inverse_odds: Decimal
    arbitrage_margin: Decimal
    arbitrage_percentage: Decimal
    has_arbitrage: bool
    
    def __str__(self) -> str:
        if self.has_arbitrage:
            return f"+{float(self.arbitrage_percentage):.2f}%"
        return f"{float(self.arbitrage_percentage):.2f}%"


@dataclass
class StakeAllocation:
    """Optimal stake allocation for arbitrage."""
    stakes: List[Decimal]
    total_stake: Decimal
    gross_payout: Decimal
    profit: Decimal
    roi: Decimal
    
    def __str__(self) -> str:
        return f"Stakes: {[float(s) for s in self.stakes]}, Profit: ${float(self.profit):.2f}, ROI: {float(self.roi)*100:.2f}%"


class OddsError(Exception):
    """Base exception for odds calculations."""
    pass


class InvalidOddsError(OddsError):
    """Raised when odds values are invalid."""
    pass


class ConversionError(OddsError):
    """Raised when conversion fails."""
    pass


def decimal_to_implied_probability(decimal_odds: Decimal) -> Decimal:
    """
    Convert decimal odds to implied probability.
    
    Formula: p = 1 / decimal_odds
    
    Example:
        2.00 → 0.50
        3.00 → 0.333...
        1.50 → 0.666...
    
    Args:
        decimal_odds: Decimal odds value (must be > 0)
    
    Returns:
        Implied probability as Decimal
    
    Raises:
        InvalidOddsError: If decimal_odds <= 0
    """
    if decimal_odds <= 0:
        raise InvalidOddsError("Decimal odds must be positive")
    
    try:
        return Decimal(1) / decimal_odds
    except DivisionByZero:
        raise InvalidOddsError("Division by zero in decimal odds conversion")


def american_to_implied_probability(american_odds: Decimal) -> Decimal:
    """
    Convert American odds to implied probability.
    
    For positive American odds (A > 0):
        p = 100 / (A + 100)
    
    For negative American odds (A < 0):
        p = -A / (-A + 100)
    
    Examples:
        +150 → 100/250 = 0.40
        -150 → 150/250 = 0.60
        +100 → 100/200 = 0.50
        -100 → 100/200 = 0.50
    
    Args:
        american_odds: American odds value (cannot be 0)
    
    Returns:
        Implied probability as Decimal
    
    Raises:
        InvalidOddsError: If american_odds is 0 or invalid
    """
    if american_odds == 0:
        raise InvalidOddsError("American odds cannot be zero")
    
    try:
        if american_odds > 0:
            return Decimal(100) / (american_odds + Decimal(100))
        else:
            abs_odds = abs(american_odds)
            return abs_odds / (abs_odds + Decimal(100))
    except DivisionByZero:
        raise InvalidOddsError("Division by zero in American odds conversion")


def fractional_to_implied_probability(numerator: Decimal, denominator: Decimal) -> Decimal:
    """
    Convert fractional odds to implied probability.
    
    Formula: p = 1 / (1 + a/b) = b / (a + b)
    
    Examples:
        3/2 → 2/(3+2) = 0.40
        1/1 → 1/(1+1) = 0.50
        2/1 → 1/(2+1) = 0.333...
    
    Args:
        numerator: Numerator of fractional odds
        denominator: Denominator of fractional odds (must be > 0)
    
    Returns:
        Implied probability as Decimal
    
    Raises:
        InvalidOddsError: If denominator <= 0
    """
    if denominator <= 0:
        raise InvalidOddsError("Fractional odds denominator must be positive")
    
    try:
        return denominator / (numerator + denominator)
    except DivisionByZero:
        raise InvalidOddsError("Division by zero in fractional odds conversion")


def convert_odds_to_probability(value: Decimal, format: OddsFormat) -> Decimal:
    """
    Unified function to convert any odds format to probability.
    
    Args:
        value: The odds value
        format: The format of the odds
    
    Returns:
        Implied probability as Decimal
    
    Examples:
        >>> convert_odds_to_probability(Decimal('2.00'), OddsFormat.DECIMAL)
        Decimal('0.5')
        >>> convert_odds_to_probability(Decimal('+150'), OddsFormat.AMERICAN)
        Decimal('0.4')
        >>> convert_odds_to_probability(Decimal('-150'), OddsFormat.AMERICAN)
        Decimal('0.6')
    """
    if format == OddsFormat.DECIMAL:
        return decimal_to_implied_probability(value)
    elif format == OddsFormat.AMERICAN:
        return american_to_implied_probability(value)
    else:  # FRACTIONAL - value represents numerator/denominator ratio
        # For fractional, we need both numerator and denominator
        # This is a simplified version assuming value is the ratio
        if value <= 0:
            raise InvalidOddsError("Fractional odds must be positive")
        return Decimal(1) / (Decimal(1) + value)


def probability_to_decimal_odds(probability: Decimal) -> Decimal:
    """
    Convert probability to decimal odds.
    
    Formula: decimal_odds = 1 / probability
    
    Examples:
        0.50 → 2.00
        0.25 → 4.00
        0.10 → 10.00
    
    Args:
        probability: Probability value (0 < p <= 1)
    
    Returns:
        Decimal odds
    
    Raises:
        InvalidOddsError: If probability is out of range
    """
    if probability <= 0 or probability > 1:
        raise InvalidOddsError("Probability must be between 0 (exclusive) and 1 (inclusive)")
    
    try:
        return Decimal(1) / probability
    except DivisionByZero:
        raise InvalidOddsError("Division by zero in probability conversion")


def probability_to_american_odds(probability: Decimal) -> Decimal:
    """
    Convert probability to American odds.
    
    For p >= 0.5:
        A = -100 * p / (1 - p)
    
    For p < 0.5:
        A = 100 * (1 - p) / p
    
    Examples:
        0.50 → +100
        0.60 → -150
        0.40 → +150
    
    Args:
        probability: Probability value (0 < p < 1)
    
    Returns:
        American odds
    
    Raises:
        InvalidOddsError: If probability is out of range
    """
    if probability <= 0 or probability >= 1:
        raise InvalidOddsError("Probability must be between 0 and 1 (exclusive)")
    
    try:
        if probability >= Decimal("0.5"):
            return -Decimal(100) * probability / (Decimal(1) - probability)
        else:
            return Decimal(100) * (Decimal(1) - probability) / probability
    except DivisionByZero:
        raise InvalidOddsError("Division by zero in American odds conversion")


def probability_to_fractional_odds(probability: Decimal) -> Tuple[int, int]:
    """
    Convert probability to fractional odds.
    
    First converts to decimal odds, then finds best fractional approximation.
    
    Args:
        probability: Probability value (0 < p < 1)
    
    Returns:
        Tuple of (numerator, denominator)
    
    Raises:
        InvalidOddsError: If probability is out of range
    """
    if probability <= 0 or probability >= 1:
        raise InvalidOddsError("Probability must be between 0 and 1 (exclusive)")
    
    decimal_odds = probability_to_decimal_odds(probability)
    fractional_part = decimal_odds - Decimal(1)
    
    # Find best fractional approximation
    # Using continued fraction method for better accuracy
    max_denominator = 1000
    best_num, best_den = 1, 1
    min_error = float('inf')
    
    for den in range(1, max_denominator + 1):
        num = round(float(fractional_part) * den)
        if num < 1:
            num = 1
        approx = Decimal(num) / Decimal(den)
        error = abs(float(approx - fractional_part))
        
        if error < min_error:
            min_error = error
            best_num, best_den = num, den
        
        if error < 1e-6:
            break
    
    return best_num, best_den


def decimal_to_american(decimal_odds: Decimal) -> Decimal:
    """Convert decimal odds to American odds."""
    if decimal_odds <= 0:
        raise InvalidOddsError("Decimal odds must be positive")
    
    if decimal_odds >= Decimal(2):
        return (decimal_odds - Decimal(1)) * Decimal(100)
    else:
        return -Decimal(100) / (decimal_odds - Decimal(1))


def decimal_to_fractional(decimal_odds: Decimal) -> Tuple[int, int]:
    """Convert decimal odds to fractional odds."""
    if decimal_odds <= Decimal(1):
        raise InvalidOddsError("Decimal odds must be greater than 1")
    
    fractional_part = decimal_odds - Decimal(1)
    probability = Decimal(1) / decimal_odds
    return probability_to_fractional_odds(probability)


def american_to_decimal(american_odds: Decimal) -> Decimal:
    """Convert American odds to decimal odds."""
    if american_odds == 0:
        raise InvalidOddsError("American odds cannot be zero")
    
    if american_odds > 0:
        return american_odds / Decimal(100) + Decimal(1)
    else:
        return Decimal(100) / abs(american_odds) + Decimal(1)


def fractional_to_decimal(numerator: Decimal, denominator: Decimal) -> Decimal:
    """Convert fractional odds to decimal odds."""
    if denominator <= 0:
        raise InvalidOddsError("Denominator must be positive")
    
    return Decimal(1) + (numerator / denominator)


def calculate_overround(implied_probabilities: List[Decimal]) -> Overround:
    """
    Calculate bookmaker overround (vig).
    
    Formula: overround = Σ(pi) - 1
    
    Example:
        p1 = 0.55, p2 = 0.50
        overround = 0.55 + 0.50 - 1 = 0.05 = 5%
    
    Args:
        implied_probabilities: List of implied probabilities for all outcomes
    
    Returns:
        Overround object with total, overround, and percentage
    """
    if not implied_probabilities:
        return Overround(
            total_implied_probability=Decimal(0),
            overround=Decimal(0),
            overround_percentage=Decimal(0)
        )
    
    total = sum(implied_probabilities)
    overround = total - Decimal(1)
    overround_pct = overround * Decimal(100)
    
    return Overround(
        total_implied_probability=total,
        overround=overround,
        overround_percentage=overround_pct
    )


def calculate_fair_probabilities(implied_probabilities: List[Decimal]) -> List[FairProbability]:
    """
    Calculate fair probabilities by normalizing implied probabilities.
    
    Formula: fair_pi = pi / Σ(pj)
    
    This removes the overround to show the "fair" probability distribution.
    
    Example:
        p1 = 0.55, p2 = 0.50
        sum = 1.05
        fair_p1 = 0.55 / 1.05 = 0.5238...
        fair_p2 = 0.50 / 1.05 = 0.4762...
    
    Args:
        implied_probabilities: List of implied probabilities
    
    Returns:
        List of FairProbability objects
    """
    if not implied_probabilities:
        return []
    
    total = sum(implied_probabilities)
    
    if total == 0:
        return [FairProbability(Decimal(0), Decimal(0), Decimal(0)) for _ in implied_probabilities]
    
    normalization_factor = Decimal(1) / total
    
    fair_probs = []
    for p in implied_probabilities:
        fair_p = p * normalization_factor
        fair_probs.append(FairProbability(
            probability=fair_p,
            original_probability=p,
            normalization_factor=normalization_factor
        ))
    
    return fair_probs


def calculate_expected_value(
    true_probability: Decimal,
    decimal_odds: Decimal
) -> ExpectedValue:
    """
    Calculate expected value for a bet.
    
    Formula: EV = p * decimal_odds - 1
    
    Example:
        p = 0.45, odds = 2.50
        EV = 0.45 * 2.50 - 1 = 0.125 = +12.5%
    
    Args:
        true_probability: Your estimated true probability
        decimal_odds: Offered decimal odds
    
    Returns:
        ExpectedValue object
    """
    if true_probability < 0 or true_probability > 1:
        raise InvalidOddsError("Probability must be between 0 and 1")
    
    if decimal_odds <= 0:
        raise InvalidOddsError("Decimal odds must be positive")
    
    ev = true_probability * decimal_odds - Decimal(1)
    ev_pct = ev * Decimal(100)
    
    return ExpectedValue(
        ev_decimal=ev,
        ev_percentage=ev_pct,
        is_positive=ev > 0
    )


def calculate_arbitrage_margin(decimal_odds: List[Decimal]) -> ArbitrageMargin:
    """
    Calculate arbitrage margin for mutually exclusive outcomes.
    
    Formula: arbitrage exists if Σ(1/Oi) < 1
    Margin = 1 - Σ(1/Oi)
    
    Example:
        Odds A = 2.10, Odds B = 2.10
        1/2.10 + 1/2.10 = 0.95238
        Margin = 1 - 0.95238 = 0.0476 = 4.76%
    
    Args:
        decimal_odds: List of decimal odds for all outcomes
    
    Returns:
        ArbitrageMargin object
    """
    if not decimal_odds:
        return ArbitrageMargin(
            sum_inverse_odds=Decimal(0),
            arbitrage_margin=Decimal(0),
            arbitrage_percentage=Decimal(0),
            has_arbitrage=False
        )
    
    for odds in decimal_odds:
        if odds <= 0:
            raise InvalidOddsError("All odds must be positive")
    
    sum_inverse = sum(Decimal(1) / odds for odds in decimal_odds)
    margin = Decimal(1) - sum_inverse
    margin_pct = margin * Decimal(100)
    
    return ArbitrageMargin(
        sum_inverse_odds=sum_inverse,
        arbitrage_margin=margin,
        arbitrage_percentage=margin_pct,
        has_arbitrage=margin > 0
    )


def calculate_stake_allocation(
    capital: Decimal,
    decimal_odds: List[Decimal]
) -> StakeAllocation:
    """
    Calculate optimal stake allocation for arbitrage.
    
    Formula: stake_i = C * (1/Oi) / Σ(1/Oj)
    
    This equalizes payout across all outcomes.
    
    Example:
        Capital = $1000
        Odds A = 2.10, Odds B = 2.10
        stake_A = 1000 * (1/2.10) / (1/2.10 + 1/2.10) = $500
        stake_B = 1000 * (1/2.10) / (1/2.10 + 1/2.10) = $500
    
    Args:
        capital: Total capital to deploy
        decimal_odds: List of decimal odds for all outcomes
    
    Returns:
        StakeAllocation object with stakes, payout, profit, and ROI
    """
    if capital <= 0:
        raise InvalidOddsError("Capital must be positive")
    
    if not decimal_odds:
        return StakeAllocation(
            stakes=[],
            total_stake=Decimal(0),
            gross_payout=Decimal(0),
            profit=Decimal(0),
            roi=Decimal(0)
        )
    
    for odds in decimal_odds:
        if odds <= 0:
            raise InvalidOddsError("All odds must be positive")
    
    # Calculate inverse odds
    inverse_odds = [Decimal(1) / odds for odds in decimal_odds]
    sum_inverse = sum(inverse_odds)
    
    # Calculate stakes
    stakes = []
    for i, inv in enumerate(inverse_odds):
        if i == len(inverse_odds) - 1:
            # Last stake uses remainder to ensure exact capital allocation
            stake = capital - sum(stakes)
        else:
            stake = capital * inv / sum_inverse
            stake = stake.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        stakes.append(stake)
    
    # Calculate payout (same for any outcome)
    gross_payout = stakes[0] * decimal_odds[0]
    
    # Calculate profit and ROI
    profit = gross_payout - capital
    roi = profit / capital if capital > 0 else Decimal(0)
    
    return StakeAllocation(
        stakes=stakes,
        total_stake=capital,
        gross_payout=gross_payout,
        profit=profit,
        roi=roi
    )


def prediction_price_to_odds(price: Decimal) -> Decimal:
    """
    Convert prediction market price to decimal odds equivalent.
    
    For a YES contract at price P:
    - Cost = P
    - Payout = 1.00 if wins
    - Decimal odds = 1/P
    
    Example:
        Price = 0.62
        Decimal odds = 1/0.62 = 1.61
    
    Args:
        price: Prediction market price (0 < price <= 1)
    
    Returns:
        Equivalent decimal odds
    """
    if price <= 0 or price > 1:
        raise InvalidOddsError("Prediction market price must be between 0 and 1")
    
    return Decimal(1) / price


def odds_to_prediction_price(decimal_odds: Decimal) -> Decimal:
    """
    Convert decimal odds to prediction market price equivalent.
    
    Formula: price = 1 / decimal_odds
    
    Args:
        decimal_odds: Decimal odds (> 0)
    
    Returns:
        Equivalent prediction market price
    """
    if decimal_odds <= 0:
        raise InvalidOddsError("Decimal odds must be positive")
    
    return Decimal(1) / decimal_odds


class OddsEngine:
    """
    Main odds calculation engine.
    
    Provides unified interface for all odds-related calculations.
    """
    
    @staticmethod
    def convert(
        value: Decimal,
        from_format: OddsFormat,
        to_format: OddsFormat
    ) -> Decimal:
        """Convert odds from one format to another."""
        # First convert to probability
        probability = convert_odds_to_probability(value, from_format)
        
        # Then convert to target format
        if to_format == OddsFormat.DECIMAL:
            return probability_to_decimal_odds(probability)
        elif to_format == OddsFormat.AMERICAN:
            return probability_to_american_odds(probability)
        else:  # FRACTIONAL
            num, den = probability_to_fractional_odds(probability)
            return Decimal(num) / Decimal(den)
    
    @staticmethod
    def get_implied_probability(value: Decimal, format: OddsFormat) -> ImpliedProbability:
        """Get implied probability from odds."""
        prob = convert_odds_to_probability(value, format)
        return ImpliedProbability(
            probability=prob,
            source_odds=Odds(value=value, format=format)
        )
    
    @staticmethod
    def get_fair_probabilities(
        odds_values: List[Decimal],
        format: OddsFormat = OddsFormat.DECIMAL
    ) -> List[FairProbability]:
        """Get fair probabilities from a set of odds."""
        implied = [convert_odds_to_probability(o, format) for o in odds_values]
        return calculate_fair_probabilities(implied)
    
    @staticmethod
    def get_overround(
        odds_values: List[Decimal],
        format: OddsFormat = OddsFormat.DECIMAL
    ) -> Overround:
        """Calculate overround from a set of odds."""
        implied = [convert_odds_to_probability(o, format) for o in odds_values]
        return calculate_overround(implied)
    
    @staticmethod
    def calculate_ev(
        your_probability: Decimal,
        odds_value: Decimal,
        odds_format: OddsFormat = OddsFormat.DECIMAL
    ) -> ExpectedValue:
        """Calculate expected value given your probability estimate."""
        if odds_format == OddsFormat.DECIMAL:
            decimal_odds = odds_value
        else:
            decimal_odds = OddsEngine.convert(odds_value, odds_format, OddsFormat.DECIMAL)
        
        return calculate_expected_value(your_probability, decimal_odds)
    
    @staticmethod
    def detect_arbitrage(
        odds_values: List[Decimal],
        format: OddsFormat = OddsFormat.DECIMAL
    ) -> ArbitrageMargin:
        """Detect arbitrage opportunity in a set of odds."""
        if format != OddsFormat.DECIMAL:
            decimal_odds = [OddsEngine.convert(o, format, OddsFormat.DECIMAL) for o in odds_values]
        else:
            decimal_odds = odds_values
        
        return calculate_arbitrage_margin(decimal_odds)
    
    @staticmethod
    def calculate_stakes(
        capital: Decimal,
        odds_values: List[Decimal],
        format: OddsFormat = OddsFormat.DECIMAL
    ) -> StakeAllocation:
        """Calculate optimal stake allocation for arbitrage."""
        if format != OddsFormat.DECIMAL:
            decimal_odds = [OddsEngine.convert(o, format, OddsFormat.DECIMAL) for o in odds_values]
        else:
            decimal_odds = odds_values
        
        return calculate_stake_allocation(capital, decimal_odds)
    
    @staticmethod
    def full_analysis(
        odds_values: List[Decimal],
        format: OddsFormat = OddsFormat.DECIMAL,
        your_probabilities: Optional[List[Decimal]] = None,
        capital: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        Perform comprehensive analysis on a set of odds.
        
        Returns dictionary with:
        - implied_probabilities
        - fair_probabilities
        - overround
        - arbitrage_margin
        - expected_values (if your_probabilities provided)
        - stake_allocation (if capital provided)
        """
        # Convert all to decimal if needed
        if format != OddsFormat.DECIMAL:
            decimal_odds = [OddsEngine.convert(o, format, OddsFormat.DECIMAL) for o in odds_values]
        else:
            decimal_odds = odds_values
        
        # Calculate implied probabilities
        implied_probs = [convert_odds_to_probability(o, OddsFormat.DECIMAL) for o in decimal_odds]
        
        # Calculate fair probabilities
        fair_probs = calculate_fair_probabilities(implied_probs)
        
        # Calculate overround
        overround = calculate_overround(implied_probs)
        
        # Detect arbitrage
        arb_margin = calculate_arbitrage_margin(decimal_odds)
        
        result = {
            "odds": [str(o) for o in decimal_odds],
            "implied_probabilities": [f"{float(p)*100:.2f}%" for p in implied_probs],
            "fair_probabilities": [str(fp) for fp in fair_probs],
            "overround": str(overround),
            "arbitrage": {
                "has_arbitrage": arb_margin.has_arbitrage,
                "margin": str(arb_margin)
            }
        }
        
        # Add EV calculations if probabilities provided
        if your_probabilities:
            if len(your_probabilities) != len(decimal_odds):
                raise InvalidOddsError("Number of probabilities must match number of odds")
            
            evs = [calculate_expected_value(p, o) for p, o in zip(your_probabilities, decimal_odds)]
            result["expected_values"] = [str(ev) for ev in evs]
        
        # Add stake allocation if capital provided
        if capital and arb_margin.has_arbitrage:
            stakes = calculate_stake_allocation(capital, decimal_odds)
            result["stake_allocation"] = {
                "stakes": [float(s) for s in stakes.stakes],
                "total_stake": float(stakes.total_stake),
                "gross_payout": float(stakes.gross_payout),
                "profit": float(stakes.profit),
                "roi": float(stakes.roi) * 100
            }
        
        return result
