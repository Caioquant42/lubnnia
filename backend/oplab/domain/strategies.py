"""
Strategy management endpoints.

Provides access to strategy CRUD operations, renaming, committing, and closing.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class StrategiesAPI:
    """Strategy management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize strategies API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_strategies(
        self,
        portfolio_id: int,
        status: str = 'open'
    ) -> Optional[List[Dict]]:
        """
        List portfolio strategies.
        
        Args:
            portfolio_id: Portfolio ID.
            status: Strategy position status ('open' or 'all', default: 'open').
            
        Returns:
            List of strategy objects.
            Returns None if no data available.
            
        Example:
            >>> strategies = client.domain.strategies.list_strategies(12345, status='all')
        """
        params = {'status': status} if status != 'open' else None
        return self.client.get(f'/domain/portfolios/{portfolio_id}/strategies', params=params)
    
    def create_strategy(
        self,
        portfolio_id: int,
        name: str,
        underlying: str,
        positions: List[Dict],
        origin: str = 'order_ticket',
        published_at: Optional[str] = None,
        expired_at: Optional[str] = None,
        short_description: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create strategy in portfolio.
        
        Args:
            portfolio_id: Portfolio ID.
            name: Strategy name.
            underlying: Underlying asset symbol.
            positions: List of position objects with symbol, amount, side, price.
            origin: Strategy origin (default: 'order_ticket').
            published_at: Publication date (optional).
            expired_at: Expiration date (optional).
            short_description: Short description (optional).
            description: Full description (optional).
            
        Returns:
            Created strategy object.
            Returns None if creation fails.
            
        Example:
            >>> strategy = client.domain.strategies.create_strategy(
            ...     12345, 'Covered Call', 'PETR4',
            ...     [{'symbol': 'PETR4', 'amount': 100, 'side': 'BUY', 'price': 28.0}]
            ... )
        """
        data = {
            'name': name,
            'underlying': underlying,
            'origin': origin,
            'positions': positions
        }
        if published_at:
            data['published_at'] = published_at
        if expired_at:
            data['expired_at'] = expired_at
        if short_description:
            data['short_description'] = short_description
        if description:
            data['description'] = description
        
        return self.client.post(f'/domain/portfolios/{portfolio_id}/strategies', data=data)
    
    def get_strategy(
        self,
        portfolio_id: int,
        strategy_id: int
    ) -> Optional[Dict]:
        """
        Get strategy details.
        
        Args:
            portfolio_id: Portfolio ID.
            strategy_id: Strategy ID.
            
        Returns:
            Strategy object with all strategy data.
            Returns None if not found.
            
        Example:
            >>> strategy = client.domain.strategies.get_strategy(12345, 100)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/strategies/{strategy_id}')
    
    def delete_strategy(
        self,
        portfolio_id: int,
        strategy_id: int
    ) -> bool:
        """
        Delete strategy.
        
        Args:
            portfolio_id: Portfolio ID.
            strategy_id: Strategy ID.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.strategies.delete_strategy(12345, 100)
        """
        result = self.client.delete(f'/domain/portfolios/{portfolio_id}/strategies/{strategy_id}')
        return result is None  # 204 No Content means success
    
    def rename_strategy(
        self,
        portfolio_id: int,
        strategy_id: int,
        name: str
    ) -> Optional[Dict]:
        """
        Rename strategy.
        
        Args:
            portfolio_id: Portfolio ID.
            strategy_id: Strategy ID.
            name: New strategy name.
            
        Returns:
            Renamed strategy object.
            Returns None if rename fails.
            
        Example:
            >>> strategy = client.domain.strategies.rename_strategy(12345, 100, 'New Name')
        """
        data = {'name': name}
        return self.client.put(f'/domain/portfolios/{portfolio_id}/strategies/{strategy_id}/rename', data=data)
    
    def commit_strategy(
        self,
        portfolio_id: int,
        strategy_id: int
    ) -> Optional[List[Dict]]:
        """
        Commit (consolidate) strategy.
        
        Args:
            portfolio_id: Portfolio ID.
            strategy_id: Strategy ID.
            
        Returns:
            List of consolidated position objects.
            Returns None if commit fails.
            
        Example:
            >>> positions = client.domain.strategies.commit_strategy(12345, 100)
        """
        return self.client.put(f'/domain/portfolios/{portfolio_id}/strategies/{strategy_id}/commit')
    
    def close_strategy(
        self,
        portfolio_id: int,
        strategy_id: int
    ) -> Optional[Dict]:
        """
        Close strategy positions.
        
        Args:
            portfolio_id: Portfolio ID.
            strategy_id: Strategy ID.
            
        Returns:
            Closed strategy object.
            Returns None if close fails.
            
        Example:
            >>> strategy = client.domain.strategies.close_strategy(12345, 100)
        """
        return self.client.put(f'/domain/portfolios/{portfolio_id}/strategies/{strategy_id}/close')

