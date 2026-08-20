from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime


class Market:
    """Normalized market representation."""

    def __init__(
        self,
        provider: str,
        market_id: str,
        event_id: str,
        title: str,
        description: Optional[str] = None,
        category: Optional[str] = None,
        status: str = "open",
        close_time: Optional[datetime] = None,
        resolution_time: Optional[datetime] = None,
        outcomes: Optional[List["Outcome"]] = None,
    ):
        self.provider = provider
        self.market_id = market_id
        self.event_id = event_id
        self.title = title
        self.description = description
        self.category = category
        self.status = status
        self.close_time = close_time
        self.resolution_time = resolution_time
        self.outcomes = outcomes or []


class Outcome:
    """Normalized outcome representation."""

    def __init__(
        self,
        outcome_id: str,
        name: str,
        normalized_name: Optional[str] = None,
        price: float = 0.0,
        available_size: float = 0.0,
        is_winner: bool = False,
    ):
        self.outcome_id = outcome_id
        self.name = name
        self.normalized_name = normalized_name or name.lower().replace(" ", "_")
        self.price = price
        self.available_size = available_size
        self.is_winner = is_winner


class Quote:
    """Normalized quote representation."""

    def __init__(
        self,
        provider: str,
        market_id: str,
        outcome_id: str,
        outcome_name: str,
        side: str,  # "buy" or "sell"
        price: float,
        available_size: float = 0.0,
        indicative: bool = False,
        timestamp: Optional[datetime] = None,
    ):
        self.provider = provider
        self.market_id = market_id
        self.outcome_id = outcome_id
        self.outcome_name = outcome_name
        self.side = side
        self.price = price
        self.available_size = available_size
        self.indicative = indicative
        self.timestamp = timestamp or datetime.utcnow()


class OrderBook:
    """Order book representation."""

    def __init__(
        self,
        provider: str,
        market_id: str,
        bids: List[tuple],  # [(price, size), ...]
        asks: List[tuple],  # [(price, size), ...]
        timestamp: Optional[datetime] = None,
    ):
        self.provider = provider
        self.market_id = market_id
        self.bids = bids
        self.asks = asks
        self.timestamp = timestamp or datetime.utcnow()

    @property
    def best_bid(self) -> Optional[float]:
        """Get best bid price."""
        if not self.bids:
            return None
        return max(price for price, size in self.bids)

    @property
    def best_ask(self) -> Optional[float]:
        """Get best ask price."""
        if not self.asks:
            return None
        return min(price for price, size in self.asks)


class ProviderHealth:
    """Provider health status."""

    def __init__(
        self,
        provider: str,
        status: str,  # "UP", "DEGRADED", "DOWN", "RATE_LIMITED", "AUTH_REQUIRED", "UNKNOWN"
        latency_ms: Optional[float] = None,
        last_check: Optional[datetime] = None,
        error_message: Optional[str] = None,
    ):
        self.provider = provider
        self.status = status
        self.latency_ms = latency_ms
        self.last_check = last_check or datetime.utcnow()
        self.error_message = error_message


class PredictionMarketProvider(ABC):
    """Abstract base class for prediction market providers."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled

    @abstractmethod
    async def get_markets(self) -> List[Market]:
        """Fetch all active markets from the provider."""
        pass

    @abstractmethod
    async def get_market(self, market_id: str) -> Optional[Market]:
        """Fetch a specific market by ID."""
        pass

    @abstractmethod
    async def get_orderbook(self, market_id: str) -> Optional[OrderBook]:
        """Fetch order book for a specific market."""
        pass

    @abstractmethod
    async def health_check(self) -> ProviderHealth:
        """Check provider health status."""
        pass
