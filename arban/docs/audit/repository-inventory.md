# ARBAN v1.0 - Repository Inventory

## Audit Metadata
- Branch: `audit/v1.0-production`
- Commit: `a4dba1d698c513f9d4eca0a597a72833e4a3b05f`
- Audit Date: 2025

## File Inventory

### Root Level
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| README.md | Project documentation | PRESENT | LOW - Claims need verification |
| CONTRIBUTING.md | Contribution guidelines | PRESENT | LOW |
| SECURITY.md | Security policy | PRESENT | LOW |
| LICENSE | MIT License | PRESENT | LOW |
| docker-compose.yml | Docker orchestration | PRESENT | MEDIUM - Needs testing |
| .github/workflows/ci.yml | CI/CD pipeline | PRESENT | MEDIUM - Needs verification |
| pytest.ini | Pytest configuration | PRESENT | LOW |

### Backend Structure
| Directory/File | Purpose | Status | Risk |
|----------------|---------|--------|------|
| backend/app/main.py | FastAPI application entry | PRESENT | HIGH - Core component |
| backend/app/config.py | Configuration management | PRESENT | MEDIUM |
| backend/app/logging.py | Logging setup | PRESENT | LOW |
| backend/requirements.txt | Python dependencies | PRESENT | MEDIUM - Had conflict issue |

### API Layer (backend/app/api/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| routes_arbitrage.py | Arbitrage endpoints | PRESENT | HIGH |
| routes_health.py | Health check endpoints | PRESENT | MEDIUM |
| routes_markets.py | Market data endpoints | PRESENT | HIGH |
| routes_odds.py | Odds conversion endpoints | PRESENT | MEDIUM |
| routes_opportunities.py | Opportunity endpoints | PRESENT | HIGH |

### Core Modules

#### Arbitrage (backend/app/arbitrage/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| calculator.py | Arbitrage calculations | PRESENT | CRITICAL - Core math |

#### Odds Engine (backend/app/odds/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| engine.py | Odds conversions, stake calculation | PRESENT | CRITICAL - Core math |

#### Paper Trading (backend/app/paper_trading/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| engine.py | Paper trade execution simulation | PRESENT | HIGH - Execution logic |

#### Providers (backend/app/providers/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| base.py | Base provider interface | PRESENT | HIGH |
| mock_provider.py | Mock/simulated provider | PRESENT | MEDIUM - May be confused with real |

#### Database (backend/app/db/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| database.py | DB connection management | PRESENT | HIGH |
| models.py | SQLAlchemy models | PRESENT | HIGH |

#### Models (backend/app/models/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| __init__.py | Model exports | PRESENT | LOW |

### Tests (backend/app/tests/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| test_calculator.py | Arbitrage calculator tests | PRESENT | Tests exist but limited scope |
| test_odds_engine.py | Odds engine tests | PRESENT | Good coverage of odds logic |

### Documentation (docs/)
| File | Purpose | Status | Risk |
|------|---------|--------|------|
| arbitrage-math.md | Mathematical formulas | PRESENT | Need to verify implementation matches |
| architecture.md | System architecture | PRESENT | Claims need verification |

## Critical Gaps Identified

### Missing Components
1. **No frontend directory** - README claims Next.js dashboard but no frontend/ exists
2. **No scripts/ directory** - README references seed_demo_data.py and run_scanner.py
3. **No .env.example** - Required for configuration
4. **No pyproject.toml** - Referenced in README structure
5. **No integration tests** - Only unit tests present
6. **No E2E tests** - No end-to-end testing infrastructure

### Provider Implementation Gaps
1. **No Polymarket provider** - README claims "Implemented" but only mock_provider.py exists
2. **No Kalshi provider** - README claims "Implemented" but not found
3. **No Limitless provider** - Only mock available
4. **No Crypto.com provider** - Only mock available

### Database Issues
1. **No migrations** - README mentions alembic but no migrations/ directory
2. **No schema creation scripts**

## Risk Summary

| Risk Level | Count | Description |
|------------|-------|-------------|
| CRITICAL | 2 | Core math modules need independent verification |
| HIGH | 6 | Missing provider implementations, missing frontend |
| MEDIUM | 5 | Configuration issues, missing scripts, CI verification needed |
| LOW | 4 | Documentation gaps |

## Immediate Red Flags

1. **README claims vs Reality**: Multiple features claimed as "Implemented" are missing
2. **No live provider integrations**: Only mock provider exists
3. **No frontend**: Dashboard claimed but doesn't exist
4. **Limited test coverage**: Only 94 unit tests for odds/calculator, no integration tests
5. **Dependency conflict**: requirements.txt had broken pytest-asyncio version
