"""
Mock provider for testing and demo purposes.

This provider returns deterministic test data for development and testing.
"""
from typing import List, Optional
from datetime import datetime, timedelta

from .base import PredictionMarketProvider, Market, Outcome, OrderBook, ProviderHealth


class MockProvider(PredictionMarketProvider):
    """Mock provider returning predefined test markets."""

    def __init__(self):
        super().__init__(name="mock", enabled=True)
        
        # Create demo markets with known arbitrage opportunities
        self._demo_markets = self._create_demo_markets()

    def _create_demo_markets(self) -> List[Market]:
        """Create demo markets for testing."""
        now = datetime.utcnow()
        
        # Market 1: Binary arbitrage opportunity (YES=0.43, NO=0.51)
        market1 = Market(
            provider="mock",
            market_id="mock_binary_1",
            event_id="event_1",
            title="Will Team A win?",
            category="sports",
            status="open",
            close_time=now + timedelta(hours=24),
            outcomes=[
                Outcome(
                    outcome_id="yes",
                    name="Yes",
                    normalized_name="yes",
                    price=0.43,
                    available_size=1000.0,
                ),
                Outcome(
                    outcome_id="no",
                    name="No",
                    normalized_name="no",
                    price=0.51,
                    available_size=1000.0,
                ),
            ],
        )
        
        # Market 2: No arbitrage (YES=0.52, NO=0.51, sum=1.03 > 1)
        market2 = Market(
            provider="mock",
            market_id="mock_binary_2",
            event_id="event_2",
            title="Will Team B win?",
            category="sports",
            status="open",
            close_time=now + timedelta(hours=48),
            outcomes=[
                Outcome(
                    outcome_id="yes",
                    name="Yes",
                    normalized_name="yes",
                    price=0.52,
                    available_size=500.0,
                ),
                Outcome(
                    outcome_id="no",
                    name="No",
                    normalized_name="no",
                    price=0.51,
                    available_size=500.0,
                ),
            ],
        )
        
        # Market 3: Multi-outcome arbitrage (A=0.40, Draw=0.30, B=0.25, sum=0.95)
        market3 = Market(
            provider="mock",
            market_id="mock_multi_1",
            event_id="event_3",
            title="Team C vs Team D - Match Result",
            category="sports",
            status="open",
            close_time=now + timedelta(hours=72),
            outcomes=[
                Outcome(
                    outcome_id="team_c",
                    name="Team C",
                    normalized_name="team_c",
                    price=0.40,
                    available_size=800.0,
                ),
                Outcome(
                    outcome_id="draw",
                    name="Draw",
                    normalized_name="draw",
                    price=0.30,
                    available_size=800.0,
                ),
                Outcome(
                    outcome_id="team_d",
                    name="Team D",
                    normalized_name="team_d",
                    price=0.25,
                    available_size=800.0,
                ),
            ],
        )
        
        return [market1, market2, market3]

    async def get_markets(self) -> List[Market]:
        """Return all demo markets."""
        return self._demo_markets

    async def get_market(self, market_id: str) -> Optional[Market]:
        """Get a specific market by ID."""
        for market in self._demo_markets:
            if market.market_id == market_id:
                return market
        return None

    async def get_orderbook(self, market_id: str) -> Optional[OrderBook]:
        """Get order book for a market."""
        market = await self.get_market(market_id)
        if not market:
            return None
        
        # Create synthetic order book from outcomes
        bids = []
        asks = []
        
        for outcome in market.outcomes:
            # Simulate bid-ask spread
            bid_price = outcome.price * 0.98  # 2% below mid
            ask_price = outcome.price * 1.02  # 2% above mid
            size = outcome.available_size / 2
            
            bids.append((bid_price, size))
            asks.append((ask_price, size))
        
        return OrderBook(
            provider="mock",
            market_id=market_id,
            bids=bids,
            asks=asks,
        )

    async def health_check(self) -> ProviderHealth:
        """Mock provider is always healthy."""
        return ProviderHealth(
            provider="mock",
            status="UP",
            latency_ms=5.0,
        )
