"""
Quote endpoints.

Provides access to real-time quotes for multiple instruments.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class QuoteAPI:
    """Quote endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize quote API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_quote(self, tickers: str) -> Optional[List[Dict]]:
        """
        Get quotes for a list of instruments.
        
        Args:
            tickers: Comma-separated list of instrument symbols (e.g., 'PETR4,PETRE100').
            
        Returns:
            List of quote objects with fields including:
            symbol, close, strike, variation, volume, financial_volume,
            bid, ask, bid_volume, ask_volume, time, open, high, low.
            Returns None if no data available.
            
        Example:
            >>> quotes = client.market.quote.get_quote('PETR4,PETRE100')
            >>> for quote in quotes:
            ...     print(f"{quote['symbol']}: {quote['close']}")
        """
        params = {'tickers': tickers}
        return self.client.get('/market/quote', params=params)

