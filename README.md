# ARBAN

**Cross-Market Prediction Arbitrage Scanner**

ARBAN is an open-source system for discovering and analyzing arbitrage opportunities across prediction markets.

```
Collect → Normalize → Match → Detect → Calculate
```

## What is ARBAN?

ARBAN (Arbitrage Bot for Analysis) is a **read-only** prediction market intelligence engine that:

- Collects live prices from multiple prediction markets
- Normalizes market data into a common format
- Matches equivalent events across platforms
- Detects mathematically valid arbitrage opportunities
- Calculates required stakes and guaranteed returns

**Important:** ARBAN MVP does NOT execute trades, place bets, or handle user funds. It is purely an analysis tool.

## Why ARBAN?

Prediction markets often show price discrepancies for the same real-world event. ARBAN helps identify these opportunities systematically with mathematical rigor.

## Features

- ✅ Multi-provider support (Polymarket, Kalshi, Limitless, Crypto.com)
- ✅ Event and outcome normalization
- ✅ Settlement equivalence verification
- ✅ Binary and multi-outcome arbitrage detection
- ✅ Liquidity-aware calculations
- ✅ Slippage modeling via order book depth
- ✅ Fee modeling (maker, taker, network fees)
- ✅ Real-time REST API
- ✅ Web dashboard
- ✅ CLI interface
- ✅ Automated testing
- ✅ Docker support

## Supported Prediction Markets

| Provider | Status | Type |
|----------|--------|------|
| Polymarket | ✅ Implemented | Crypto prediction market |
| Kalshi | ✅ Implemented | Regulated US prediction market |
| Limitless | 🔄 Mock available | Crypto derivatives |
| Crypto.com | 🔄 Mock available | Exchange prediction markets |

## Architecture

```mermaid
graph TD
    A[Providers] --> B[Data Fetcher]
    B --> C[Normalization Layer]
    C --> D[Event Matcher]
    D --> E[Settlement Verifier]
    E --> F[Arbitrage Engine]
    F --> G[Opportunity Store]
    G --> H[REST API]
    G --> I[Web Dashboard]
    G --> J[CLI]
    
    K[PostgreSQL] <--> G
    L[Redis] <--> G
```

### Components

1. **Providers**: Abstract interface for fetching market data
2. **Normalization**: Convert provider-specific formats to canonical models
3. **Matcher**: Identify equivalent events across platforms
4. **Settlement Verifier**: Ensure contracts have equivalent resolution rules
5. **Arbitrage Engine**: Calculate profitable opportunities
6. **Storage**: PostgreSQL for persistence, Redis for caching
7. **API**: FastAPI REST endpoints
8. **Dashboard**: Next.js web interface

## Arbitrage Mathematics

### Binary Arbitrage

For a binary market with YES/NO outcomes:

```
If: YES_price + NO_price < 1.0
Then: Arbitrage exists

Cost = YES_price + NO_price
Profit = 1.0 - Cost
ROI = Profit / Cost
```

**Example:**

```
Polymarket YES = $0.43
Kalshi NO       = $0.51

Total cost: 0.43 + 0.51 = 0.94
Settlement value: $1.00
Profit: 1.00 - 0.94 = $0.06
ROI: 0.06 / 0.94 = 6.38%
```

### Multi-Outcome Arbitrage

For N mutually exclusive outcomes:

```
If: Σ(price_i) < 1.0
Then: Arbitrage exists

Sum = price_1 + price_2 + ... + price_N
Profit = 1.0 - Sum
ROI = Profit / Sum
```

**Example:**

```
Team A win:  0.40
Draw:        0.30
Team B win:  0.25

Sum:   0.40 + 0.30 + 0.25 = 0.95
Profit: 1.00 - 0.95 = 0.05
ROI:    0.05 / 0.95 = 5.26%
```

### Stake Calculation

Given total capital B and two outcomes with prices p₁, p₂:

```
stake_1 = B × p₁ / (p₁ + p₂)
stake_2 = B × p₂ / (p₁ + p₂)

Guaranteed return = stake_1 / p₁ = stake_2 / p₂
```

### Fees

Net profit accounts for:

- Maker/taker fees per provider
- Transaction/network fees
- Settlement fees

```
Net Profit = Gross Profit - Total Fees
Net ROI = Net Profit / (Capital + Fees)
```

## Installation

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ (for local development)
- Node.js 18+ (for frontend development)

### Quick Start with Docker

```bash
git clone <repository-url>
cd arban
docker compose up --build
```

Access:
- Backend API: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- Frontend Dashboard: http://localhost:3000

### Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Configuration

Copy `.env.example` to `.env` and configure:

