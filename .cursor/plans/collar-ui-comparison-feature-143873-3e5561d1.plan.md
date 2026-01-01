<!-- 3e5561d1-19a3-4b13-9283-6c45caf71f71 f57bc862-c516-4158-a435-14f6be5f107e -->
# Collar UI Comparison Feature Implementation

## Overview

Add comparison functionality to the collar UI application, allowing users to compare two collar structures side-by-side with detailed metrics and visualizations, based on the Python script `mbb_bootstrap_paths_comparison.py`.

## Architecture

The implementation will follow this flow:

1. User inputs parameters for two structures using the Python script format (strike_put %, strike_call %, expiration date, barrier %)
2. Frontend sends both structures to new backend comparison endpoint
3. Backend performs MBB simulation for both structures and calculates comparison metrics
4. Frontend displays side-by-side comparison with charts and tables

## Implementation Steps

### 1. Backend: Create Comparison Utility Module

**File**: `backend/app/utils/collar_ui_comparison.py`

- Create `CollarUIComparison` class that:
- Accepts parameters for two structures (ticker, S0, strike_put %, strike_call %, expiration date, barrier %, n_bootstrap)
- Generates MBB paths for both structures using existing `MBBCore` and `DataGatherer`
- Calculates payoffs for each structure using the logic from `calculate_collar_ui_payoffs`
- Computes comparison metrics (Sharpe, Sortino, VaR, CVaR, probabilities, percentiles)
- Returns structured comparison data

### 2. Backend: Create Comparison API Endpoint

**File**: `backend/app/api/routes.py`

- Add `CollarUIComparisonResource` class:
- Accepts query parameters for Structure A and Structure B:
- `ticker_A`, `S0_A`, `strike_put_pct_A`, `strike_call_pct_A`, `expiration_date_A`, `barrier_pct_A`
- `ticker_B`, `S0_B`, `strike_put_pct_B`, `strike_call_pct_B`, `expiration_date_B`, `barrier_pct_B`
- `n_bootstrap` (shared)
- Validates parameters and calculates business days from expiration dates
- Calls comparison utility and returns JSON response with:
- Parameters for both structures
- Individual statistics for A and B
- Comparison metrics (differences, ratios)
- Payoff distributions for both
- Scenario probabilities

### 3. Backend: Register Comparison Endpoint

**File**: `backend/app/api/__init__.py`

- Add route registration: `api.add_resource(CollarUIComparisonResource, '/collar-ui/compare')`
- Update API documentation in index endpoint

### 4. Frontend: Update API Client

**File**: `frontend/src/api/collarUIApi.ts`

- Add TypeScript interfaces:
- `CollarUIComparisonParams` (for both structures)
- `CollarUIComparisonResponse` (with all comparison data)
- Add `getCollarUIComparison()` function to call the new endpoint

### 5. Frontend: Update Collar UI Page

**File**: `frontend/src/app/(dashboard)/options/collar-ui/page.tsx`

- Add mode toggle: "Single Structure" vs "Comparison"
- When in comparison mode:
- Display two parameter forms side-by-side (Structure A and Structure B)
- Use Python script parameter format:
- Ticker, S0, Strike Put %, Strike Call %, Expiration Date (date picker), Barrier %
- Auto-calculate max_loss and limited_gain from strikes
- Auto-calculate ttm from expiration date
- Show comparison results:
- Side-by-side parameter table
- Comparison metrics table (expected return, Sharpe, Sortino, VaR, CVaR, etc.)
- Scenario probabilities comparison
- Risk metrics comparison
- Charts:
- Overlaid payoff histograms
- Box plots side-by-side
- CDF comparison
- Risk-return scatter
- Scenario probabilities bar chart
- Recommendation section with composite score

### 6. Frontend: Add Comparison Components

**Files**: Create reusable components in `frontend/src/components/Finance/`

- `CollarUIComparisonTable.tsx` - Comparison metrics table
- `CollarUIComparisonCharts.tsx` - All comparison visualizations
- `CollarUIComparisonParams.tsx` - Parameter input forms for both structures

## Key Implementation Details

### Parameter Mapping

The Python script uses:

- `strike_put_pct` (e.g., 90.0 for 90% of S0) → converts to `max_loss = 1 - strike_put`
- `strike_call_pct` (e.g., 107.5 for 107.5% of S0) → used for gain calculation
- `barrier_pct` (e.g., 144.0 for 144% of S0) → converts to `threshold_percentage = barrier_pct / 100 - 1`
- `expiration_date` (DD-MM-YYYY) → converts to `ttm` (business days)

### Payoff Calculation Logic

Based on Python script:

- If final price < S0: payoff = max(retorno, -prejuizo_maximo)
- If final price >= S0:
- If barrier reached: payoff = min(retorno, ganho_max_ativado)
- If barrier not reached: payoff = min(retorno, ganho_max_nao_ativado)

### Comparison Metrics

Calculate and display:

- Expected return, std, Sharpe, Sortino
- VaR 5%, CVaR 5%
- Percentiles (5, 25, 50, 75, 95)
- Scenario probabilities (loss, gain without barrier, gain with barrier)
- Conditional expected gain
- Composite score for recommendation

## Testing Considerations

- Test with same ticker, different parameters
- Test with different tickers
- Test edge cases (very short/long expiration, extreme barriers)
- Validate business days calculation
- Ensure charts render correctly with different data ranges

### To-dos

- [x] Create backend utility module collar_ui_comparison.py with comparison logic based on Python script
- [x] Create CollarUIComparisonResource API endpoint in routes.py
- [ ] Register comparison endpoint in backend/app/api/__init__.py
- [ ] Add comparison API client functions and types to collarUIApi.ts
- [ ] Create comparison UI components (tables, charts, parameter forms)
- [ ] Update collar-ui page.tsx to support comparison mode with toggle and all comparison features