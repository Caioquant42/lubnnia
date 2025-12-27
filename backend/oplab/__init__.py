"""
OPLAB API Client Module

Provides a comprehensive Python interface to the OPLAB API v3.
All endpoints from the OpenAPI specification are available through
organized API classes.

Example usage:
    from backend.oplab import create_client

    client = create_client()

    # Market data
    stocks = client.market.stocks.list_stocks()
    options = client.market.options.list_options('PETR4')
    rate = client.market.interest_rates.get_rate('SELIC')

    # Domain data (requires authentication)
    portfolios = client.domain.portfolios.list_portfolios()
"""
from typing import Optional

from .client import OPLABClient

# Market API imports
from .market.interest_rates import InterestRatesAPI
from .market.options import OptionsAPI
from .market.stocks import StocksAPI
from .market.instruments import InstrumentsAPI
from .market.quote import QuoteAPI
from .market.historical import HistoricalAPI
from .market.statistics import StatisticsAPI
from .market.companies import CompaniesAPI
from .market.exchanges import ExchangesAPI
from .market.status import MarketStatusAPI

# Domain API imports
from .domain.users import UsersAPI
from .domain.portfolios import PortfoliosAPI
from .domain.positions import PositionsAPI
from .domain.orders import OrdersAPI
from .domain.strategies import StrategiesAPI
from .domain.robots import RobotsAPI
from .domain.watchlists import WatchlistsAPI
from .domain.notifications import NotificationsAPI
from .domain.brokers import BrokersAPI
from .domain.trading_accounts import TradingAccountsAPI
from .domain.trading import TradingAPI


def _attach_apis(client: OPLABClient) -> OPLABClient:
    """
    Attach API modules to client instance for easy access.
    
    Args:
        client: OPLABClient instance.
        
    Returns:
        Client with attached API modules.
    """
    # Market APIs
    client.market = type('Market', (), {})()
    client.market.interest_rates = InterestRatesAPI(client)
    client.market.options = OptionsAPI(client)
    client.market.stocks = StocksAPI(client)
    client.market.instruments = InstrumentsAPI(client)
    client.market.quote = QuoteAPI(client)
    client.market.historical = HistoricalAPI(client)
    client.market.statistics = StatisticsAPI(client)
    client.market.companies = CompaniesAPI(client)
    client.market.exchanges = ExchangesAPI(client)
    client.market.status = MarketStatusAPI(client)
    
    # Domain APIs
    client.domain = type('Domain', (), {})()
    client.domain.users = UsersAPI(client)
    client.domain.portfolios = PortfoliosAPI(client)
    client.domain.positions = PositionsAPI(client)
    client.domain.orders = OrdersAPI(client)
    client.domain.strategies = StrategiesAPI(client)
    client.domain.robots = RobotsAPI(client)
    client.domain.watchlists = WatchlistsAPI(client)
    client.domain.notifications = NotificationsAPI(client)
    client.domain.brokers = BrokersAPI(client)
    client.domain.trading_accounts = TradingAccountsAPI(client)
    client.domain.trading = TradingAPI(client)
    
    return client


def create_client(access_token: Optional[str] = None) -> OPLABClient:
    """
    Create and configure OPLAB client with all API modules attached.
    
    Args:
        access_token: API access token. If None, reads from OPLAB_ACCESS_TOKEN env var.
        
    Returns:
        Configured OPLABClient instance with market and domain APIs attached.
        
    Example:
        >>> from backend.oplab import create_client
        >>> client = create_client()
        >>> stocks = client.market.stocks.list_stocks()
    """
    client = OPLABClient(access_token)
    return _attach_apis(client)


__all__ = ['OPLABClient', 'create_client']

