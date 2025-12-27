"""
Watchlist management endpoints.

Provides access to watchlist CRUD operations and instrument management.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class WatchlistsAPI:
    """Watchlist management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize watchlists API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_watchlists(self) -> Optional[List[Dict]]:
        """
        List all user watchlists.
        
        Returns:
            List of watchlist objects.
            Returns None if no data available.
            
        Example:
            >>> watchlists = client.domain.watchlists.list_watchlists()
        """
        return self.client.get('/domain/watchlists')
    
    def create_watchlist(
        self,
        name: str,
        is_default: bool = False,
        sort: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Create watchlist.
        
        Args:
            name: Watchlist name.
            is_default: Whether this is the default watchlist (default: False).
            sort: Sort order (optional).
            
        Returns:
            Created watchlist object.
            Returns None if creation fails.
            
        Example:
            >>> watchlist = client.domain.watchlists.create_watchlist('My Watchlist')
        """
        data = {'name': name, 'is_default': is_default}
        if sort is not None:
            data['sort'] = sort
        
        return self.client.post('/domain/watchlists', data=data)
    
    def get_watchlist(self, watchlist_id: str) -> Optional[Dict]:
        """
        Get watchlist details.
        
        Args:
            watchlist_id: Watchlist ID or 'default' for default watchlist.
            
        Returns:
            Watchlist object with all watchlist data.
            Returns None if not found.
            
        Example:
            >>> watchlist = client.domain.watchlists.get_watchlist('default')
        """
        return self.client.get(f'/domain/watchlists/{watchlist_id}')
    
    def update_watchlist(
        self,
        watchlist_id: str,
        name: Optional[str] = None,
        is_default: Optional[bool] = None,
        sort: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Update watchlist.
        
        Args:
            watchlist_id: Watchlist ID or 'default' for default watchlist.
            name: New watchlist name (optional).
            is_default: Whether this is the default watchlist (optional).
            sort: New sort order (optional).
            
        Returns:
            Updated watchlist object.
            Returns None if update fails.
            
        Example:
            >>> watchlist = client.domain.watchlists.update_watchlist(1, name='Updated Name')
        """
        data = {}
        if name:
            data['name'] = name
        if is_default is not None:
            data['is_default'] = is_default
        if sort is not None:
            data['sort'] = sort
        
        return self.client.put(f'/domain/watchlists/{watchlist_id}', data=data)
    
    def delete_watchlist(self, watchlist_id: str) -> bool:
        """
        Delete watchlist.
        
        Args:
            watchlist_id: Watchlist ID or 'default' for default watchlist.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.watchlists.delete_watchlist(1)
        """
        result = self.client.delete(f'/domain/watchlists/{watchlist_id}')
        return result is None  # 204 No Content means success
    
    def add_instrument(
        self,
        watchlist_id: str,
        symbol: str,
        weight: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Add instrument to watchlist.
        
        Args:
            watchlist_id: Watchlist ID or 'default' for default watchlist.
            symbol: Instrument trading symbol.
            weight: Instrument weight (optional).
            
        Returns:
            Updated watchlist object.
            Returns None if addition fails.
            
        Example:
            >>> watchlist = client.domain.watchlists.add_instrument('default', 'PETR4', weight=10)
        """
        data = {}
        if weight is not None:
            data['weight'] = weight
        
        return self.client.post(f'/domain/watchlists/{watchlist_id}/{symbol}', data=data)
    
    def remove_instrument(
        self,
        watchlist_id: str,
        symbol: str
    ) -> bool:
        """
        Remove instrument from watchlist.
        
        Args:
            watchlist_id: Watchlist ID or 'default' for default watchlist.
            symbol: Instrument trading symbol.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.watchlists.remove_instrument('default', 'PETR4')
        """
        result = self.client.delete(f'/domain/watchlists/{watchlist_id}/{symbol}')
        return result is None  # 204 No Content means success

