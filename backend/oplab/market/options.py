"""
Options endpoints.

Provides access to options data, Black-Scholes calculations, and option strategies.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class OptionsAPI:
    """Options endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize options API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_options(self, symbol: str) -> Optional[List[Dict]]:
        """
        List all options for an underlying asset.
        
        Args:
            symbol: Underlying stock symbol (e.g., 'PETR4', 'VALE3').
            
        Returns:
            List of option objects (CALL and PUT) with fields including:
            symbol, category (CALL/PUT), strike, due_date, days_to_maturity,
            bid, ask, close, open, high, low, volume, financial_volume, spot_price.
            Returns None if no data available.
            
        Example:
            >>> options = client.market.options.list_options('PETR4')
            >>> calls = [opt for opt in options if opt['category'] == 'CALL']
        """
        return self.client.get(f'/market/options/{symbol}')
    
    def get_option(self, symbol: str) -> Optional[Dict]:
        """
        Get specific option details.
        
        Args:
            symbol: Option trading symbol (e.g., 'PETRE100').
            
        Returns:
            Option detail object with all option information including parent_symbol.
            Returns None if no data available.
            
        Example:
            >>> option = client.market.options.get_option('PETRE100')
            >>> print(f"Strike: {option['strike']}, Premium: {option['close']}")
        """
        return self.client.get(f'/market/options/details/{symbol}')
    
    def get_black_scholes(
        self,
        symbol: Optional[str] = None,
        irate: float = 0,
        option_type: Optional[str] = None,
        spotprice: float = 0,
        strike: float = 0,
        premium: float = 0,
        dtm: int = 0,
        vol: float = 0,
        duedate: Optional[str] = None,
        amount: int = 0
    ) -> Optional[Dict]:
        """
        Get Black-Scholes calculation for an option.
        
        Args:
            symbol: Option trading symbol (required if not providing type/strike/duedate).
            irate: Interest rate value (%) (required).
            option_type: Option type ('CALL' or 'PUT'). Required if symbol not provided.
            spotprice: Current underlying price.
            strike: Strike price. Required if symbol is a stock code.
            premium: Option premium.
            dtm: Days to maturity.
            vol: Implied volatility.
            duedate: Due date (YYYY-MM-DD). Required if symbol is a stock code.
            amount: Number of contracts.
            
        Returns:
            Black-Scholes calculation object with:
            moneyness, price, delta, gamma, vega, theta, rho, volatility, poe,
            spotprice, strike, margin.
            Returns None if no data available.
            
        Example:
            >>> bs = client.market.options.get_black_scholes(
            ...     symbol='PETRE100',
            ...     irate=14.15,
            ...     spotprice=24.71
            ... )
            >>> print(f"Theoretical price: {bs['price']}, Delta: {bs['delta']}")
        """
        params = {
            'symbol': symbol,
            'irate': irate,
            'type': option_type,
            'spotprice': spotprice,
            'strike': strike,
            'premium': premium,
            'dtm': dtm,
            'vol': vol,
            'duedate': duedate,
            'amount': amount
        }
        # Remove None values and zeros for optional parameters
        params = {k: v for k, v in params.items() if v is not None and (v != 0 or k in ['symbol', 'irate'])}
        
        return self.client.get('/market/options/bs', params=params)
    
    def list_covered_options(self, underlying: str) -> Optional[List[Dict]]:
        """
        List options for covered strategies.
        
        Gets options with strike less than or equal to the price of one or more assets.
        
        Args:
            underlying: Comma-separated list of underlying symbols (e.g., 'PETR4,ABEV3').
            
        Returns:
            List of options suitable for covered strategies.
            Returns None if no data available.
            
        Example:
            >>> covered = client.market.options.list_covered_options('PETR4,ABEV3')
        """
        params = {'underlying': underlying} if underlying else None
        return self.client.get('/market/options/strategies/covered', params=params)
    
    def list_powders(self) -> Optional[List[Dict]]:
        """
        List main "pozinhos" (low-priced options).
        
        Returns:
            List of powder options with pricing and volume information.
            Returns None if no data available.
            
        Example:
            >>> powders = client.market.options.list_powders()
            >>> for powder in powders:
            ...     print(f"{powder['symbol']}: {powder['close']}")
        """
        return self.client.get('/market/options/powders')

