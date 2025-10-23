# Monte Carlo Bootstrap Simulation for Stock Price Forecasting

## Introduction

This document explains the Monte Carlo bootstrap simulation code implemented in `mcbootv3.ipynb`. This code uses historical stock price data to simulate potential future price paths, providing statistical insights into price forecasts, volatility, and risk metrics.

## What is Monte Carlo Bootstrap?

Monte Carlo bootstrap combines two powerful statistical techniques:

1. **Monte Carlo Simulation**: Generates multiple random scenarios to model the probability of different outcomes.
2. **Bootstrap Resampling**: Generates new datasets by randomly sampling with replacement from the original data, preserving the statistical properties of the original distribution.

The combination allows us to simulate potential future price paths while capturing the empirical distribution of returns without making assumptions about normality.

## How the Code Works

### 1. Data Acquisition

- Uses `yfinance` library to download historical OHLCV (Open, High, Low, Close, Volume) data
- Handles issues with MultiIndex column structures often returned by yfinance
- Supports various time frames (hourly, daily) and lookback periods

```python
# Example: Getting hourly data for a Brazilian stock
data = get_data(ticker="PETR4.SA", period="2y", interval="1h")
```

### 2. Return Calculation

- Calculates simple returns and log returns from price data
- Processes and cleans the data (removing NaN values)
- Ensures proper column structure for subsequent analysis

### 3. Empirical Distribution Estimation

- Creates an empirical Cumulative Distribution Function (CDF) of historical log returns
- Uses cubic spline interpolation to create a continuous CDF for inverse transform sampling
- Preserves the actual characteristics of returns (skewness, kurtosis, fat tails)

### 4. Monte Carlo Bootstrap Simulation

- Generates random numbers from a uniform distribution
- Maps these numbers to log returns using the empirical CDF (inverse transform sampling)
- Simulates multiple price paths starting from the last observed price
- Aggregates hourly simulations into daily prices for easier analysis

```python
# Key parameters:
# - iterations: Number of simulated paths (typically 1000+)
# - forecast_days: Number of days to forecast (typically 30)
# - hours_per_day: Trading hours per day (default 7)
```

### 5. Visualization & Analysis

The code creates comprehensive visualizations:

- **Daily Price Paths**: Shows multiple potential future price trajectories
- **Arrival Distribution**: Histogram of final prices at the end of the forecast period
- **Log Returns Distribution**: Shows the distribution of historical returns
- **Percentage Change Distribution**: Shows potential percentage changes from the current price

### 6. Statistical Analysis

- Calculates key statistics about the forecast:
  - Mean and median forecast prices
  - Standard deviation (volatility measure)
  - Various percentiles (1%, 5%, 25%, 75%, 95%, 99%)
  - Value at Risk (VaR) metrics
  - Distribution fitting tests

## Asset Comparison Functionality

The code includes features to compare forecasts across multiple assets:

- Normalized price path comparison
- Return distribution comparison 
- Risk-return metrics comparison
- Confidence interval visualization

## Interpreting the Results

The simulation provides several insights:

1. **Range of Potential Outcomes**: The spread of simulated paths shows the range of possible future prices.
2. **Probability of Price Levels**: The arrival distribution indicates the likelihood of reaching different price levels.
3. **Risk Assessment**: Percentiles help quantify downside and upside potential.
4. **Expected Return**: The mean/median of the arrival distribution indicates the expected price.
5. **Volatility**: The standard deviation of outcomes indicates the expected volatility.

## Limitations

- The model assumes that future returns will follow a similar distribution to past returns
- Does not explicitly account for regime changes or structural breaks
- Doesn't incorporate fundamental analysis or external factors
- Historical data limitations can impact the quality of the simulation

## Example Usage

```python
# Basic usage
ticker = "MSFT"  # Microsoft
iterations = 1000
forecast_days = 30
results, asset_df, raw_data = run_bootstrap(ticker, "1y", iterations, forecast_days)

# Visualize results
plot_stats = plot_mc_paths(results, raw_data)

# Compare multiple assets
compare_assets(["MSFT", "AAPL", "GOOGL"], period="6mo", iterations=500, forecast_days=30)
```

## Technical Implementation Details

- Uses NumPy for efficient numerical operations
- Leverages pandas for data manipulation
- Employs SciPy for statistical functions and interpolation
- Matplotlib and Seaborn for visualization
- Implements proper error handling and validation

This implementation provides a non-parametric approach to financial forecasting that captures the empirical characteristics of the financial time series without making strong assumptions about the underlying distribution.
