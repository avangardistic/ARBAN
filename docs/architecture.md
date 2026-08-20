# Architecture

## Overview

ARBAN follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │   CLI   │  │   API   │  │Dashboard│ │
│  └─────────┘  └─────────┘  └─────────┘ │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│           Business Logic Layer          │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │   Scanner    │  │Arbitrage Engine │  │
│  └──────────────┘  └─────────────────┘  │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │   Matcher    │  │  Normalization  │  │
│  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│            Data Access Layer            │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │  Providers   │  │   Repository    │  │
│  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│           Infrastructure Layer          │
│  ┌──────────────┐  ┌─────────────────┐  │
│  │  PostgreSQL  │  │     Redis       │  │
│  └──────────────┘  └─────────────────┘  │
└─────────────────────────────────────────┘
```

## Components

### Presentation Layer

- **CLI**: Command-line interface for quick access
- **API**: RESTful FastAPI endpoints
- **Dashboard**: Next.js web application

### Business Logic Layer

- **Scanner**: Orchestrates data collection and opportunity detection
- **Arbitrage Engine**: Mathematical calculations for opportunity detection
- **Matcher**: Event and outcome matching across providers
- **Normalization**: Converts provider-specific formats to canonical models

### Data Access Layer

- **Providers**: Abstract interface for market data providers
- **Repository**: Database access patterns

### Infrastructure Layer

- **PostgreSQL**: Persistent storage
- **Redis**: Caching and real-time data

## Data Flow

1. **Collection**: Providers fetch data from external APIs
2. **Normalization**: Raw data converted to canonical models
3. **Matching**: Events/outcomes matched across providers
4. **Detection**: Arbitrage engine identifies opportunities
5. **Storage**: Results stored in database
6. **Presentation**: Data exposed via API, CLI, Dashboard

## Key Design Decisions

### Read-Only by Design

The MVP is intentionally read-only to:
- Reduce complexity
- Eliminate execution risk
- Focus on core value: opportunity detection
- Avoid regulatory complications

### Provider Abstraction

All providers implement a common interface:
- Consistent data models
- Easy to add new providers
- Isolated failure domains

### Decimal Precision

Financial calculations use `Decimal` type:
- Avoids floating-point errors
- Ensures accurate ROI calculations
- Critical for arbitrage detection

### Async Architecture

- Non-blocking I/O for provider calls
- Efficient resource utilization
- Better scalability

## Error Handling

Each layer has specific error handling:

- **Provider errors**: Retries with exponential backoff
- **Normalization errors**: Log and skip malformed data
- **Matching errors**: Mark as uncertain, don't reject
- **Calculation errors**: Return safe defaults

## Scalability Considerations

### Horizontal Scaling

- Stateless backend services
- Shared database and cache
- Load balancer ready

### Vertical Scaling

- Connection pooling for database
- Redis for hot data caching
- Efficient data structures

## Security Boundaries

```
External APIs → Provider Layer → Internal Models → Business Logic → Storage
                    ↑                                    ↓
              Validation                            Authorization
```

- No direct access from external APIs to business logic
- All inputs validated at boundaries
- Secrets managed via environment variables