```env
APP_ENV=development

DATABASE_URL=postgresql+asyncpg://arban:arban@postgres:5432/arban
REDIS_URL=redis://redis:6379/0

SCAN_INTERVAL_SECONDS=5
MAX_QUOTE_AGE_SECONDS=5

MIN_ARBITRAGE_ROI=0.5
MIN_NET_ROI=0.25

POLYMARKET_ENABLED=true
KALSHI_ENABLED=true
LIMITLESS_ENABLED=true
CRYPTO_COM_ENABLED=true

# Fee rates (decimal form, e.g., 0.02 = 2%)
POLYMARKET_FEE_RATE=0
KALSHI_FEE_RATE=0
LIMITLESS_FEE_RATE=0
CRYPTO_COM_FEE_RATE=0
NETWORK_FEE_ESTIMATE=0
```

## CLI

```bash
# Scan for opportunities
python -m arban scan

# List markets
python -m arban markets

# Show opportunities
python -m arban opportunities --min-roi 1.0

# Check provider health
python -m arban health
```

## API Endpoints

### Health

```
GET /health
GET /health/providers
```

### Markets

```
GET /api/v1/markets
GET /api/v1/markets/{market_id}
```

### Events

```
GET /api/v1/events
GET /api/v1/events/{event_id}
```

### Opportunities

```
GET /api/v1/opportunities
GET /api/v1/opportunities/{opportunity_id}
```

Filters: `provider`, `sport`, `category`, `minimum_roi`, `classification`, `status`

### Arbitrage

```
GET /api/v1/arbitrage/binary
GET /api/v1/arbitrage/multi-outcome
```

### Stats

```
GET /api/v1/stats
```

## Dashboard

The web dashboard provides:

- **Summary Cards**: Active opportunities, best ROI, total markets, healthy providers
- **Opportunities Table**: Filterable list with Event, Sport, Type, ROI, Liquidity, Status
- **Detail View**: Full breakdown of each opportunity including legs, stakes, fees, settlement rules
- **Provider Health**: Real-time status of all data providers
- **Settings**: Configure thresholds and filters

## Demo Mode

Seed the database with deterministic demo data:

```bash
python scripts/seed_demo_data.py
```

Demo includes:

1. **Binary arbitrage**: YES=0.43, NO=0.51 → ROI=6.38%
2. **No arbitrage**: YES=0.52, NO=0.51 → No opportunity
3. **Multi-outcome**: A=0.40, Draw=0.30, B=0.25 → ROI=5.26%

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend/app

# Unit tests only
pytest backend/app/tests/unit

# Integration tests
pytest backend/app/tests/integration

# Type checking
mypy backend/app

# Linting
ruff check .
black --check .
```

## Project Structure

```
arban/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── pyproject.toml
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/           # REST routes
│   │   ├── models/        # Pydantic/SQLAlchemy models
│   │   ├── providers/     # Market data providers
│   │   ├── matching/      # Event/outcome matching
│   │   ├── arbitrage/     # Detection & calculation
│   │   ├── services/      # Business logic
│   │   ├── db/            # Database layer
│   │   └── tests/         # Test suites
│   └── requirements.txt
│
├── frontend/
│   ├── app/               # Next.js pages
│   ├── components/        # React components
│   ├── lib/               # Utilities
│   ├── types/             # TypeScript types
│   └── package.json
│
├── scripts/
│   ├── seed_demo_data.py
│   └── run_scanner.py
│
└── docs/
    ├── architecture.md
    ├── arbitrage-math.md
    ├── providers.md
    └── matching.md
```

## Roadmap

### Phase 1 (MVP) ✅

- Core data collection
- Normalization & matching
- Binary & multi-outcome arbitrage
- Basic API & dashboard
- Demo mode

### Phase 2 (Enhanced Analysis)

- Historical backtesting
- Opportunity trend tracking
- Advanced filtering
- WebSocket real-time updates
- Mobile-responsive dashboard

### Phase 3 (Advanced Features)

- Machine learning for event matching
- Cross-chain settlement analysis
- Risk metrics (Kelly criterion, etc.)
- Alerting system (email, Discord, Telegram)
- Portfolio simulation

## Limitations

- **Read-only**: No trade execution
- **Latency**: Prices may change between detection and execution
- **Liquidity**: Reported opportunities may have insufficient size
- **Settlement risk**: Contract terms may differ subtly
- **Geographic restrictions**: Some providers may be unavailable in certain regions

## Security

ARBAN follows security best practices:

- No secrets committed to Git
- Input validation on all API endpoints
- Rate limiting to prevent abuse
- CORS configuration for safe cross-origin requests
- Dependency pinning for reproducible builds
- Regular security audits via CI

**Important**: ARBAN does not handle private keys, wallet credentials, or user funds.

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Run linters: `ruff check . && black --check .`
6. Submit a pull request

## License

MIT License - See [LICENSE](LICENSE) for details.

---

**Disclaimer**: ARBAN is for informational and educational purposes only. It does not provide financial advice. Users are responsible for complying with applicable laws and regulations in their jurisdiction.
