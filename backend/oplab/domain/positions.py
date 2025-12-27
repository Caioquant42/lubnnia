"""
Position management endpoints.

Provides access to position CRUD operations, tagging, committing, and closing.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class PositionsAPI:
    """Position management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize positions API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_positions(
        self,
        portfolio_id: int,
        status: str = 'open'
    ) -> Optional[List[Dict]]:
        """
        List portfolio positions.
        
        Args:
            portfolio_id: Portfolio ID.
            status: Position status ('open', 'closed', or 'all', default: 'open').
            
        Returns:
            List of position objects.
            Returns None if no data available.
            
        Example:
            >>> positions = client.domain.positions.list_positions(12345, status='all')
        """
        params = {'status': status} if status != 'open' else None
        return self.client.get(
            f'/domain/portfolios/{portfolio_id}/positions',
            params=params
        )
    
    def get_position(
        self,
        portfolio_id: int,
        position_id: int
    ) -> Optional[Dict]:
        """
        Get position details.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            
        Returns:
            Position object with all position data.
            Returns None if not found.
            
        Example:
            >>> position = client.domain.positions.get_position(12345, 100)
        """
        return self.client.get(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}'
        )
    
    def update_position(
        self,
        portfolio_id: int,
        position_id: int,
        name: Optional[str] = None,
        positive_scenario_probability: Optional[int] = None,
        strategy_id: Optional[int] = None,
        strategy_name: Optional[str] = None,
        orders: Optional[List[int]] = None
    ) -> Optional[Dict]:
        """
        Update position.
        
        Can move position to another strategy (new or existing).
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            name: Position name.
            positive_scenario_probability: Positive scenario probability (0-100).
            strategy_id: Strategy ID to move position to.
            strategy_name: New strategy name (if creating new strategy).
            orders: List of order IDs.
            
        Returns:
            Updated position object.
            Returns None if update fails.
            
        Example:
            >>> position = client.domain.positions.update_position(
            ...     12345, 100,
            ...     name='Updated Position',
            ...     strategy_id=5
            ... )
        """
        data = {}
        if name:
            data['name'] = name
        if positive_scenario_probability is not None:
            data['positive_scenario_probability'] = positive_scenario_probability
        if strategy_id:
            data['strategy_id'] = strategy_id
        if strategy_name:
            data['strategy_name'] = strategy_name
        if orders:
            data['orders'] = orders
        
        return self.client.put(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}',
            data=data
        )
    
    def delete_position(
        self,
        portfolio_id: int,
        position_id: int
    ) -> bool:
        """
        Delete position.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.positions.delete_position(12345, 100)
        """
        result = self.client.delete(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}'
        )
        return result is None  # 204 No Content means success
    
    def tag_position(
        self,
        portfolio_id: int,
        position_id: int,
        tag: str
    ) -> bool:
        """
        Add tag to position.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            tag: Tag to add.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.positions.tag_position(12345, 100, 'important')
        """
        result = self.client.put(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/tag/{tag}'
        )
        return result is None  # 204 No Content means success
    
    def untag_position(
        self,
        portfolio_id: int,
        position_id: int,
        tag: str
    ) -> bool:
        """
        Remove tag from position.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            tag: Tag to remove.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.positions.untag_position(12345, 100, 'important')
        """
        result = self.client.put(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/untag/{tag}'
        )
        return result is None  # 204 No Content means success
    
    def commit_position(
        self,
        portfolio_id: int,
        position_id: int
    ) -> Optional[Dict]:
        """
        Commit (consolidate) a simulated position.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            
        Returns:
            Committed position object.
            Returns None if commit fails.
            
        Example:
            >>> position = client.domain.positions.commit_position(12345, 100)
        """
        return self.client.put(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/commit'
        )
    
    def close_position(
        self,
        portfolio_id: int,
        position_id: int,
        exercise: bool = False
    ) -> Optional[Dict]:
        """
        Close position.
        
        Changes position status to closed by sending a counter-order.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            exercise: Whether to exercise options (default: False).
            
        Returns:
            Closed position object or None if 204 No Content.
            Returns None if close fails.
            
        Example:
            >>> position = client.domain.positions.close_position(12345, 100, exercise=True)
        """
        data = {'exercise': exercise}
        return self.client.put(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/close',
            data=data
        )

