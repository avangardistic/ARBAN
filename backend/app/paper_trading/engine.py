"""
ARBAN Paper Trading Engine

Simulated execution engine for testing strategies without real capital.
Supports:
- Paper orders (market, limit)
- Simulated fills with slippage
- Partial fills
- Fee calculation
- PnL tracking
- Portfolio management
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid


class OrderSide(Enum):
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class PaperOrder:
    """Represents a paper trading order."""
    order_id: str
    market_id: str
    provider: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal]  # None for market orders
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: Decimal = Decimal("0")
    average_fill_price: Decimal = Decimal("0")
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    fees: Decimal = Decimal("0")
    slippage: Decimal = Decimal("0")
    
    def __str__(self) -> str:
        return f"{self.side.value.upper()} {self.quantity} @ {self.price or 'MARKET'} [{self.status.value}]"


@dataclass
class PaperFill:
    """Represents a fill from a paper order."""
    fill_id: str
    order_id: str
    quantity: Decimal
    price: Decimal
    fee: Decimal
    slippage: Decimal
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PaperPosition:
    """Represents a position in a specific market."""
    market_id: str
    provider: str
    quantity: Decimal
    average_entry_price: Decimal
    current_price: Decimal
    unrealized_pnl: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    
    @property
    def market_value(self) -> Decimal:
        return self.quantity * self.current_price
    
    @property
    def cost_basis(self) -> Decimal:
        return self.quantity * self.average_entry_price
    
    def update_pnl(self, current_price: Decimal):
        """Update unrealized PnL based on current price."""
        self.current_price = current_price
        if self.quantity > 0:
            self.unrealized_pnl = (current_price - self.average_entry_price) * self.quantity


@dataclass
class PaperPortfolio:
    """Represents the overall paper trading portfolio."""
    portfolio_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    initial_capital: Decimal = Decimal("10000")
    available_capital: Decimal = Decimal("10000")
    invested_capital: Decimal = Decimal("0")
    total_fees: Decimal = Decimal("0")
    realized_pnl: Decimal = Decimal("0")
    unrealized_pnl: Decimal = Decimal("0")
    positions: Dict[str, PaperPosition] = field(default_factory=dict)
    orders: List[PaperOrder] = field(default_factory=list)
    fills: List[PaperFill] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def total_value(self) -> Decimal:
        """Total portfolio value including cash and positions."""
        return self.available_capital + sum(p.market_value for p in self.positions.values())
    
    @property
    def total_pnl(self) -> Decimal:
        """Total PnL (realized + unrealized)."""
        return self.realized_pnl + self.unrealized_pnl
    
    @property
    def total_return_pct(self) -> float:
        """Total return as percentage."""
        if self.initial_capital == 0:
            return 0.0
        return float((self.total_pnl / self.initial_capital) * 100)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert portfolio to dictionary for API response."""
        return {
            "portfolio_id": self.portfolio_id,
            "initial_capital": float(self.initial_capital),
            "available_capital": float(self.available_capital),
            "invested_capital": float(self.invested_capital),
            "total_value": float(self.total_value),
            "total_fees": float(self.total_fees),
            "realized_pnl": float(self.realized_pnl),
            "unrealized_pnl": float(self.unrealized_pnl),
            "total_pnl": float(self.total_pnl),
            "total_return_pct": self.total_return_pct,
            "num_positions": len(self.positions),
            "num_orders": len(self.orders),
            "created_at": self.created_at.isoformat()
        }


