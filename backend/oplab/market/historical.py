"""
Historical data endpoints.

Provides access to historical price and options data.
"""
from typing import Dict, Optional, List
from datetime import datetime
from ..client import OPLABClient


class HistoricalAPI:
    """Historical data endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize historical data API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_historical_data(
        self,
        symbol: str,
        resolution: str,
        from_date: str,
        to_date: str,
        amount: Optional[int] = None,
        raw: bool = False,
        smooth: bool = False,
        df: str = 'timestamp'
    ) -> Optional[Dict]:
        """
        Get historical data for an instrument.
        
        Args:
            symbol: Instrument trading symbol.
            resolution: Time interval between data points (e.g., '1d', '1h', '1w', '1m', '1y').
                Format: number + letter (h=hour, d=day, w=week, m=month, y=year).
                If no letter, assumes minutes.
            from_date: Start date (ISO 8601 format: YYYY-MM-DDTHH:mm:ssZ).
            to_date: End date (ISO 8601 format: YYYY-MM-DDTHH:mm:ssZ).
            amount: Number of items according to period (hour, day, week, month, or year).
            raw: Whether to ignore financial data, returning zero values.
            smooth: Whether to fill zero close values with previous day's value.
            df: Date format ('timestamp' or 'iso', default: 'timestamp').
            
        Returns:
            Historical data object with symbol, name, resolution, and data array.
            Data array contains objects with time, open, high, low, close, volume, fvolume.
            Returns None if no data available.
            
        Example:
            >>> hist = client.market.historical.get_historical_data(
            ...     'PETR4', '1d', '2024-01-01T00:00:00Z', '2024-12-31T23:59:59Z'
            ... )
        """
        params = {
            'from': from_date,
            'to': to_date,
            'raw': raw,
            'smooth': smooth,
            'df': df
        }
        if amount is not None:
            params['amount'] = amount
        
        return self.client.get(f'/market/historical/{symbol}/{resolution}', params=params)
    
    def get_historical_options(
        self,
        spot: str,
        from_date: str,
        to_date: str,
        symbol: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Get historical options data for an underlying asset.
        
        Args:
            spot: Underlying asset trading symbol.
            from_date: Start date (YYYY-MM-DD format).
            to_date: End date (YYYY-MM-DD format).
            symbol: Specific option symbol to list (optional).
            
        Returns:
            List of historical option updates with fields including:
            symbol, time, spot (price and symbol), type, due_date, strike, premium,
            maturity_type, days_to_maturity, moneyness, Greeks (delta, gamma, vega, theta, rho),
            volatility, poe, bs.
            Returns None if no data available.
            
        Example:
            >>> hist_options = client.market.historical.get_historical_options(
            ...     'PETR4', '2024-01-01', '2024-12-31'
            ... )
        """
        params = {}
        if symbol:
            params['symbol'] = symbol
        
        return self.client.get(
            f'/market/historical/options/{spot}/{from_date}/{to_date}',
            params=params
        )
    
    def get_historical_instruments(
        self,
        tickers: str,
        date: str
    ) -> Optional[List[Dict]]:
        """
        Get instrument data for a specific date.
        
        Args:
            tickers: Comma-separated list of instrument symbols.
            date: Query date (YYYY-MM-DD format).
            
        Returns:
            List of instrument data objects for the specified date.
            Can include options or other instruments.
            Returns None if no data available.
            
        Example:
            >>> instruments = client.market.historical.get_historical_instruments(
            ...     'PETR4,ABEV3', '2024-01-15'
            ... )
        """
        params = {
            'tickers': tickers,
            'date': date
        }
        return self.client.get('/market/historical/instruments', params=params)

