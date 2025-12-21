# Moving Block Bootstrap (MBB) Module

This module implements portfolio optimization and option pricing using Moving Block Bootstrap methodology for Brazilian stocks.

## Features

- **Portfolio Optimization**: Finds optimal portfolio allocation using MBB, Monte Carlo, and Newton-Raphson optimization
- **Option Pricing**: Calculates theoretical option prices using MBB methodology
- **Brazilian Stock Support**: Automatic `.SA` suffix handling for B3 stocks
- **Monte Carlo Asset Selection**: Selects top-performing assets before optimization
- **High Performance**: C library for computationally intensive operations

## Installation

### Requirements

- Python 3.8+
- GCC compiler (MinGW on Windows)
- Required Python packages: numpy, pandas, yfinance, scipy

### Compile C Library

```bash
cd backend/app/utils/mbb
make  # On Linux/macOS
# OR
gcc -shared -o functions.dll functions_optimized.c -lm  # On Windows
```

## Usage

### Portfolio Optimization

```python
from app.utils.mbb import MBBCore, DataGatherer

# Initialize
mbb_core = MBBCore()
data_gatherer = DataGatherer(use_monte_carlo_selection=True, top_n_assets=15)

# Get data
closing_prices = data_gatherer.get_data()
log_returns = closing_prices.pct_change().dropna()
current_prices = data_gatherer.get_current_prices()

# Run MBB and Monte Carlo for each asset
arrival_values = {}
for asset in log_returns.columns:
    S0 = current_prices[asset]
    bootstrap_samples = mbb_core.moving_block_bootstrap(log_returns[asset])
    arrival_values[asset] = mbb_core.monte_carlo_simulation(S0, bootstrap_samples)

# Optimize portfolio
import pandas as pd
arrival_values_df = pd.DataFrame(arrival_values)
optimal_weights = mbb_core.optimize_portfolio_newton_raphson(
    arrival_values_df,
    risk_free_rate=0.1375
)
```

### Option Pricing

```python
from app.utils.mbb import MBBCore, DataGatherer, OptionPricer

# Initialize
mbb_core = MBBCore()
data_gatherer = DataGatherer(use_monte_carlo_selection=False)
option_pricer = OptionPricer(mbb_core, data_gatherer)

# Price options
result = option_pricer.price_options(
    ticker='PETR4',
    expiry_date='2025-12-19',  # Optional
    n_bootstrap=1000,
    iterations=5000,
    risk_free_rate=0.1375
)

# Access results
calls = result['calls']  # List of call option prices
puts = result['puts']    # List of put option prices
statistics = result['statistics']  # MBB and MC statistics
```

## API Endpoints

### POST /api/portfolio-optimize

Optimize portfolio allocation.

**Request Body:**
```json
{
  "portfolio_size": 4,
  "top_n_assets": 15,
  "risk_free_rate": 0.1375,
  "n_bootstrap": 1000,
  "iterations": 5000
}
```

**Response:**
```json
{
  "success": true,
  "portfolio": {
    "assets": ["PETR4", "VALE3", "ITUB4", "BBDC4"],
    "weights": [0.25, 0.30, 0.25, 0.20],
    "sharpe_ratio": 1.5432,
    "expected_return": 125.50,
    "volatility": 45.30,
    "current_prices": {...},
    "allocation_10k": {...}
  },
  "parameters": {...},
  "timestamp": "2025-10-22T08:15:00"
}
```

### POST /api/option-price

Calculate theoretical option prices.

**Request Body:**
```json
{
  "ticker": "PETR4",
  "expiry_date": "2025-12-19",
  "n_bootstrap": 1000,
  "iterations": 5000,
  "risk_free_rate": 0.1375
}
```

**Response:**
```json
{
  "ticker": "PETR4",
  "current_price": 38.50,
  "expiry_date": "2025-12-19",
  "days_to_expiry": 58,
  "calls": [
    {
      "strike": 35.00,
      "market_price": 5.20,
      "theoretical_price": 4.85,
      "difference": 0.35,
      "pct_difference": 7.22,
      "prob_exercise": 0.75,
      "delta": 0.68,
      ...
    }
  ],
  "puts": [...],
  "statistics": {...}
}
```

## Frontend Pages

### Portfolio Optimizer

- **URL**: `/portfolio/optimizer`
- **Features**:
  - Interactive slider for portfolio size (3-10 assets)
  - Dropdown for top N assets selection
  - Risk-free rate input
  - Real-time optimization
  - Pie chart visualization of weights
  - Allocation table with current prices
  - Bar chart of allocation values

### Option Calculator

- **URL**: `/options/calculator`
- **Features**:
  - Ticker input with auto `.SA` suffix
  - Optional expiry date selection
  - Strike grid with all available options
  - Comparison: market price vs theoretical price
  - Color-coded differences (green=undervalued, red=overvalued)
  - Greeks display (delta, gamma, vega, theta)
  - Monte Carlo statistics
  - Price distribution chart

## Methodology

### Moving Block Bootstrap (MBB)

Preserves temporal dependencies in time series by:
1. Dividing the data into overlapping blocks
2. Randomly sampling blocks with replacement
3. Concatenating blocks to form bootstrap samples

### Monte Carlo Simulation

Uses bootstrap samples as price trajectories:
1. Select a bootstrap sample
2. Apply returns sequentially to initial price
3. Record final price
4. Repeat for many iterations

### Portfolio Optimization

Maximizes Sharpe ratio using Newton-Raphson:
1. Calculate gradient and Hessian numerically
2. Update weights with line search
3. Project to simplex (weights sum to 1, all ≥ 0)
4. Iterate until convergence

### Option Pricing

Calculates theoretical prices using MC:
1. Generate final price distribution via MBB+MC
2. Calculate expected payoff for each strike
3. Discount to present value
4. Compare with market prices

## Configuration

Default parameters:
- `n_bootstrap`: 1000 samples
- `sample_size`: 63 days (3 months)
- `iterations`: 5000 Monte Carlo iterations
- `risk_free_rate`: 0.1375 (13.75% CDI)
- `block_size`: Auto-optimized (theoretical or empirical)

## Technical Details

- **C Library**: Compiled shared library for performance
- **Memory Management**: Proper allocation and cleanup
- **Random Seed**: 1987 for reproducibility
- **Time Complexity**: O(n_bootstrap × sample_size × iterations)
- **Platform Support**: Windows (.dll), Linux (.so), macOS (.dylib)

## References

- Politis, D. N., & Romano, J. P. (1994). The stationary bootstrap.
- Künsch, H. R. (1989). The jackknife and the bootstrap for general stationary observations.
- Sharpe, W. F. (1966). Mutual fund performance.

