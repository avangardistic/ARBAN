# Arbitrage Mathematics

## Core Concept

Arbitrage exists when you can purchase all mutually exclusive outcomes of an event for less than the guaranteed settlement value.

## Binary Markets

### Definition

A binary market has two mutually exclusive outcomes:
- YES (event occurs)
- NO (event does not occur)

Exactly one outcome will settle to $1.00, the other to $0.00.

### Detection

Arbitrage exists when:

```
p_yes + p_no < 1.0
```

Where:
- `p_yes` = executable price for YES
- `p_no` = executable price for NO

### Calculations

**Total Cost:**
```
C = p_yes + p_no
```

**Gross Profit (per unit):**
```
profit = 1.0 - C
```

**Gross ROI:**
```
roi = profit / C = (1.0 - C) / C
```

### Example

```
Polymarket YES = $0.43
Kalshi NO       = $0.51

C = 0.43 + 0.51 = 0.94
profit = 1.00 - 0.94 = $0.06
roi = 0.06 / 0.94 = 6.38%
```

For every $0.94 invested, you guarantee $1.00 return.
Profit: $0.06 per $0.94 = 6.38% ROI.

### Stake Calculation

To deploy capital B with equal settlement value:

```
stake_yes = B × p_yes / (p_yes + p_no)
stake_no  = B × p_no / (p_yes + p_no)
```

**Example with B = $1000:**

```
stake_yes = 1000 × 0.43 / 0.94 = $457.45
stake_no  = 1000 × 0.51 / 0.94 = $542.55

Check: 457.45 + 542.55 = $1000 ✓

Return if YES wins:  457.45 / 0.43 = $1063.83
Return if NO wins:   542.55 / 0.51 = $1063.83 ✓

Profit: 1063.83 - 1000 = $63.83
ROI: 63.83 / 1000 = 6.38% ✓
```

## Multi-Outcome Markets

### Definition

Markets with N ≥ 2 mutually exclusive outcomes where exactly one wins.

Examples:
- Match result: Home Win, Draw, Away Win
- Election: Candidate A, Candidate B, Candidate C, ...
- Award: Winner among multiple nominees

### Detection

Arbitrage exists when:

```
Σ(p_i) < 1.0

where p_i is the price for outcome i
```

### Calculations

**Total Cost:**
```
C = Σ(p_i) for all outcomes
```

**Gross Profit:**
```
profit = 1.0 - C
```

**Gross ROI:**
```
roi = profit / C
```

### Example (3-Way)

```
Team A Win:  $0.40
Draw:        $0.30
Team B Win:  $0.25

C = 0.40 + 0.30 + 0.25 = 0.95
profit = 1.00 - 0.95 = $0.05
roi = 0.05 / 0.95 = 5.26%
```

### Stake Calculation (N-Outcomes)

For capital B and prices [p₁, p₂, ..., pₙ]:

```
stake_i = B × p_i / Σ(p_j)
```

**Example with B = $1000:**

```
stake_A    = 1000 × 0.40 / 0.95 = $421.05
stake_Draw = 1000 × 0.30 / 0.95 = $315.79
stake_B    = 1000 × 0.25 / 0.95 = $263.16

Check: 421.05 + 315.79 + 263.16 = $1000 ✓

Return (any outcome wins): 
  A:    421.05 / 0.40 = $1052.63
  Draw: 315.79 / 0.30 = $1052.63
  B:    263.16 / 0.25 = $1052.63 ✓

Profit: 1052.63 - 1000 = $52.63
ROI: 52.63 / 1000 = 5.26% ✓
```

## Fee Modeling

### Fee Types

1. **Maker Fee**: Fee for adding liquidity
2. **Taker Fee**: Fee for removing liquidity
3. **Transaction Fee**: Network/blockchain fees
4. **Settlement Fee**: Fee on winnings
5. **Withdrawal Fee**: Fee to withdraw funds

### Net Calculations

**Total Fees:**
```
fees = Σ(stake_i × fee_rate_i) + network_fees
```

**Net Profit:**
```
net_profit = gross_profit - fees
```

**Net ROI:**
```
net_roi = net_profit / (B + fees)
```

### Example with Fees

```
Gross profit: $60
Capital: $1000
Fee rate: 2% per leg
Network fee: $5

Trading fees: 1000 × 0.02 × 2 = $40
Network fee: $5
Total fees: $45

Net profit: 60 - 45 = $15
Net ROI: 15 / 1005 = 1.49%
```

## Boundary Conditions

### No Arbitrage Cases

1. **Sum equals 1.0:**
   ```
   p_yes + p_no = 1.0 → No arbitrage (fair market)
   ```

2. **Sum greater than 1.0:**
   ```
   p_yes + p_no > 1.0 → No arbitrage (overround)
   ```

3. **Insufficient liquidity:**
   ```
   Available size < Minimum threshold → Not executable
   ```

4. **Uncertain settlement:**
   ```
   Settlement rules differ → Not guaranteed
   ```

## Precision Requirements

### Decimal Usage

All calculations MUST use `Decimal` type:

```python
from decimal import Decimal

# Correct
price = Decimal("0.43")

# Incorrect (floating point errors)
price = 0.43  # May be stored as 0.43000000000000005
```

### Tolerance

Comparisons should use appropriate tolerance:

```python
def approximately_equal(a: Decimal, b: Decimal, tol: Decimal = Decimal("0.0001")):
    return abs(a - b) < tol
```

## Classification Levels

| Level | Description | Requirements |
|-------|-------------|--------------|
| THEORETICAL | Indicative prices only | Mid prices, no execution guarantee |
| POTENTIAL | Executable but uncertain | Executable prices, matching uncertain |
| EXECUTABLE | Ready to execute | Confirmed match, sufficient liquidity |
| GUARANTEED | Mathematically certain | All above + verified settlement + known fees |

## Risk Considerations

### Execution Risk

- Prices may change between detection and execution
- Liquidity may disappear
- One leg may fill while other doesn't

### Settlement Risk

- Different providers may have different resolution rules
- Event cancellations handled differently
- Edge cases (postponement, overtime, etc.)

### Counterparty Risk

- Provider solvency
- Withdrawal restrictions
- Platform outages

## Implementation Notes

### VWAP Calculation

For large orders, calculate volume-weighted average price:

```python
def calculate_vwap(orderbook: List[Tuple[float, float]], target_size: float) -> float:
    """Calculate VWAP for target size."""
    filled = 0
    cost = 0
    
    for price, size in orderbook:
        take = min(size, target_size - filled)
        cost += price * take
        filled += take
        
        if filled >= target_size:
            break
    
    return cost / filled if filled > 0 else float('inf')
```

### Maximum Executable Size

```
max_size = min(liquidity_leg_1, liquidity_leg_2, ...)
```

Always report the maximum capital that can be deployed at the quoted prices.
