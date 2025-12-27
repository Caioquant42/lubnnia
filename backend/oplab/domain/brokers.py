"""
Broker management endpoints.

Provides access to broker information and sign-up.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class BrokersAPI:
    """Broker management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize brokers API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_brokers(self) -> Optional[List[Dict]]:
        """
        List all registered brokers.
        
        Returns:
            List of broker objects.
            Returns None if no data available.
            
        Example:
            >>> brokers = client.domain.brokers.list_brokers()
        """
        return self.client.get('/domain/brokers')
    
    def get_broker(self, broker_id: int) -> Optional[Dict]:
        """
        Get broker details.
        
        Args:
            broker_id: Broker ID.
            
        Returns:
            Broker object with all broker data.
            Returns None if not found.
            
        Example:
            >>> broker = client.domain.brokers.get_broker(1)
        """
        return self.client.get(f'/domain/brokers/{broker_id}')
    
    def sign_up(
        self,
        broker_id: int,
        plan_id: int,
        pin: str
    ) -> Optional[Dict]:
        """
        Sign up user to broker.
        
        Creates a trading account.
        
        Args:
            broker_id: Broker ID.
            plan_id: Plan ID.
            pin: PIN code.
            
        Returns:
            Created trading account object.
            Returns None if sign-up fails.
            
        Example:
            >>> account = client.domain.brokers.sign_up(1, 19, '2134')
        """
        data = {
            'plan_id': plan_id,
            'pin': pin
        }
        return self.client.post(f'/domain/brokers/{broker_id}/sign_up', data=data)

