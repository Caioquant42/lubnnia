# Portfolio Optimization System - Optimized Version

## Overview

This is a high-performance portfolio optimization system that combines Python and C for financial computations. The system uses Moving Block Bootstrap and Monte Carlo simulations to generate asset price scenarios, then optimizes portfolio weights using Newton-Raphson optimization implemented in C.

## Key Features

### 🚀 Performance Optimizations
- **C Implementation**: All heavy computations (bootstrap, Monte Carlo, optimization) run in C
- **50-60% Code Reduction**: Streamlined codebase while maintaining functionality
- **Deterministic Results**: All random seeds set to 1987 for reproducible results
- **Memory Efficient**: Optimized memory allocation and cleanup

### 📊 Monte Carlo Asset Selection
- **2000 Simulations**: Monte Carlo analysis for asset selection
- **Top 20 Assets**: Automatically selects best performing assets
- **Deterministic Selection**: Consistent asset selection across runs

### 🎯 Portfolio Optimization
- **5000 Monte Carlo Iterations**: High-precision simulations
- **1000 Bootstrap Samples**: Preserves temporal dependencies
- **Newton-Raphson Optimization**: C-implemented for maximum performance
- **4-Asset Portfolio**: Optimized for Brazilian market

## System Architecture

### Python Layer (Data & Visualization)
```
main_optimized.py          # Main orchestration
get_data_optimized.py      # Data fetching and asset selection
```

### C Layer (Computation Engine)
```
functions_optimized.c      # Core algorithms
functions.so              # Compiled library
```

### Key Functions

#### Moving Block Bootstrap
- **Purpose**: Generate bootstrap samples preserving temporal structure
- **Implementation**: C with optimized block size selection
- **Parameters**: 1000 samples, 63-day periods, dynamic block size

#### Monte Carlo Simulation
- **Purpose**: Generate asset price scenarios
- **Implementation**: C with complete temporal path preservation
- **Parameters**: 5000 iterations per asset

#### Newton-Raphson Optimization
- **Purpose**: Maximize Sharpe ratio
- **Implementation**: C with numerical differentiation
- **Features**: Line search, regularization, simplex projection

## Data Flow

1. **Asset Selection** (Python)
   - Download IBOVESPA data (86 assets)
   - Monte Carlo analysis (2000 simulations)
   - Select top 20 assets

2. **Data Processing** (Python)
   - Download recent data (63 days)
   - Calculate log returns
   - Handle missing data gracefully

3. **Bootstrap Generation** (C)
   - Moving block bootstrap per asset
   - Optimized block size selection
   - 1000 samples per asset

4. **Monte Carlo Simulation** (C)
   - 5000 iterations per asset
   - Complete temporal path preservation
   - Generate arrival values

5. **Portfolio Optimization** (C)
   - Newton-Raphson optimization
   - Maximize Sharpe ratio
   - Constrain to valid weights

6. **Results & Visualization** (Python)
   - Portfolio metrics calculation
   - Comprehensive visualizations
   - Individual asset plots

## Key Improvements

### Deterministic Results
- **Consistent Seeds**: All random seeds set to 1987
- **Reproducible Selection**: Same assets selected across runs
- **Stable Optimization**: Consistent portfolio weights

### Error Handling
- **Graceful Degradation**: Skip assets with missing data
- **Robust Data Fetching**: Handle network issues and delisted assets
- **Memory Management**: Proper cleanup and error recovery

### Performance Enhancements
- **C Library**: All heavy computations in C
- **Optimized Algorithms**: Streamlined implementations
- **Efficient Memory**: Reduced memory footprint

## Output Files

### Core Results
- `arrival_values.csv`: Monte Carlo arrival values (5000 × 20 assets)
- `all_portfolio_results.csv`: All portfolio combinations and metrics
- `best_portfolio_details.csv`: Optimal portfolio details

### Visualizations
- `portfolio_optimization_results.png`: Main portfolio analysis
- `monte_carlo_*.png`: Individual asset Monte Carlo plots (20 files)
- `block_size_optimization_mean.png`: Block size optimization analysis

### Individual Asset Plots
Each asset gets a comprehensive Monte Carlo visualization:
- Final price distributions
- Return distributions  
- Sample price paths
- Bootstrap statistics

## Technical Specifications

### Monte Carlo Parameters
- **Iterations**: 5000 per asset
- **Bootstrap Samples**: 1000 per asset
- **Sample Size**: 63 days (consistent)
- **Block Size**: Dynamically optimized per asset

### Portfolio Parameters
- **Size**: 4 assets
- **Optimization**: Newton-Raphson
- **Objective**: Maximize Sharpe ratio
- **Constraints**: Non-negative weights, sum to 1

### Data Parameters
- **Universe**: 86 IBOVESPA assets
- **Selection**: Top 20 via Monte Carlo
- **Period**: 63 days (recent data)
- **Frequency**: Daily returns

## Usage

### Compilation
```bash
make -f Makefile_optimized clean
make -f Makefile_optimized
```

### Execution
```bash
source ../../myenv/bin/activate
make -f Makefile_optimized run
```

### Dependencies
- Python: numpy, pandas, matplotlib, seaborn, yfinance
- C: gcc with math library
- System: Linux with standard development tools

## Performance Characteristics

### Computation Time
- **Asset Selection**: ~2-3 minutes (2000 Monte Carlo simulations)
- **Data Processing**: ~30 seconds (20 assets, 63 days)
- **Bootstrap Generation**: ~1-2 minutes (1000 samples per asset)
- **Monte Carlo Simulation**: ~3-5 minutes (5000 iterations per asset)
- **Portfolio Optimization**: ~1-2 minutes (Newton-Raphson)

### Memory Usage
- **Peak**: ~500MB during Monte Carlo simulations
- **Final**: ~100MB for results and visualizations

### Accuracy
- **Deterministic**: Same results across runs
- **Precision**: 5000 Monte Carlo iterations ensure high accuracy
- **Robustness**: Handles missing data and edge cases

## Key Innovations

1. **Hybrid Architecture**: Python for data/visualization, C for computation
2. **Deterministic Monte Carlo**: Reproducible asset selection
3. **Temporal Preservation**: Complete bootstrap sample usage
4. **Optimized Block Size**: Theoretical and empirical methods
5. **Comprehensive Visualization**: Individual asset analysis
6. **Robust Error Handling**: Graceful degradation for missing data

## Future Enhancements

- **Parallel Processing**: Multi-threaded Monte Carlo simulations
- **GPU Acceleration**: CUDA implementation for large-scale simulations
- **Real-time Updates**: Live data integration
- **Risk Metrics**: Additional risk measures (VaR, CVaR)
- **Dynamic Rebalancing**: Time-varying portfolio optimization 