"""
Stocks endpoints.

Provides access to stock data including quotes, details, and listings.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class StocksAPI:
    """Stocks endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize stocks API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_stock(self, symbol: str, with_financials: Optional[str] = None) -> Optional[Dict]:
        """
        Get stock details.
        
        Args:
            symbol: Stock symbol (e.g., 'PETR4', 'VALE3').
            with_financials: Comma-separated list of additional fields to include.
                Options: sector, name, cvmCode, currency, currencyScale, dre, bpp, bpa, dfc,
                stocks, close, dividends, fundamentals, cnpj.
                
        Returns:
            Stock detail object with comprehensive stock information including:
            symbol, type, name, open, high, low, close, volume, financial_volume,
            bid, ask, category, contract_size, and many other fields.
            Returns None if no data available.
            
        Example:
            >>> stock = client.market.stocks.get_stock('PETR4', with_financials='sector,name')
            >>> print(f"{stock['name']}: {stock['close']}")
        """
        params = {}
        if with_financials:
            params['with_financials'] = with_financials
        
        return self.client.get(f'/market/stocks/{symbol}', params=params)
    
    def list_stocks(
        self,
        rank_by: str = 'volume',
        sort: str = 'asc',
        limit: int = 20,
        financial_volume_start: int = 0
    ) -> Optional[List[Dict]]:
        """
        List stocks that have options.
        
        Args:
            rank_by: Attribute to sort by (default: 'volume').
                Options include: symbol, type, name, open, high, low, close, volume,
                financial_volume, trades, bid, ask, category, and many others.
            sort: Sort order ('asc' or 'desc', default: 'asc').
            limit: Maximum number of items (default: 20).
            financial_volume_start: Minimum financial volume (default: 0).
            
        Returns:
            List of stock objects that have options listed.
            Returns None if no data available.
            
        Example:
            >>> stocks = client.market.stocks.list_stocks(rank_by='volume', sort='desc', limit=50)
        """
        params = {
            'rank_by': rank_by,
            'sort': sort,
            'limit': limit,
            'financial_volume_start': financial_volume_start
        }
        return self.client.get('/market/stocks', params=params)
    
    def list_all_stocks(
        self,
        page: int = 1,
        per: int = 20,
        rank_by: str = 'symbol',
        sort: str = 'asc',
        financial_volume_start: int = 0
    ) -> Optional[List[Dict]]:
        """
        List all stocks traded on B3.
        
        Args:
            page: Page number (default: 1).
            per: Items per page (default: 20).
            rank_by: Attribute to sort by (default: 'symbol').
                Options include: symbol, type, name, open, high, low, close, volume,
                financial_volume, trades, bid, ask, category, and many others.
            sort: Sort order ('asc' or 'desc', default: 'asc').
            financial_volume_start: Minimum financial volume (default: 0).
            
        Returns:
            List of all stock objects traded on B3.
            Returns None if no data available.
            
        Note:
            Response includes 'total-pages' header indicating total number of pages.
            
        Example:
            >>> all_stocks = client.market.stocks.list_all_stocks(page=1, per=100)
        """
        params = {
            'page': page,
            'per': per,
            'rank_by': rank_by,
            'sort': sort,
            'financial_volume_start': financial_volume_start
        }
        return self.client.get('/market/stocks/all', params=params)

