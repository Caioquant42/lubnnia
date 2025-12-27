"""
Portfolio management endpoints.

Provides access to portfolio CRUD operations, returns, tags, synchronization, and sharing.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class PortfoliosAPI:
    """Portfolio management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize portfolios API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_portfolios(self) -> Optional[List[Dict]]:
        """
        List all user portfolios.
        
        Returns:
            List of portfolio objects.
            Returns None if no data available.
            
        Example:
            >>> portfolios = client.domain.portfolios.list_portfolios()
        """
        return self.client.get('/domain/portfolios')
    
    def create_portfolio(self, name: str, active: bool = True) -> Optional[Dict]:
        """
        Create a new empty portfolio.
        
        Args:
            name: Portfolio name.
            active: Whether portfolio is active (default: True).
            
        Returns:
            Created portfolio object.
            Returns None if creation fails.
            
        Example:
            >>> portfolio = client.domain.portfolios.create_portfolio('My Portfolio')
        """
        data = {'name': name, 'active': active}
        return self.client.post('/domain/portfolios', data=data)
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Dict]:
        """
        Get portfolio details.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            Portfolio object with all portfolio data.
            Returns None if not found.
            
        Example:
            >>> portfolio = client.domain.portfolios.get_portfolio(12345)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}')
    
    def update_portfolio(
        self,
        portfolio_id: int,
        name: Optional[str] = None,
        active: Optional[bool] = None
    ) -> Optional[Dict]:
        """
        Update portfolio.
        
        Args:
            portfolio_id: Portfolio ID.
            name: New portfolio name.
            active: Whether portfolio is active.
            
        Returns:
            Updated portfolio object.
            Returns None if update fails.
            
        Example:
            >>> portfolio = client.domain.portfolios.update_portfolio(12345, name='Updated Name')
        """
        data = {}
        if name:
            data['name'] = name
        if active is not None:
            data['active'] = active
        
        return self.client.put(f'/domain/portfolios/{portfolio_id}', data=data)
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """
        Delete portfolio.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.portfolios.delete_portfolio(12345)
        """
        result = self.client.delete(f'/domain/portfolios/{portfolio_id}')
        return result is None  # 204 No Content means success
    
    def set_default_portfolio(self, portfolio_id: int) -> bool:
        """
        Set portfolio as default.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.portfolios.set_default_portfolio(12345)
        """
        result = self.client.put(f'/domain/portfolios/{portfolio_id}/default')
        return result is None  # 204 No Content means success
    
    def get_portfolio_returns(
        self,
        portfolio_id: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        Get portfolio returns data.
        
        Args:
            portfolio_id: Portfolio ID.
            from_date: Start date (optional).
            to_date: End date (optional).
            
        Returns:
            List of portfolio return data objects.
            Returns None if no data available.
            
        Example:
            >>> returns = client.domain.portfolios.get_portfolio_returns(12345, '2024-01-01', '2024-12-31')
        """
        params = {}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        
        return self.client.get(f'/domain/portfolios/{portfolio_id}/returns', params=params)
    
    def get_portfolio_tags(self, portfolio_id: int) -> Optional[List[str]]:
        """
        Get portfolio tags.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            List of tag strings associated with the portfolio.
            Returns None if no data available.
            
        Example:
            >>> tags = client.domain.portfolios.get_portfolio_tags(12345)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/tags')
    
    def synchronize_portfolio(
        self,
        portfolio_id: int,
        sync_strategy: str
    ) -> Optional[Dict]:
        """
        Enable portfolio synchronization.
        
        Args:
            portfolio_id: Portfolio ID.
            sync_strategy: Synchronization strategy (e.g., 'b3').
            
        Returns:
            Synchronization configuration object.
            Returns None if synchronization fails.
            
        Example:
            >>> sync = client.domain.portfolios.synchronize_portfolio(12345, 'b3')
        """
        data = {'sync_strategy': sync_strategy}
        return self.client.put(f'/domain/portfolios/{portfolio_id}/synchronize', data=data)
    
    def desynchronize_portfolio(self, portfolio_id: int) -> bool:
        """
        Disable portfolio synchronization.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.portfolios.desynchronize_portfolio(12345)
        """
        result = self.client.delete(f'/domain/portfolios/{portfolio_id}/synchronize')
        return result is None  # 204 No Content means success
    
    def list_shared_portfolios(self, portfolio_id: int) -> Optional[List[Dict]]:
        """
        List portfolio shares.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            List of shared portfolio objects with sharing information.
            Returns None if no data available.
            
        Example:
            >>> shares = client.domain.portfolios.list_shared_portfolios(12345)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/shared_portfolios')
    
    def create_shared_portfolio(
        self,
        portfolio_id: int,
        advisor_id: int,
        access_level: str
    ) -> Optional[Dict]:
        """
        Create portfolio share.
        
        Args:
            portfolio_id: Portfolio ID.
            advisor_id: Advisor user ID.
            access_level: Access level ('read' or 'write').
            
        Returns:
            Created shared portfolio object.
            Returns None if creation fails.
            
        Example:
            >>> share = client.domain.portfolios.create_shared_portfolio(12345, 67890, 'read')
        """
        data = {
            'advisor_id': advisor_id,
            'access_level': access_level
        }
        return self.client.post(f'/domain/portfolios/{portfolio_id}/shared_portfolios', data=data)
    
    def get_shared_portfolio(
        self,
        portfolio_id: int,
        share_id: int
    ) -> Optional[Dict]:
        """
        Get shared portfolio details.
        
        Args:
            portfolio_id: Portfolio ID.
            share_id: Shared portfolio ID.
            
        Returns:
            Shared portfolio object.
            Returns None if not found.
            
        Example:
            >>> share = client.domain.portfolios.get_shared_portfolio(12345, 1)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/shared_portfolios/{share_id}')
    
    def update_shared_portfolio(
        self,
        portfolio_id: int,
        share_id: int,
        access_level: str
    ) -> Optional[Dict]:
        """
        Update portfolio share access level.
        
        Args:
            portfolio_id: Portfolio ID.
            share_id: Shared portfolio ID.
            access_level: New access level ('read' or 'write').
            
        Returns:
            Updated shared portfolio object.
            Returns None if update fails.
            
        Example:
            >>> share = client.domain.portfolios.update_shared_portfolio(12345, 1, 'write')
        """
        data = {'access_level': access_level}
        return self.client.put(
            f'/domain/portfolios/{portfolio_id}/shared_portfolios/{share_id}',
            data=data
        )
    
    def delete_shared_portfolio(self, portfolio_id: int, share_id: int) -> bool:
        """
        Disable portfolio share.
        
        Args:
            portfolio_id: Portfolio ID.
            share_id: Shared portfolio ID.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.portfolios.delete_shared_portfolio(12345, 1)
        """
        result = self.client.delete(
            f'/domain/portfolios/{portfolio_id}/shared_portfolios/{share_id}'
        )
        return result is None  # 204 No Content means success

