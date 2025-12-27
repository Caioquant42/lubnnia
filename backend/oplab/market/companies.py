"""
Companies endpoints.

Provides access to company data and information.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class CompaniesAPI:
    """Companies endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize companies API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_companies(
        self,
        symbols: str,
        includes: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Get company data for a list of symbols.
        
        Args:
            symbols: Comma-separated list of stock symbols (e.g., 'PETR4,ABEV3').
            includes: Comma-separated list of additional attributes to include.
                Options include: type, name, open, high, low, close, volume, financial_volume,
                trades, bid, ask, category, exchange_id, created_at, updated_at, variation,
                has_options, middle_term_trend, semi_return_1y, short_term_trend, stdv_1y,
                stdv_5d, beta_ibov, and many others including financial data.
                
        Returns:
            List of company objects. Response will include attributes specified in `includes`.
            Returns None if no data available.
            
        Example:
            >>> companies = client.market.companies.get_companies(
            ...     'PETR4,ABEV3',
            ...     includes='sector,name,close'
            ... )
        """
        params = {'symbols': symbols}
        if includes:
            params['includes'] = includes
        
        return self.client.get('/market/companies', params=params)

