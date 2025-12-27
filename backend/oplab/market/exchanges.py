"""
Exchanges endpoints.

Provides access to stock exchange information.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class ExchangesAPI:
    """Exchanges endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize exchanges API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_exchanges(self) -> Optional[List[Dict]]:
        """
        List all stock exchanges in Brazil.
        
        Returns:
            List of exchange objects with exchange information.
            Returns None if no data available.
            
        Example:
            >>> exchanges = client.market.exchanges.list_exchanges()
        """
        return self.client.get('/market/exchanges')
    
    def get_exchange(self, uid: str) -> Optional[Dict]:
        """
        Get specific exchange details.
        
        Args:
            uid: Exchange UID.
            
        Returns:
            Exchange object with exchange details.
            Returns None if no data available.
            
        Example:
            >>> exchange = client.market.exchanges.get_exchange('BOVESPA')
        """
        return self.client.get(f'/market/exchanges/{uid}')

