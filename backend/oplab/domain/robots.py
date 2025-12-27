"""
Robot management endpoints.

Provides access to robot CRUD operations, pause, resume, and logs.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class RobotsAPI:
    """Robot management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize robots API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_robots(
        self,
        portfolio_id: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        per: Optional[int] = None,
        status: Optional[str] = None
    ) -> Optional[List[Dict]]:
        """
        List portfolio robots.
        
        Args:
            portfolio_id: Portfolio ID.
            from_date: Start date (optional).
            to_date: End date (optional).
            page: Page number (optional).
            per: Items per page (optional).
            status: Robot status filter, comma-separated numbers (optional).
                Options: 0, 1, 2, 3, 4, 5, 6, 7, 8, 11, 12, 13, 14.
                
        Returns:
            List of robot objects.
            Returns None if no data available.
            
        Example:
            >>> robots = client.domain.robots.list_robots(12345, status='0,1')
        """
        params = {}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if page:
            params['page'] = page
        if per:
            params['per'] = per
        if status:
            params['status'] = status
        
        return self.client.get(f'/domain/portfolios/{portfolio_id}/robots', params=params)
    
    def create_robot(
        self,
        portfolio_id: int,
        trading_account_id: int,
        strategy: Dict,
        legs: List[Dict],
        spread: Optional[float] = None,
        debug: Optional[int] = None,
        mode: Optional[str] = None,
        expire_date: Optional[str] = None,
        start_time: Optional[str] = None,
        stop_time: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Create robot in portfolio.
        
        Args:
            portfolio_id: Portfolio ID.
            trading_account_id: Trading account ID.
            strategy: Strategy object with id (optional), name, underlying.
            legs: List of leg objects with symbol, target_amount, side, depth.
            spread: Spread value (optional).
            debug: Debug level (optional).
            mode: Robot mode (optional, e.g., 'secure').
            expire_date: Expiration date (optional, YYYY-MM-DD).
            start_time: Start time (optional, HH:MM).
            stop_time: Stop time (optional, HH:MM).
            
        Returns:
            Created robot object.
            Returns None if creation fails.
            
        Example:
            >>> robot = client.domain.robots.create_robot(
            ...     12345, 9,
            ...     {'name': 'Trava de alta', 'underlying': 'PETR4'},
            ...     [{'symbol': 'PETRI216', 'target_amount': 1000, 'side': 'SELL', 'depth': 1}]
            ... )
        """
        data = {
            'trading_account_id': trading_account_id,
            'strategy': strategy,
            'legs': legs
        }
        if spread is not None:
            data['spread'] = spread
        if debug is not None:
            data['debug'] = debug
        if mode:
            data['mode'] = mode
        if expire_date:
            data['expire_date'] = expire_date
        if start_time:
            data['start_time'] = start_time
        if stop_time:
            data['stop_time'] = stop_time
        
        return self.client.post(f'/domain/portfolios/{portfolio_id}/robots', data=data)
    
    def get_robot(
        self,
        portfolio_id: int,
        robot_id: int
    ) -> Optional[Dict]:
        """
        Get robot details.
        
        Args:
            portfolio_id: Portfolio ID.
            robot_id: Robot ID.
            
        Returns:
            Robot object with all robot data.
            Returns None if not found.
            
        Example:
            >>> robot = client.domain.robots.get_robot(12345, 100)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/robots/{robot_id}')
    
    def update_robot(
        self,
        portfolio_id: int,
        robot_id: int,
        spread: Optional[float] = None,
        expire_date: Optional[str] = None,
        start_time: Optional[str] = None,
        stop_time: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update robot.
        
        Only works for robots that are running, paused, or waiting for execution time.
        
        Args:
            portfolio_id: Portfolio ID.
            robot_id: Robot ID.
            spread: New spread value (optional).
            expire_date: New expiration date (optional).
            start_time: New start time (optional).
            stop_time: New stop time (optional).
            
        Returns:
            Updated robot object.
            Returns None if update fails.
            
        Example:
            >>> robot = client.domain.robots.update_robot(12345, 100, spread=200)
        """
        data = {}
        if spread is not None:
            data['spread'] = spread
        if expire_date:
            data['expire_date'] = expire_date
        if start_time:
            data['start_time'] = start_time
        if stop_time:
            data['stop_time'] = stop_time
        
        return self.client.put(f'/domain/portfolios/{portfolio_id}/robots/{robot_id}', data=data)
    
    def delete_robot(
        self,
        portfolio_id: int,
        robot_id: int
    ) -> Optional[Dict]:
        """
        Cancel robot.
        
        Only works for robots that are running, paused, or waiting for execution time.
        
        Args:
            portfolio_id: Portfolio ID.
            robot_id: Robot ID.
            
        Returns:
            Cancelled robot object or None if 200 OK.
            Returns None if cancellation fails.
            
        Example:
            >>> client.domain.robots.delete_robot(12345, 100)
        """
        return self.client.delete(f'/domain/portfolios/{portfolio_id}/robots/{robot_id}')
    
    def pause_robot(
        self,
        portfolio_id: int,
        robot_id: int
    ) -> Optional[Dict]:
        """
        Pause robot.
        
        Only works for robots that are running or waiting for execution time.
        
        Args:
            portfolio_id: Portfolio ID.
            robot_id: Robot ID.
            
        Returns:
            Paused robot object.
            Returns None if pause fails.
            
        Example:
            >>> robot = client.domain.robots.pause_robot(12345, 100)
        """
        return self.client.post(f'/domain/portfolios/{portfolio_id}/robots/{robot_id}/pause')
    
    def resume_robot(
        self,
        portfolio_id: int,
        robot_id: int
    ) -> Optional[Dict]:
        """
        Resume robot execution.
        
        Only works for robots that are paused.
        
        Args:
            portfolio_id: Portfolio ID.
            robot_id: Robot ID.
            
        Returns:
            Resumed robot object.
            Returns None if resume fails.
            
        Example:
            >>> robot = client.domain.robots.resume_robot(12345, 100)
        """
        return self.client.post(f'/domain/portfolios/{portfolio_id}/robots/{robot_id}/resume')
    
    def get_robot_log(
        self,
        portfolio_id: int,
        robot_id: int
    ) -> Optional[str]:
        """
        Get robot log file.
        
        Args:
            portfolio_id: Portfolio ID.
            robot_id: Robot ID.
            
        Returns:
            Robot log file content as string.
            Returns None if not found.
            
        Example:
            >>> log = client.domain.robots.get_robot_log(12345, 100)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/robots/{robot_id}/log')