class PaperExecutionEngine:
    """
    Paper trading execution engine.
    
    Simulates order execution with realistic slippage and fees.
    """
    
    def __init__(
        self,
        initial_capital: Decimal = Decimal("10000"),
        default_fee_rate: Decimal = Decimal("0.001"),  # 0.1%
        max_slippage_rate: Decimal = Decimal("0.005"),  # 0.5%
    ):
        self.portfolio = PaperPortfolio(initial_capital=initial_capital)
        self.default_fee_rate = default_fee_rate
        self.max_slippage_rate = max_slippage_rate
        self.provider_fee_rates: Dict[str, Decimal] = {}
        self.provider_slippage_rates: Dict[str, Decimal] = {}
    
    def set_provider_fees(self, provider: str, fee_rate: Decimal):
        """Set fee rate for a specific provider."""
        self.provider_fee_rates[provider] = fee_rate
    
    def set_provider_slippage(self, provider: str, slippage_rate: Decimal):
        """Set slippage rate for a specific provider."""
        self.provider_slippage_rates[provider] = slippage_rate
    
    def _get_fee_rate(self, provider: str) -> Decimal:
        """Get fee rate for provider or default."""
        return self.provider_fee_rates.get(provider, self.default_fee_rate)
    
    def _get_slippage_rate(self, provider: str) -> Decimal:
        """Get slippage rate for provider or default."""
        return self.provider_slippage_rates.get(provider, self.max_slippage_rate)
    
    def submit_order(
        self,
        market_id: str,
        provider: str,
        side: OrderSide,
        quantity: Decimal,
        order_type: OrderType = OrderType.MARKET,
        limit_price: Optional[Decimal] = None,
    ) -> PaperOrder:
        """Submit a new paper order."""
        # Validate order
        if side == OrderSide.BUY and order_type == OrderType.MARKET:
            # Check if we have enough capital
            estimated_cost = quantity * Decimal("1")  # Simplified - would need current price
            if estimated_cost > self.portfolio.available_capital:
                order = PaperOrder(
                    order_id=str(uuid.uuid4()),
                    market_id=market_id,
                    provider=provider,
                    side=side,
                    order_type=order_type,
                    quantity=quantity,
                    price=limit_price,
                    status=OrderStatus.REJECTED,
                )
                return order
        
        # Create order
        order = PaperOrder(
            order_id=str(uuid.uuid4()),
            market_id=market_id,
            provider=provider,
            side=side,
            order_type=order_type,
            quantity=quantity,
            price=limit_price,
        )
        
        self.portfolio.orders.append(order)
        return order
    
    def simulate_fill(
        self,
        order: PaperOrder,
        market_price: Decimal,
        fill_quantity: Optional[Decimal] = None,
    ) -> Optional[PaperFill]:
        """Simulate filling an order at current market price."""
        if order.status == OrderStatus.CANCELLED:
            return None
        
        # Determine fill quantity
        if fill_quantity is None:
            fill_quantity = order.quantity - order.filled_quantity
        else:
            fill_quantity = min(fill_quantity, order.quantity - order.filled_quantity)
        
        if fill_quantity <= 0:
            return None
        
        # Calculate slippage (adverse price movement)
        slippage_rate = self._get_slippage_rate(order.provider)
        if order.side == OrderSide.BUY:
            fill_price = market_price * (Decimal("1") + slippage_rate)
        else:
            fill_price = market_price * (Decimal("1") - slippage_rate)
        
        slippage = abs(fill_price - market_price) * fill_quantity
        
        # Calculate fees
        fee_rate = self._get_fee_rate(order.provider)
        fee = fill_price * fill_quantity * fee_rate
        
        # Update order
        total_filled = order.filled_quantity + fill_quantity
        total_cost = (order.average_fill_price * order.filled_quantity) + (fill_price * fill_quantity)
        order.average_fill_price = (total_cost / total_filled).quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
        order.filled_quantity = total_filled
        order.fees += fee
        order.slippage += slippage
        order.updated_at = datetime.utcnow()
        
        # Update status
        if order.filled_quantity >= order.quantity:
            order.status = OrderStatus.FILLED
        else:
            order.status = OrderStatus.PARTIALLY_FILLED
        
        # Create fill record
        fill = PaperFill(
            fill_id=str(uuid.uuid4()),
            order_id=order.order_id,
            quantity=fill_quantity,
            price=fill_price,
            fee=fee,
            slippage=slippage,
        )
        
        self.portfolio.fills.append(fill)
        
        # Update portfolio
        self.portfolio.total_fees += fee
        if order.side == OrderSide.BUY:
            self.portfolio.invested_capital += fill_price * fill_quantity
            self.portfolio.available_capital -= (fill_price * fill_quantity + fee)
        else:
            self.portfolio.available_capital += (fill_price * fill_quantity - fee)
            self.portfolio.invested_capital -= fill_price * fill_quantity
        
        return fill
    
    def update_position(
        self,
        order: PaperOrder,
        current_price: Decimal,
    ):
        """Update or create position based on filled order."""
        if order.status not in [OrderStatus.FILLED, OrderStatus.PARTIALLY_FILLED]:
            return
        
        position_key = f"{order.market_id}:{order.provider}"
        
        if position_key in self.portfolio.positions:
            position = self.portfolio.positions[position_key]
            
            if order.side == OrderSide.BUY:
                # Add to position
                total_cost = (position.average_entry_price * position.quantity) + \
                            (order.average_fill_price * order.filled_quantity)
                total_qty = position.quantity + order.filled_quantity
                position.average_entry_price = total_cost / total_qty
                position.quantity = total_qty
            else:
                # Reduce position
                position.quantity -= order.filled_quantity
                
                if position.quantity <= 0:
                    # Position closed - calculate realized PnL
                    pnl = (order.average_fill_price - position.average_entry_price) * abs(position.quantity)
                    position.realized_pnl += pnl
                    self.portfolio.realized_pnl += pnl
                    del self.portfolio.positions[position_key]
                    return
        else:
            # New position
            if order.side == OrderSide.BUY:
                self.portfolio.positions[position_key] = PaperPosition(
                    market_id=order.market_id,
                    provider=order.provider,
                    quantity=order.filled_quantity,
                    average_entry_price=order.average_fill_price,
                    current_price=current_price,
                )
        
        # Update PnL
        if position_key in self.portfolio.positions:
            self.portfolio.positions[position_key].update_pnl(current_price)
        
        # Recalculate total unrealized PnL
        self.portfolio.unrealized_pnl = sum(
            p.unrealized_pnl for p in self.portfolio.positions.values()
        )
    
    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary."""
        return self.portfolio.to_dict()
    
    def get_positions(self) -> List[Dict[str, Any]]:
        """Get all current positions."""
        return [
            {
                "market_id": p.market_id,
                "provider": p.provider,
                "quantity": float(p.quantity),
                "average_entry_price": float(p.average_entry_price),
                "current_price": float(p.current_price),
                "market_value": float(p.market_value),
                "unrealized_pnl": float(p.unrealized_pnl),
                "realized_pnl": float(p.realized_pnl),
            }
            for p in self.portfolio.positions.values()
        ]
    
    def get_orders(self, status: Optional[OrderStatus] = None) -> List[Dict[str, Any]]:
        """Get orders, optionally filtered by status."""
        orders = self.portfolio.orders
        if status:
            orders = [o for o in orders if o.status == status]
        
        return [
            {
                "order_id": o.order_id,
                "market_id": o.market_id,
                "provider": o.provider,
                "side": o.side.value,
                "order_type": o.order_type.value,
                "quantity": float(o.quantity),
                "price": float(o.price) if o.price else None,
                "status": o.status.value,
                "filled_quantity": float(o.filled_quantity),
                "average_fill_price": float(o.average_fill_price),
                "fees": float(o.fees),
                "slippage": float(o.slippage),
                "created_at": o.created_at.isoformat(),
                "updated_at": o.updated_at.isoformat(),
            }
            for o in orders
        ]
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel a pending order."""
        for order in self.portfolio.orders:
            if order.order_id == order_id:
                if order.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]:
                    order.status = OrderStatus.CANCELLED
                    order.updated_at = datetime.utcnow()
                    
                    # Release any reserved capital for unfilled portion
                    unfilled = order.quantity - order.filled_quantity
                    if order.side == OrderSide.BUY and order.price:
                        self.portfolio.available_capital += unfilled * order.price
                    
                    return True
        return False
