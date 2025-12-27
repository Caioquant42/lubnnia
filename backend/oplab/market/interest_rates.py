"""
Interest rates endpoints.

Provides access to interest rate data including CETIP and SELIC rates.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class InterestRatesAPI:
    """Interest rates endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize interest rates API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_rates(self) -> Optional[List[Dict]]:
        """
        List all available interest rates.
        
        Returns:
            List of interest rate objects with uid, name, value, updated_at.
            Returns None if no data available.
            
        Example:
            >>> rates = client.market.interest_rates.list_rates()
            >>> for rate in rates:
            ...     print(f"{rate['name']}: {rate['value']}%")
        """
        return self.client.get('/market/interest_rates')
    
    def get_rate(self, rate_id: str) -> Optional[Dict]:
        """
        Get specific interest rate.
        
        Args:
            rate_id: Interest rate ID ('CETIP' or 'SELIC').
            
        Returns:
            Interest rate object with uid, name, value, updated_at.
            Returns None if no data available.
            
        Example:
            >>> selic = client.market.interest_rates.get_rate('SELIC')
            >>> print(f"SELIC rate: {selic['value']}%")
        """
        return self.client.get(f'/market/interest_rates/{rate_id}')

