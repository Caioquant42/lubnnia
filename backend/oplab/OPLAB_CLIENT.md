# OPLAB API Client Documentation

## Overview

The OPLAB Client is a comprehensive Python module that provides type-safe access to all 115 endpoints from the OPLAB API v3. The module is organized into logical submodules for market data and domain (user/portfolio) management, making it easy to discover and use the available functionality.

**Base URL:** `https://api.oplab.com.br/v3`

**API Version:** 3.0

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Authentication](#authentication)
4. [Client Structure](#client-structure)
5. [Market Endpoints](#market-endpoints)
6. [Domain Endpoints](#domain-endpoints)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)
9. [Migration Guide](#migration-guide)

---

## Installation

The OPLAB client module is located in `backend/oplab/`. Ensure you have the required dependencies:

```bash
pip install requests python-dotenv
```

The module is already part of the project structure and can be imported directly:

```python
from backend.oplab import create_client
```

---

## Quick Start

### Basic Usage

```python
from backend.oplab import create_client

# Initialize client (reads OPLAB_ACCESS_TOKEN from environment)
client = create_client()

# Market data examples
stocks = client.market.stocks.list_stocks(limit=50)
options = client.market.options.list_options('PETR4')
rate = client.market.interest_rates.get_rate('SELIC')

# Domain data examples (requires authentication)
portfolios = client.domain.portfolios.list_portfolios()
```

### With Explicit Token

```python
from backend.oplab import create_client

client = create_client(access_token="your_token_here")
```

---

## Authentication

All API requests require authentication using an access token. The client supports multiple ways to provide the token:

### 1. Environment Variable (Recommended)

Create a `.env` file in the project root:

```env
OPLAB_ACCESS_TOKEN=your_access_token_here
```

The client automatically loads this via `python-dotenv`.

### 2. Direct Parameter

```python
client = create_client(access_token="your_token_here")
```

### 3. Shell Environment Variable

```bash
export OPLAB_ACCESS_TOKEN=your_token_here
python your_script.py
```

### Obtaining an Access Token

Access tokens can be obtained from:
- OpLab website: https://go.oplab.com.br/api
- Authentication endpoint: `POST /domain/users/authenticate`

---

## Client Structure

The OPLAB client is organized into two main categories:

### Market APIs
- `client.market.interest_rates` - Interest rates (SELIC, CETIP)
- `client.market.options` - Options data and calculations
- `client.market.stocks` - Stock quotes and listings
- `client.market.instruments` - Instrument search and details
- `client.market.quote` - Real-time quotes
- `client.market.historical` - Historical data
- `client.market.statistics` - Rankings and statistics
- `client.market.companies` - Company information
- `client.market.exchanges` - Exchange information
- `client.market.status` - Market status

### Domain APIs
- `client.domain.users` - User management and authentication
- `client.domain.portfolios` - Portfolio CRUD operations
- `client.domain.positions` - Position management
- `client.domain.orders` - Order management
- `client.domain.strategies` - Strategy management
- `client.domain.robots` - Robot/trading bot management
- `client.domain.watchlists` - Watchlist management
- `client.domain.notifications` - Notification management
- `client.domain.brokers` - Broker information
- `client.domain.trading_accounts` - Trading account management
- `client.domain.trading` - Trading utilities

---

## Market Endpoints

### Interest Rates

#### List All Interest Rates
```python
rates = client.market.interest_rates.list_rates()
# Returns: List of interest rate objects
```

#### Get Specific Interest Rate
```python
selic = client.market.interest_rates.get_rate('SELIC')
cetip = client.market.interest_rates.get_rate('CETIP')
# Returns: Interest rate object with uid, name, value, updated_at
```

### Options

#### List Options for an Underlying Asset
```python
options = client.market.options.list_options('PETR4')
# Returns: List of option objects (CALL and PUT)
```

#### Get Option Details
```python
option = client.market.options.get_option('PETRE100')
# Returns: Option detail object
```

#### Black-Scholes Calculation
```python
bs = client.market.options.get_black_scholes(
    symbol='PETRE100',
    irate=14.15,
    spotprice=24.71
)
# Returns: Black-Scholes calculation with Greeks
```

#### List Covered Options
```python
covered = client.market.options.list_covered_options('PETR4,ABEV3')
# Returns: List of options suitable for covered strategies
```

#### List Powders (Low-Priced Options)
```python
powders = client.market.options.list_powders()
# Returns: List of powder options
```

### Stocks

#### Get Stock Details
```python
stock = client.market.stocks.get_stock('PETR4', with_financials='sector,name')
# Returns: Stock detail object
```

#### List Stocks with Options
```python
stocks = client.market.stocks.list_stocks(
    rank_by='volume',
    sort='desc',
    limit=50
)
# Returns: List of stocks that have options
```

#### List All Stocks
```python
all_stocks = client.market.stocks.list_all_stocks(
    page=1,
    per=100,
    rank_by='symbol'
)
# Returns: Paginated list of all stocks on B3
```

### Instruments

#### Get Instrument Details
```python
instrument = client.market.instruments.get_instrument('PETR4')
# Returns: Instrument object
```

#### List Multiple Instruments
```python
instruments = client.market.instruments.list_instruments('PETR4,ABEV3')
# Returns: List of instrument objects
```

#### Search Instruments
```python
results = client.market.instruments.search_instruments(
    expr='PETR',
    limit=20,
    has_options=True
)
# Returns: List of matching instruments
```

#### Get Instrument Series
```python
series = client.market.instruments.get_instrument_series(
    'PETR4',
    bs=True,
    irate=14.15
)
# Returns: Instrument with all option series organized by due_date
```

### Quote

#### Get Real-Time Quotes
```python
quotes = client.market.quote.get_quote('PETR4,PETRE100')
# Returns: List of quote objects
```

### Historical Data

#### Get Historical Data
```python
historical = client.market.historical.get_historical_data(
    symbol='PETR4',
    resolution='1d',
    from_date='2024-01-01T00:00:00Z',
    to_date='2024-12-31T23:59:59Z'
)
# Returns: Historical data object with time series
```

#### Get Historical Options
```python
hist_options = client.market.historical.get_historical_options(
    spot='PETR4',
    from_date='2024-01-01',
    to_date='2024-12-31'
)
# Returns: List of historical option updates
```

#### Get Historical Instruments
```python
instruments = client.market.historical.get_historical_instruments(
    tickers='PETR4,ABEV3',
    date='2024-01-15'
)
# Returns: List of instrument data for specific date
```

### Statistics and Rankings

#### Highest Options Volume
```python
top_volume = client.market.statistics.get_highest_options_volume(
    order_by='total',
    limit=10
)
```

#### Best Covered Options Rates
```python
best_calls = client.market.statistics.get_best_covered_options_rates('CALL', limit=10)
best_puts = client.market.statistics.get_best_covered_options_rates('PUT', limit=10)
```

#### Highest Options Variation
```python
top_variations = client.market.statistics.get_highest_options_variation('PUT', limit=15)
```

#### M9_M21 Ranking
```python
trends = client.market.statistics.get_m9_m21_ranking(
    sort='desc',
    limit=30
)
```

#### IBOV Correlation Ranking
```python
correlations = client.market.statistics.get_correl_ibov_ranking(sort='desc')
```

#### Fundamental Ranking
```python
roe_ranking = client.market.statistics.get_fundamental_ranking(
    attribute='roe',
    sort='desc'
)
```

#### OpLab Score Ranking
```python
top_scores = client.market.statistics.get_oplab_score_ranking(
    sort='desc',
    limit=50
)
```

### Companies

#### Get Company Data
```python
companies = client.market.companies.get_companies(
    symbols='PETR4,ABEV3',
    includes='sector,name,close'
)
```

### Exchanges

#### List Exchanges
```python
exchanges = client.market.exchanges.list_exchanges()
```

#### Get Exchange Details
```python
exchange = client.market.exchanges.get_exchange('BOVESPA')
```

### Market Status

#### Get Market Status
```python
status = client.market.status.get_market_status()
# Returns: Market status object with current market state
# Status codes: P (Pre-opening), A (Open), N (Closed), etc.
```

---

## Domain Endpoints

### Users

#### Authenticate
```python
user = client.domain.users.authenticate(
    email='user@example.com',
    password='password'
)
# Returns: User info with access token
```

#### Authorize
```python
user = client.domain.users.authorize()
# Returns: User info using current access token
```

#### Get Settings
```python
settings = client.domain.users.get_settings()
admin_settings = client.domain.users.get_settings('admin')
```

#### Update Settings
```python
prefs = json.dumps({
    "interest_rate_type": "SELIC",
    "order_amount": 1000
})
client.domain.users.update_settings(prefs)
```

#### Reset Password
```python
client.domain.users.reset_password('user@example.com')
```

### Portfolios

#### List Portfolios
```python
portfolios = client.domain.portfolios.list_portfolios()
```

#### Create Portfolio
```python
portfolio = client.domain.portfolios.create_portfolio('My Portfolio')
```

#### Get Portfolio
```python
portfolio = client.domain.portfolios.get_portfolio(12345)
```

#### Update Portfolio
```python
portfolio = client.domain.portfolios.update_portfolio(12345, name='Updated Name')
```

#### Delete Portfolio
```python
client.domain.portfolios.delete_portfolio(12345)
```

#### Set Default Portfolio
```python
client.domain.portfolios.set_default_portfolio(12345)
```

#### Get Portfolio Returns
```python
returns = client.domain.portfolios.get_portfolio_returns(
    12345,
    from_date='2024-01-01',
    to_date='2024-12-31'
)
```

### Positions

#### List Positions
```python
positions = client.domain.positions.list_positions(12345, status='all')
```

#### Get Position
```python
position = client.domain.positions.get_position(12345, 100)
```

#### Update Position
```python
position = client.domain.positions.update_position(
    12345, 100,
    name='Updated Position',
    strategy_id=5
)
```

#### Tag/Untag Position
```python
client.domain.positions.tag_position(12345, 100, 'important')
client.domain.positions.untag_position(12345, 100, 'important')
```

#### Commit Position
```python
position = client.domain.positions.commit_position(12345, 100)
```

#### Close Position
```python
position = client.domain.positions.close_position(12345, 100, exercise=True)
```

### Orders

#### List Portfolio Orders
```python
orders = client.domain.orders.list_portfolio_orders(
    12345,
    status='pending',
    order_type='market'
)
```

#### Create Order
```python
order = client.domain.orders.create_portfolio_order(
    12345,
    symbol='PETR4',
    price=28.0,
    amount=100,
    side='BUY',
    order_type='market'
)
```

#### Execute Order
```python
order = client.domain.orders.execute_portfolio_order(12345, 100)
```

#### Export Orders
```python
client.domain.orders.export_portfolio_orders(12345)
# Starts background process, notification sent when complete
```

### Strategies

#### List Strategies
```python
strategies = client.domain.strategies.list_strategies(12345, status='all')
```

#### Create Strategy
```python
strategy = client.domain.strategies.create_strategy(
    12345,
    name='Covered Call',
    underlying='PETR4',
    positions=[{
        'symbol': 'PETR4',
        'amount': 100,
        'side': 'BUY',
        'price': 28.0
    }]
)
```

#### Commit Strategy
```python
positions = client.domain.strategies.commit_strategy(12345, 100)
```

#### Close Strategy
```python
strategy = client.domain.strategies.close_strategy(12345, 100)
```

### Robots

#### List Robots
```python
robots = client.domain.robots.list_robots(12345, status='0,1')
```

#### Create Robot
```python
robot = client.domain.robots.create_robot(
    12345,
    trading_account_id=9,
    strategy={'name': 'Trava de alta', 'underlying': 'PETR4'},
    legs=[{
        'symbol': 'PETRI216',
        'target_amount': 1000,
        'side': 'SELL',
        'depth': 1
    }]
)
```

#### Pause/Resume Robot
```python
client.domain.robots.pause_robot(12345, 100)
client.domain.robots.resume_robot(12345, 100)
```

#### Get Robot Logs
```python
log = client.domain.robots.get_robot_log(12345, 100)
```

### Watchlists

#### List Watchlists
```python
watchlists = client.domain.watchlists.list_watchlists()
```

#### Create Watchlist
```python
watchlist = client.domain.watchlists.create_watchlist('My Watchlist')
```

#### Add/Remove Instruments
```python
client.domain.watchlists.add_instrument('default', 'PETR4', weight=10)
client.domain.watchlists.remove_instrument('default', 'PETR4')
```

### Notifications

#### List Notifications
```python
notifications = client.domain.notifications.list_notifications(page=1, per=20)
```

#### Get Unread Count
```python
count = client.domain.notifications.get_unread_count()
```

#### Mark All as Read
```python
client.domain.notifications.mark_all_read()
```

### Brokers

#### List Brokers
```python
brokers = client.domain.brokers.list_brokers()
```

#### Sign Up to Broker
```python
account = client.domain.brokers.sign_up(broker_id=1, plan_id=19, pin='2134')
```

### Trading Accounts

#### List Trading Accounts
```python
accounts = client.domain.trading_accounts.list_trading_accounts()
```

#### Get Pending Terms
```python
terms = client.domain.trading_accounts.get_pending_terms(9)
```

#### Agree to Term
```python
client.domain.trading_accounts.agree_term(9, 1)
```

### Trading Utilities

#### Calculate Business Days
```python
result = client.domain.trading.get_business_days('2024-12-31')
# Returns: Object with business days count
```

---

## Error Handling

The client uses custom exception classes for different error scenarios:

```python
from backend.oplab.exceptions import (
    OPLABUnauthorizedError,
    OPLABNotFoundError,
    OPLABRateLimitError,
    OPLABServerError,
)

try:
    stock = client.market.stocks.get_stock('INVALID')
except OPLABNotFoundError:
    print("Stock not found")
except OPLABUnauthorizedError:
    print("Invalid access token")
except OPLABRateLimitError:
    print("Rate limit exceeded, please wait")
except OPLABServerError:
    print("Server error, please try again later")
```

### Available Exception Classes

- `OPLABException` - Base exception for all OPLAB errors
- `OPLABUnauthorizedError` - 401: Invalid access token
- `OPLABPaymentRequiredError` - 402: Subscription expired
- `OPLABForbiddenError` - 403: Plan doesn't allow access
- `OPLABNotFoundError` - 404: Resource not found
- `OPLABPreconditionFailedError` - 412: Action requirements not met
- `OPLABUnprocessableEntityError` - 422: Request cannot be processed
- `OPLABRateLimitError` - 429: Rate limit exceeded
- `OPLABServerError` - 500, 503: Server errors

### Retry Logic

The client includes automatic retry logic for transient network errors:

```python
# Default: 3 retries with 5 second delay
stock = client.market.stocks.get_stock('PETR4')

# Custom retry configuration
stock = client.market.stocks.get_stock(
    'PETR4',
    max_retries=5,
    delay=10,
    timeout=60
)
```

---

## Best Practices

### 1. Reuse Client Instance

Create the client once and reuse it throughout your application:

```python
# Good: Create once, reuse
client = create_client()
stocks = client.market.stocks.list_stocks()
options = client.market.options.list_options('PETR4')

# Avoid: Creating multiple clients
client1 = create_client()
client2 = create_client()  # Unnecessary
```

### 2. Handle Errors Gracefully

```python
try:
    data = client.market.stocks.get_stock('PETR4')
    if data:
        print(f"Price: {data['close']}")
    else:
        print("No data available")
except OPLABUnauthorizedError:
    print("Please check your access token")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### 3. Use Type Hints

All methods include type hints for better IDE support:

```python
from typing import Optional, Dict, List

def get_stock_price(symbol: str) -> Optional[float]:
    stock = client.market.stocks.get_stock(symbol)
    return stock['close'] if stock else None
```

### 4. Batch Operations

When fetching multiple items, consider using list endpoints instead of individual calls:

```python
# Good: Single API call
stocks = client.market.stocks.list_stocks(limit=100)

# Less efficient: Multiple API calls
stocks = []
for symbol in ['PETR4', 'VALE3', 'ABEV3']:
    stock = client.market.stocks.get_stock(symbol)
    if stock:
        stocks.append(stock)
```

### 5. Use Pagination

For large datasets, use pagination:

```python
all_stocks = []
page = 1
while True:
    stocks = client.market.stocks.list_all_stocks(page=page, per=100)
    if not stocks:
        break
    all_stocks.extend(stocks)
    page += 1
```

---

## Migration Guide

### From Direct API Calls to OPLAB Client

If you're migrating from direct `requests` calls to the OPLAB client:

#### Before (Direct API Call)
```python
import requests
import os

headers = {'Access-Token': os.getenv('OPLAB_ACCESS_TOKEN')}
response = requests.get(
    'https://api.oplab.com.br/v3/market/stocks/PETR4',
    headers=headers
)
data = response.json()
```

#### After (OPLAB Client)
```python
from backend.oplab import create_client

client = create_client()
data = client.market.stocks.get_stock('PETR4')
```

### Example: Migrating collar.py Functions

The `collar.py` file has been migrated to use the OPLAB client:

#### Before
```python
def fetch_interest_rate(rate_id: str):
    url = f"https://api.oplab.com.br/v3/market/interest_rates/{rate_id}"
    response = requests.get(url, headers=headers)
    return response.json()
```

#### After
```python
from backend.oplab import create_client

_oplab_client = create_client()

def fetch_interest_rate(rate_id: str):
    return _oplab_client.market.interest_rates.get_rate(rate_id)
```

---

## Complete API Reference

### Market Endpoints Summary

| Category | Endpoints | Module |
|----------|-----------|--------|
| Interest Rates | 2 | `market.interest_rates` |
| Options | 6 | `market.options` |
| Stocks | 4 | `market.stocks` |
| Instruments | 5 | `market.instruments` |
| Quote | 1 | `market.quote` |
| Historical | 3 | `market.historical` |
| Statistics | 7 | `market.statistics` |
| Companies | 1 | `market.companies` |
| Exchanges | 2 | `market.exchanges` |
| Market Status | 1 | `market.status` |
| **Total** | **32** | |

### Domain Endpoints Summary

| Category | Endpoints | Module |
|----------|-----------|--------|
| Users | 7 | `domain.users` |
| Portfolios | 15 | `domain.portfolios` |
| Positions | 11 | `domain.positions` |
| Orders | 15 | `domain.orders` |
| Strategies | 6 | `domain.strategies` |
| Robots | 8 | `domain.robots` |
| Watchlists | 6 | `domain.watchlists` |
| Notifications | 9 | `domain.notifications` |
| Brokers | 3 | `domain.brokers` |
| Trading Accounts | 7 | `domain.trading_accounts` |
| Trading | 1 | `domain.trading` |
| **Total** | **88** | |

**Grand Total: 120 endpoints** (115 unique + some with multiple methods)

---

## Examples

### Complete Workflow Example

```python
from backend.oplab import create_client

# Initialize client
client = create_client()

# 1. Get market data
selic_rate = client.market.interest_rates.get_rate('SELIC')
print(f"SELIC Rate: {selic_rate['value']}%")

# 2. Get stock data
petr4 = client.market.stocks.get_stock('PETR4')
print(f"PETR4 Price: {petr4['close']}")

# 3. Get options
options = client.market.options.list_options('PETR4')
calls = [opt for opt in options if opt['category'] == 'CALL']
print(f"Found {len(calls)} CALL options")

# 4. Calculate Black-Scholes
if calls:
    bs = client.market.options.get_black_scholes(
        symbol=calls[0]['symbol'],
        irate=selic_rate['value'],
        spotprice=petr4['close']
    )
    print(f"Theoretical Price: {bs['price']}")
    print(f"Delta: {bs['delta']}")

# 5. Domain operations (if authenticated)
try:
    portfolios = client.domain.portfolios.list_portfolios()
    print(f"You have {len(portfolios)} portfolios")
except OPLABUnauthorizedError:
    print("Domain operations require authentication")
```

### Error Handling Example

```python
from backend.oplab import create_client
from backend.oplab.exceptions import (
    OPLABUnauthorizedError,
    OPLABNotFoundError,
    OPLABRateLimitError,
)

client = create_client()

def safe_get_stock(symbol: str):
    try:
        stock = client.market.stocks.get_stock(symbol)
        return stock
    except OPLABNotFoundError:
        print(f"Stock {symbol} not found")
        return None
    except OPLABUnauthorizedError:
        print("Authentication failed. Please check your access token.")
        return None
    except OPLABRateLimitError:
        print("Rate limit exceeded. Please wait before retrying.")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage
stock = safe_get_stock('PETR4')
if stock:
    print(f"Price: {stock['close']}")
```

---

## Testing

A comprehensive test suite is available in `backend/tests/test_oplab_client.py`. Run tests with:

```bash
cd backend
pytest tests/test_oplab_client.py -v
```

The test suite covers:
- Client initialization
- API module attachment
- HTTP request methods
- Error handling
- Retry logic
- Market and domain API methods

---

## Support

For API documentation and endpoint details, see:
- [OPLAB API Overview](./OPLAB_API_OVERVIEW.md) - Complete endpoint reference
- [OpenAPI Specification](../backend/data-source/oplab_openapi.json) - Full API specification

For issues or questions:
- Check the test file for usage examples
- Review the source code in `backend/oplab/`
- Consult the OPLAB API documentation

---

## Changelog

### Version 1.0.0
- Initial implementation of all 115 OPLAB API v3 endpoints
- Organized into market and domain submodules
- Comprehensive error handling with custom exceptions
- Automatic retry logic for network errors
- Full type hints and documentation
- Migration of existing `collar.py` functions to use client

