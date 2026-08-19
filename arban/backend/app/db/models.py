from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from ..db.database import Base


class ProviderStatus(enum.Enum):
    UP = "UP"
    DEGRADED = "DEGRADED"
    DOWN = "DOWN"
    RATE_LIMITED = "RATE_LIMITED"
    AUTH_REQUIRED = "AUTH_REQUIRED"
    UNKNOWN = "UNKNOWN"


class OpportunityClassification(enum.Enum):
    THEORETICAL = "THEORETICAL"
    POTENTIAL = "POTENTIAL"
    EXECUTABLE = "EXECUTABLE"
    GUARANTEED = "GUARANTEED"


class MatchStatus(enum.Enum):
    MATCH_CONFIRMED = "MATCH_CONFIRMED"
    MATCH_PROBABLE = "MATCH_PROBABLE"
    MATCH_UNCERTAIN = "MATCH_UNCERTAIN"
    MATCH_REJECTED = "MATCH_REJECTED"


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    enabled = Column(Boolean, default=True)
    status = Column(SQLEnum(ProviderStatus), default=ProviderStatus.UNKNOWN)
    last_check = Column(DateTime)
    fee_rate = Column(Float, default=0.0)
    api_url = Column(String)

    markets = relationship("Market", back_populates="provider")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    canonical_id = Column(String, unique=True)
    title = Column(String, nullable=False)
    sport = Column(String)
    category = Column(String)
    start_time = Column(DateTime)
    participants = Column(Text)  # JSON array of participants
    event_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True)
    provider_id = Column(Integer, ForeignKey("providers.id"))
    market_id = Column(String, nullable=False)
    event_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    category = Column(String)
    status = Column(String, default="open")
    close_time = Column(DateTime)
    resolution_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    provider = relationship("Provider", back_populates="markets")
    outcomes = relationship("Outcome", back_populates="market")


class Outcome(Base):
    __tablename__ = "outcomes"

    id = Column(Integer, primary_key=True)
    market_id = Column(Integer, ForeignKey("markets.id"))
    outcome_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    normalized_name = Column(String)
    price = Column(Float)
    available_size = Column(Float)
    is_winner = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

    market = relationship("Market", back_populates="outcomes")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    market_id = Column(String, nullable=False)
    outcome_id = Column(String, nullable=False)
    outcome_name = Column(String)
    side = Column(String)  # "buy" or "sell"
    price = Column(Float, nullable=False)
    available_size = Column(Float)
    indicative = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


class OrderbookSnapshot(Base):
    __tablename__ = "orderbook_snapshots"

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    market_id = Column(String, nullable=False)
    bids = Column(Text)  # JSON array
    asks = Column(Text)  # JSON array
    timestamp = Column(DateTime, default=datetime.utcnow)


class ArbitrageOpportunity(Base):
    __tablename__ = "arbitrage_opportunities"

    id = Column(Integer, primary_key=True)
    canonical_event_id = Column(String)
    type = Column(String)  # "binary" or "multi_outcome"
    classification = Column(SQLEnum(OpportunityClassification))
    providers = Column(Text)  # JSON array
    capital_required = Column(Float)
    max_capital = Column(Float)
    gross_profit = Column(Float)
    gross_roi = Column(Float)
    net_profit = Column(Float)
    net_roi = Column(Float)
    liquidity = Column(Float)
    confidence = Column(Float)
    settlement_verified = Column(Boolean)
    status = Column(String, default="ACTIVE")
    detected_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime)
    expires_at = Column(DateTime)

    legs = relationship("ArbitrageLeg", back_populates="opportunity")


class ArbitrageLeg(Base):
    __tablename__ = "arbitrage_legs"

    id = Column(Integer, primary_key=True)
    opportunity_id = Column(Integer, ForeignKey("arbitrage_opportunities.id"))
    provider = Column(String, nullable=False)
    market_id = Column(String, nullable=False)
    outcome = Column(String, nullable=False)
    side = Column(String)
    price = Column(Float, nullable=False)
    size = Column(Float)
    cost = Column(Float)

    opportunity = relationship("ArbitrageOpportunity", back_populates="legs")


class ScanRun(Base):
    __tablename__ = "scan_runs"

    id = Column(Integer, primary_key=True)
    scan_id = Column(String, unique=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    markets_received = Column(Integer)
    markets_normalized = Column(Integer)
    events_matched = Column(Integer)
    opportunities_found = Column(Integer)
    provider_latencies = Column(Text)  # JSON object
    provider_errors = Column(Integer)
    status = Column(String, default="RUNNING")
