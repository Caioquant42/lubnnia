"""
Market status endpoints.

Provides access to current market status information.
"""
from typing import Dict, Optional
from ..client import OPLABClient


class MarketStatusAPI:
    """Market status endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize market status API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_market_status(self) -> Optional[Dict]:
        """
        Get current market status.
        
        Returns:
            Market status object with:
            - server_time: Server time
            - market_status: Market status code
                - 'P' = Pré abertura (Pre-opening)
                - 'A' = Abertura (Opening - normal session)
                - 'PN' = Pré fechamento (Pre-closing)
                - 'N' = Fechamento (Closing)
                - 'E' = Pré abertura do after (After-hours pre-opening)
                - 'R' = Abertura After (After-hours opening)
                - 'NE' = Fechamento do after (After-hours closing)
                - 'F' = Final (Final)
            Returns None if no data available.
            
        Example:
            >>> status = client.market.status.get_market_status()
            >>> print(f"Market is: {status['market_status']}")
        """
        return self.client.get('/market/status')

