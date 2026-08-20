# ARBAN v1.0 - Baseline Test Report

## Audit Branch
- Branch: `audit/v1.0-production`
- Commit: `a4dba1d698c513f9d4eca0a597a72833e4a3b05f`
- Date: $(date)

## Test Execution

### Initial Issue
The repository had a dependency conflict in `requirements.txt`:
- `pytest==8.0.0` conflicts with `pytest-asyncio==0.23.4` (requires pytest<8)

**Fix Applied:** Changed `pytest-asyncio==0.23.4` to `pytest-asyncio==0.24.0`

### Test Results

**Command:** `PYTHONPATH=/workspace/arban/backend:$PYTHONPATH pytest`

**Result:** 94 tests PASSED, 0 FAILED

Test breakdown:
- `test_calculator.py`: 18 tests (arbitrage calculations)
- `test_odds_engine.py`: 76 tests (odds conversions, arbitrage margin, stake allocation)

### Coverage Note
No coverage report was generated as `--cov` flag was not included in baseline run.

## Initial Assessment
- Tests pass but cover only unit-level functionality
- No integration tests detected
- No E2E tests detected
- Test scope limited to odds engine and calculator modules
