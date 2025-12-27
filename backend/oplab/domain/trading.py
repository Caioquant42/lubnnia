"""
Trading utility endpoints.

Provides access to trading-related utilities like business days calculation.
"""
from typing import Dict, Optional
from ..client import OPLABClient


class TradingAPI:
    """Trading utility endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize trading API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_business_days(self, until: str) -> Optional[Dict]:
        """
        Calculate business days until a date.
        
        Args:
            until: Reference date (YYYY-MM-DD format).
            
        Returns:
            Object with business days count until the specified date.
            Returns None if no data available.
            
        Example:
            >>> result = client.domain.trading.get_business_days('2024-12-31')
            >>> print(f"Business days: {result['business_days']}")
        """
        return self.client.get(f'/domain/trading/business_days/{until}')

