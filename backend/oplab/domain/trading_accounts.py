"""
Trading account management endpoints.

Provides access to trading account operations, terms, and events.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class TradingAccountsAPI:
    """Trading account management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize trading accounts API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_trading_accounts(self) -> Optional[List[Dict]]:
        """
        List all user trading accounts.
        
        Returns:
            List of trading account objects.
            Returns None if no data available.
            
        Example:
            >>> accounts = client.domain.trading_accounts.list_trading_accounts()
        """
        return self.client.get('/domain/trading_accounts')
    
    def get_trading_account(self, account_id: int) -> Optional[Dict]:
        """
        Get trading account details.
        
        Args:
            account_id: Trading account ID.
            
        Returns:
            Trading account object.
            Returns None if not found.
            
        Example:
            >>> account = client.domain.trading_accounts.get_trading_account(9)
        """
        return self.client.get(f'/domain/trading_accounts/{account_id}')
    
    def cancel_trading_account(self, account_id: int) -> Optional[Dict]:
        """
        Cancel trading account.
        
        Args:
            account_id: Trading account ID.
            
        Returns:
            Cancelled trading account object or None if 204 No Content.
            Returns None if cancellation fails.
            
        Example:
            >>> client.domain.trading_accounts.cancel_trading_account(9)
        """
        return self.client.put(f'/domain/trading_accounts/{account_id}/cancel')
    
    def get_pending_terms(self, account_id: int) -> Optional[List[Dict]]:
        """
        List pending terms for trading account.
        
        Gets list of broker responsibility terms that user hasn't accepted yet.
        
        Args:
            account_id: Trading account ID.
            
        Returns:
            List of pending term objects.
            Returns None if no data available.
            
        Example:
            >>> terms = client.domain.trading_accounts.get_pending_terms(9)
        """
        return self.client.get(f'/domain/trading_accounts/{account_id}/pending_terms')
    
    def agree_term(
        self,
        trading_account_id: int,
        term_id: int
    ) -> Optional[Dict]:
        """
        Agree to broker term.
        
        Args:
            trading_account_id: Trading account ID.
            term_id: Term ID.
            
        Returns:
            Agreement confirmation object.
            Returns None if agreement fails.
            
        Example:
            >>> result = client.domain.trading_accounts.agree_term(9, 1)
        """
        return self.client.post(
            f'/domain/trading_accounts/{trading_account_id}/agree/{term_id}'
        )
    
    def list_events(
        self,
        trading_account_id: int
    ) -> Optional[List[Dict]]:
        """
        List trading account events.
        
        Args:
            trading_account_id: Trading account ID.
            
        Returns:
            List of event objects.
            Returns None if no data available.
            
        Example:
            >>> events = client.domain.trading_accounts.list_events(9)
        """
        return self.client.get(f'/domain/trading_accounts/{trading_account_id}/events')
    
    def get_event(
        self,
        trading_account_id: int,
        event_id: int
    ) -> Optional[Dict]:
        """
        Get trading account event details.
        
        Args:
            trading_account_id: Trading account ID.
            event_id: Event ID.
            
        Returns:
            Event object.
            Returns None if not found.
            
        Example:
            >>> event = client.domain.trading_accounts.get_event(9, 1)
        """
        return self.client.get(
            f'/domain/trading_accounts/{trading_account_id}/events/{event_id}'
        )

