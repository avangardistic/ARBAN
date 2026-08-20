"""
Arbitrage detection and calculation engine.

This module implements the core arbitrage mathematics:
- Binary arbitrage detection
- Multi-outcome arbitrage detection
- Stake calculation
- ROI calculation
- Fee modeling
"""

from typing import List, Tuple, Optional
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ArbitrageLeg:
    """One leg of an arbitrage opportunity."""

    provider: str
    market_id: str
    outcome: str
    side: str  # "buy" or "sell"
    price: Decimal
    size: Decimal
    cost: Decimal


@dataclass
class ArbitrageOpportunity:
    """Complete arbitrage opportunity."""

    id: str
    event_name: str
    type: str  # "binary" or "multi_outcome"
    classification: str  # "THEORETICAL", "POTENTIAL", "EXECUTABLE", "GUARANTEED"
    legs: List[ArbitrageLeg]
    total_cost: Decimal
    gross_profit: Decimal
    gross_roi: Decimal
    net_profit: Optional[Decimal] = None
    net_roi: Optional[Decimal] = None
    fees: Optional[Decimal] = None
    liquidity: Decimal = Decimal("0")
    confidence: float = 0.0
    detected_at: datetime = None

    def __post_init__(self):
        if self.detected_at is None:
            self.detected_at = datetime.utcnow()


def calculate_binary_arbitrage(
    yes_price: Decimal,
    no_price: Decimal,
    yes_provider: str = "",
    no_provider: str = "",
    yes_market_id: str = "",
    no_market_id: str = "",
) -> Tuple[bool, Decimal, Decimal, Decimal]:
    """
    Calculate binary arbitrage metrics.

    Args:
        yes_price: Price for YES outcome
        no_price: Price for NO outcome
        yes_provider: Provider for YES leg
        no_provider: Provider for NO leg
        yes_market_id: Market ID for YES leg
        no_market_id: Market ID for NO leg

    Returns:
        Tuple of (is_arbitrage, total_cost, gross_profit, gross_roi)

    Example:
        >>> yes = Decimal("0.43")
        >>> no = Decimal("0.51")
        >>> is_arb, cost, profit, roi = calculate_binary_arbitrage(yes, no)
        >>> is_arb
        True
        >>> cost
        Decimal('0.94')
        >>> profit
        Decimal('0.06')
        >>> float(roi)  # doctest: +ELLIPSIS
        0.0638...
    """
    total_cost = yes_price + no_price
    is_arbitrage = total_cost < Decimal("1")

    if is_arbitrage:
        gross_profit = Decimal("1") - total_cost
        gross_roi = gross_profit / total_cost
    else:
        gross_profit = Decimal("0")
        gross_roi = Decimal("0")

    return is_arbitrage, total_cost, gross_profit, gross_roi


def calculate_multi_outcome_arbitrage(
    prices: List[Decimal],
) -> Tuple[bool, Decimal, Decimal, Decimal]:
    """
    Calculate multi-outcome arbitrage metrics.

    Args:
        prices: List of prices for mutually exclusive outcomes

    Returns:
        Tuple of (is_arbitrage, total_cost, gross_profit, gross_roi)

    Example:
        >>> prices = [Decimal("0.40"), Decimal("0.30"), Decimal("0.25")]
        >>> is_arb, cost, profit, roi = calculate_multi_outcome_arbitrage(prices)
        >>> is_arb
        True
        >>> cost
        Decimal('0.95')
        >>> profit
        Decimal('0.05')
        >>> float(roi)  # doctest: +ELLIPSIS
        0.0526...
    """
    total_cost = sum(prices)
    is_arbitrage = total_cost < Decimal("1")

    if is_arbitrage:
        gross_profit = Decimal("1") - total_cost
        gross_roi = gross_profit / total_cost
    else:
        gross_profit = Decimal("0")
        gross_roi = Decimal("0")

    return is_arbitrage, total_cost, gross_profit, gross_roi


def calculate_stakes(
    capital: Decimal,
    prices: List[Decimal],
) -> List[Decimal]:
    """
    Calculate optimal stakes for each outcome to guarantee equal return.

    For binary case with prices p1, p2:
        stake1 = B * p1 / (p1 + p2)
        stake2 = B * p2 / (p1 + p2)

    Args:
        capital: Total capital to deploy
        prices: Prices for each outcome

    Returns:
        List of stake amounts for each outcome

    Example:
        >>> capital = Decimal("1000")
        >>> prices = [Decimal("0.43"), Decimal("0.51")]
        >>> stakes = calculate_stakes(capital, prices)
        >>> len(stakes)
        2
        >>> float(sum(stakes))  # Should equal capital
        1000.0
    """
    total_price = sum(prices)

    if total_price == 0:
        return [Decimal("0")] * len(prices)

    stakes = []
    for i, price in enumerate(prices):
        # For the last item, use remainder to ensure sum equals capital exactly
        if i == len(prices) - 1:
            stake = capital - sum(stakes)
        else:
            stake = capital * price / total_price
            stake = stake.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        stakes.append(stake)

    return stakes


