"""
Instruments endpoints.

Provides access to instrument data, search, and option series.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class InstrumentsAPI:
    """Instruments endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize instruments API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_instrument(self, symbol: str) -> Optional[Dict]:
        """
        Get instrument details.
        
        Args:
            symbol: Instrument trading symbol.
            
        Returns:
            Instrument object (can be Stock, Option, Index, RealEstateFund, etc.).
            Returns None if no data available.
            
        Example:
            >>> instrument = client.market.instruments.get_instrument('PETR4')
        """
        return self.client.get(f'/market/instruments/{symbol}')
    
    def list_instruments(self, tickers: str) -> Optional[List[Dict]]:
        """
        Get details for a list of instruments.
        
        Args:
            tickers: Comma-separated list of instrument symbols (e.g., 'PETR4,ABEV3').
            
        Returns:
            List of instrument detail objects.
            Returns None if no data available.
            
        Example:
            >>> instruments = client.market.instruments.list_instruments('PETR4,ABEV3')
        """
        params = {'tickers': tickers}
        return self.client.get('/market/instruments', params=params)
    
    def search_instruments(
        self,
        expr: str,
        limit: int = 10,
        instrument_type: Optional[str] = None,
        has_options: Optional[bool] = None,
        category: Optional[str] = None,
        add_info: Optional[bool] = None
    ) -> Optional[List[Dict]]:
        """
        Search for instruments.
        
        Args:
            expr: Trading codes or company names to search, comma-separated.
                Can include partial values.
            limit: Maximum number of items (default: 10).
            instrument_type: Instrument types to search, comma-separated.
                Options: STOCK, OPTION, INDEX, REAL_ESTATE_FUND, INDICATOR, INTEREST_RATE, BOND.
                Default: 'STOCK,OPTION'.
            has_options: Whether instrument must have options listed on B3.
            category: Option category to filter (CALL or PUT). Only considered if type is OPTION.
            add_info: Whether to include additional info (close, variation, volume, iv_current, etc.).
            
        Returns:
            List of instrument search results.
            Returns None if no data available.
            
        Example:
            >>> results = client.market.instruments.search_instruments('PETR', limit=20, has_options=True)
        """
        params = {'expr': expr, 'limit': limit}
        if instrument_type:
            params['type'] = instrument_type
        if has_options is not None:
            params['has_options'] = has_options
        if category:
            params['category'] = category
        if add_info is not None:
            params['add_info'] = add_info
        
        return self.client.get('/market/instruments/search', params=params)
    
    def get_instrument_series(
        self,
        symbol: str,
        bs: Optional[bool] = None,
        irate: Optional[float] = None
    ) -> Optional[Dict]:
        """
        Get instrument data with all option series.
        
        Args:
            symbol: Instrument trading symbol.
            bs: Whether to include Black-Scholes calculations. If provided, irate must also be specified.
            irate: Interest rate (%) required when bs is provided.
            
        Returns:
            Instrument object with series array containing option series data organized by due_date.
            Each series includes strikes with call and put option details.
            Returns None if no data available.
            
        Example:
            >>> series = client.market.instruments.get_instrument_series('PETR4', bs=True, irate=14.15)
            >>> for s in series['series']:
            ...     print(f"Due date: {s['due_date']}, Days to maturity: {s['days_to_maturity']}")
        """
        params = {}
        if bs is not None:
            params['bs'] = bs
        if irate is not None:
            params['irate'] = irate
        
        return self.client.get(f'/market/instruments/series/{symbol}', params=params)