def calculate_fees(
    capital: Decimal,
    fee_rates: List[Decimal],
    network_fee: Decimal = Decimal("0"),
) -> Decimal:
    """
    Calculate total fees for an arbitrage trade.

    Args:
        capital: Total capital
        fee_rates: Fee rate for each leg
        network_fee: Fixed network/transaction fee

    Returns:
        Total fees
    """
    trading_fees = sum(capital * rate for rate in fee_rates)
    return trading_fees + network_fee


def calculate_net_metrics(
    gross_profit: Decimal,
    capital: Decimal,
    total_fees: Decimal,
) -> Tuple[Decimal, Decimal]:
    """
    Calculate net profit and ROI after fees.

    Args:
        gross_profit: Gross profit before fees
        capital: Capital deployed
        total_fees: Total fees

    Returns:
        Tuple of (net_profit, net_roi)
    """
    net_profit = gross_profit - total_fees
    net_roi = (
        net_profit / (capital + total_fees)
        if (capital + total_fees) > 0
        else Decimal("0")
    )

    return net_profit, net_roi


def classify_opportunity(
    is_arbitrage: bool,
    settlement_verified: bool,
    liquidity: Decimal,
    min_liquidity: Decimal = Decimal("100"),
    fees_known: bool = True,
    executable_prices: bool = True,
) -> str:
    """
    Classify arbitrage opportunity confidence level.

    Levels:
        - THEORETICAL: Based on indicative/mid prices
        - POTENTIAL: Executable prices but uncertain matching
        - EXECUTABLE: Matching confirmed, sufficient liquidity
        - GUARANTEED: All conditions met including settlement verification

    Args:
        is_arbitrage: Whether math shows arbitrage
        settlement_verified: Whether settlement rules match
        liquidity: Available liquidity
        min_liquidity: Minimum required liquidity
        fees_known: Whether all fees are known
        executable_prices: Whether prices are executable (not indicative)

    Returns:
        Classification string
    """
    if not is_arbitrage:
        return "NO_ARBITRAGE"

    if not executable_prices:
        return "THEORETICAL"

    if liquidity < min_liquidity:
        return "POTENTIAL"

    if not settlement_verified:
        return "EXECUTABLE"

    if fees_known and settlement_verified:
        return "GUARANTEED"

    return "EXECUTABLE"


def detect_binary_opportunities(
    markets: List[dict],
    min_roi: Decimal = Decimal("0"),
) -> List[ArbitrageOpportunity]:
    """
    Detect binary arbitrage opportunities across markets.

    Args:
        markets: List of market dictionaries with outcomes
        min_roi: Minimum ROI threshold

    Returns:
        List of arbitrage opportunities
    """
    opportunities = []

    # Group markets by event
    # This is simplified - real implementation would use proper matching
    for i, market1 in enumerate(markets):
        for market2 in markets[i + 1 :]:
            if market1.get("event_id") != market2.get("event_id"):
                continue

            # Look for YES/NO split across providers
            outcomes1 = {o["name"].lower(): o for o in market1.get("outcomes", [])}
            outcomes2 = {o["name"].lower(): o for o in market2.get("outcomes", [])}

            # Check if we can form YES + NO < 1
            yes_price = None
            no_price = None

            if "yes" in outcomes1 and "no" in outcomes2:
                yes_price = Decimal(str(outcomes1["yes"]["price"]))
                no_price = Decimal(str(outcomes2["no"]["price"]))
            elif "yes" in outcomes2 and "no" in outcomes1:
                yes_price = Decimal(str(outcomes2["yes"]["price"]))
                no_price = Decimal(str(outcomes1["no"]["price"]))

            if yes_price and no_price:
                is_arb, cost, profit, roi = calculate_binary_arbitrage(
                    yes_price, no_price
                )

                if is_arb and roi >= min_roi:
                    opportunities.append(
                        ArbitrageOpportunity(
                            id=f"arb_{market1['provider']}_{market2['provider']}_{market1['event_id']}",
                            event_name=market1.get("title", "Unknown Event"),
                            type="binary",
                            classification="EXECUTABLE",
                            legs=[
                                ArbitrageLeg(
                                    provider=market1["provider"],
                                    market_id=market1["market_id"],
                                    outcome="YES",
                                    side="buy",
                                    price=yes_price,
                                    size=Decimal("0"),
                                    cost=yes_price,
                                ),
                                ArbitrageLeg(
                                    provider=market2["provider"],
                                    market_id=market2["market_id"],
                                    outcome="NO",
                                    side="buy",
                                    price=no_price,
                                    size=Decimal("0"),
                                    cost=no_price,
                                ),
                            ],
                            total_cost=cost,
                            gross_profit=profit,
                            gross_roi=roi,
                            confidence=0.8,
                        )
                    )

    return opportunities
