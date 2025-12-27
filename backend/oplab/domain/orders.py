"""
Order management endpoints.

Provides access to order CRUD operations, execution, export, and position orders.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class OrdersAPI:
    """Order management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize orders API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_portfolio_orders(
        self,
        portfolio_id: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        per: Optional[int] = None,
        ticker: Optional[str] = None,
        origin: Optional[str] = None,
        status: Optional[str] = None,
        order_type: Optional[str] = None,
        side: Optional[str] = None,
        show_position: bool = True
    ) -> Optional[List[Dict]]:
        """
        List portfolio orders.
        
        Args:
            portfolio_id: Portfolio ID.
            from_date: Start date (optional).
            to_date: End date (optional).
            page: Page number (optional).
            per: Items per page (optional).
            ticker: Asset code filter, can be partial (optional).
            origin: Order origin filter ('simulator', 'order_ticket', 'robot'), comma-separated (optional).
            status: Order status filter, comma-separated (optional).
            order_type: Order type filter ('manual', 'market', 'limit', 'stop_limit'), comma-separated (optional).
            side: Order side filter ('SELL', 'BUY'), comma-separated (optional).
            show_position: Whether to include position information (default: True).
            
        Returns:
            List of order objects.
            Returns None if no data available.
            
        Example:
            >>> orders = client.domain.orders.list_portfolio_orders(12345, status='pending')
        """
        params = {'show_position': show_position}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if page:
            params['page'] = page
        if per:
            params['per'] = per
        if ticker:
            params['ticker'] = ticker
        if origin:
            params['origin'] = origin
        if status:
            params['status'] = status
        if order_type:
            params['order_type'] = order_type
        if side:
            params['side'] = side
        
        return self.client.get(f'/domain/portfolios/{portfolio_id}/orders', params=params)
    
    def create_portfolio_order(
        self,
        portfolio_id: int,
        symbol: str,
        price: float,
        amount: int,
        side: str,
        order_type: str,
        origin: str = 'order_ticket',
        time_in_force: str = 'day',
        brokerage: float = 0,
        status: str = 'pending',
        trading_account_id: Optional[int] = None,
        created_at: Optional[str] = None,
        expires_at: Optional[str] = None,
        trigger_price: Optional[float] = None,
        executed_at: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Create order in portfolio.
        
        Args:
            portfolio_id: Portfolio ID.
            symbol: Asset symbol.
            price: Order price.
            amount: Order amount.
            side: Order side ('BUY' or 'SELL').
            order_type: Order type ('manual', 'market', 'limit', 'stop_limit').
            origin: Order origin (default: 'order_ticket').
            time_in_force: Time in force (default: 'day').
            brokerage: Brokerage fee (default: 0).
            status: Order status (default: 'pending').
            trading_account_id: Trading account ID (optional).
            created_at: Creation timestamp (optional).
            expires_at: Expiration timestamp (optional).
            trigger_price: Trigger price for stop orders (optional).
            executed_at: Execution timestamp (optional).
            tags: List of tags (optional).
            
        Returns:
            Created order object.
            Returns None if creation fails.
            
        Example:
            >>> order = client.domain.orders.create_portfolio_order(
            ...     12345, 'PETR4', 28.0, 100, 'BUY', 'market'
            ... )
        """
        data = {
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'side': side,
            'order_type': order_type,
            'origin': origin,
            'time_in_force': time_in_force,
            'brokerage': brokerage,
            'status': status
        }
        if trading_account_id:
            data['trading_account_id'] = trading_account_id
        if created_at:
            data['created_at'] = created_at
        if expires_at:
            data['expires_at'] = expires_at
        if trigger_price:
            data['trigger_price'] = trigger_price
        if executed_at:
            data['executed_at'] = executed_at
        if tags:
            data['tags'] = tags
        
        return self.client.post(f'/domain/portfolios/{portfolio_id}/orders', data=data)
    
    def get_portfolio_order(
        self,
        portfolio_id: int,
        order_id: int
    ) -> Optional[Dict]:
        """
        Get portfolio order details.
        
        Args:
            portfolio_id: Portfolio ID.
            order_id: Order ID.
            
        Returns:
            Order object.
            Returns None if not found.
            
        Example:
            >>> order = client.domain.orders.get_portfolio_order(12345, 100)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/orders/{order_id}')
    
    def update_portfolio_order(
        self,
        portfolio_id: int,
        order_id: int,
        price: Optional[float] = None,
        amount: Optional[int] = None,
        side: Optional[str] = None,
        time_in_force: Optional[str] = None,
        trigger_price: Optional[float] = None,
        expires_at: Optional[str] = None,
        executed_at: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update portfolio order.
        
        Args:
            portfolio_id: Portfolio ID.
            order_id: Order ID.
            price: New price (optional).
            amount: New amount (optional).
            side: New side (optional).
            time_in_force: New time in force (optional).
            trigger_price: New trigger price (optional).
            expires_at: New expiration timestamp (optional).
            executed_at: New execution timestamp (optional).
            
        Returns:
            Updated order object.
            Returns None if update fails.
            
        Example:
            >>> order = client.domain.orders.update_portfolio_order(12345, 100, price=29.0)
        """
        data = {}
        if price is not None:
            data['price'] = price
        if amount is not None:
            data['amount'] = amount
        if side:
            data['side'] = side
        if time_in_force:
            data['time_in_force'] = time_in_force
        if trigger_price is not None:
            data['trigger_price'] = trigger_price
        if expires_at:
            data['expires_at'] = expires_at
        if executed_at:
            data['executed_at'] = executed_at
        
        return self.client.put(f'/domain/portfolios/{portfolio_id}/orders/{order_id}', data=data)
    
    def delete_portfolio_order(
        self,
        portfolio_id: int,
        order_id: int
    ) -> Optional[Dict]:
        """
        Cancel portfolio order.
        
        Args:
            portfolio_id: Portfolio ID.
            order_id: Order ID.
            
        Returns:
            Cancelled order object or None if 200 OK.
            Returns None if cancellation fails.
            
        Example:
            >>> client.domain.orders.delete_portfolio_order(12345, 100)
        """
        return self.client.delete(f'/domain/portfolios/{portfolio_id}/orders/{order_id}')
    
    def execute_portfolio_order(
        self,
        portfolio_id: int,
        order_id: int
    ) -> Optional[Dict]:
        """
        Execute portfolio order.
        
        Order must be type 'manual' and status 'pending'.
        
        Args:
            portfolio_id: Portfolio ID.
            order_id: Order ID.
            
        Returns:
            Executed order object.
            Returns None if execution fails.
            
        Example:
            >>> order = client.domain.orders.execute_portfolio_order(12345, 100)
        """
        return self.client.post(f'/domain/portfolios/{portfolio_id}/orders/{order_id}/execute')
    
    def get_pending_orders_count(
        self,
        portfolio_id: int
    ) -> Optional[Dict]:
        """
        Get count of pending orders.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            Object with pending orders count.
            Returns None if no data available.
            
        Example:
            >>> count = client.domain.orders.get_pending_orders_count(12345)
        """
        return self.client.get(f'/domain/portfolios/{portfolio_id}/orders/pending')
    
    def export_portfolio_orders(
        self,
        portfolio_id: int
    ) -> bool:
        """
        Export portfolio orders to CSV.
        
        Starts background process. Notification sent when complete.
        
        Args:
            portfolio_id: Portfolio ID.
            
        Returns:
            True if export started successfully, False otherwise.
            
        Example:
            >>> client.domain.orders.export_portfolio_orders(12345)
        """
        result = self.client.get(f'/domain/portfolios/{portfolio_id}/orders/export')
        return result is None  # 202 Accepted means success
    
    def list_position_orders(
        self,
        portfolio_id: int,
        position_id: int,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        page: Optional[int] = None,
        per: Optional[int] = None,
        ticker: Optional[str] = None,
        origin: Optional[str] = None,
        status: Optional[str] = None,
        order_type: Optional[str] = None,
        side: Optional[str] = None,
        show_position: bool = True
    ) -> Optional[List[Dict]]:
        """
        List position orders.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            from_date: Start date (optional).
            to_date: End date (optional).
            page: Page number (optional).
            per: Items per page (optional).
            ticker: Asset code filter (optional).
            origin: Order origin filter, comma-separated (optional).
            status: Order status filter, comma-separated (optional).
            order_type: Order type filter, comma-separated (optional).
            side: Order side filter, comma-separated (optional).
            show_position: Whether to include position information (default: True).
            
        Returns:
            List of order objects.
            Returns None if no data available.
            
        Example:
            >>> orders = client.domain.orders.list_position_orders(12345, 100)
        """
        params = {'show_position': show_position}
        if from_date:
            params['from'] = from_date
        if to_date:
            params['to'] = to_date
        if page:
            params['page'] = page
        if per:
            params['per'] = per
        if ticker:
            params['ticker'] = ticker
        if origin:
            params['origin'] = origin
        if status:
            params['status'] = status
        if order_type:
            params['order_type'] = order_type
        if side:
            params['side'] = side
        
        return self.client.get(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/orders',
            params=params
        )
    
    def create_position_order(
        self,
        portfolio_id: int,
        position_id: int,
        symbol: str,
        price: float,
        amount: int,
        side: str,
        order_type: str,
        origin: str = 'order_ticket',
        time_in_force: str = 'day',
        brokerage: float = 0,
        status: str = 'pending',
        trading_account_id: Optional[int] = None,
        created_at: Optional[str] = None,
        expires_at: Optional[str] = None,
        trigger_price: Optional[float] = None,
        executed_at: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> Optional[Dict]:
        """
        Create order in position.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            symbol: Asset symbol.
            price: Order price.
            amount: Order amount.
            side: Order side ('BUY' or 'SELL').
            order_type: Order type ('manual', 'market', 'limit', 'stop_limit').
            origin: Order origin (default: 'order_ticket').
            time_in_force: Time in force (default: 'day').
            brokerage: Brokerage fee (default: 0).
            status: Order status (default: 'pending').
            trading_account_id: Trading account ID (optional).
            created_at: Creation timestamp (optional).
            expires_at: Expiration timestamp (optional).
            trigger_price: Trigger price (optional).
            executed_at: Execution timestamp (optional).
            tags: List of tags (optional).
            
        Returns:
            Created order object.
            Returns None if creation fails.
            
        Example:
            >>> order = client.domain.orders.create_position_order(
            ...     12345, 100, 'PETR4', 28.0, 100, 'BUY', 'market'
            ... )
        """
        data = {
            'symbol': symbol,
            'price': price,
            'amount': amount,
            'side': side,
            'order_type': order_type,
            'origin': origin,
            'time_in_force': time_in_force,
            'brokerage': brokerage,
            'status': status
        }
        if trading_account_id:
            data['trading_account_id'] = trading_account_id
        if created_at:
            data['created_at'] = created_at
        if expires_at:
            data['expires_at'] = expires_at
        if trigger_price:
            data['trigger_price'] = trigger_price
        if executed_at:
            data['executed_at'] = executed_at
        if tags:
            data['tags'] = tags
        
        return self.client.post(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/orders',
            data=data
        )
    
    def get_position_order(
        self,
        portfolio_id: int,
        position_id: int,
        order_id: int
    ) -> Optional[Dict]:
        """
        Get position order details.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            order_id: Order ID.
            
        Returns:
            Order object.
            Returns None if not found.
            
        Example:
            >>> order = client.domain.orders.get_position_order(12345, 100, 200)
        """
        return self.client.get(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{order_id}'
        )
    
    def update_position_order(
        self,
        portfolio_id: int,
        position_id: int,
        order_id: int,
        price: Optional[float] = None,
        amount: Optional[int] = None,
        side: Optional[str] = None,
        time_in_force: Optional[str] = None,
        trigger_price: Optional[float] = None,
        expires_at: Optional[str] = None,
        executed_at: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update position order.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            order_id: Order ID.
            price: New price (optional).
            amount: New amount (optional).
            side: New side (optional).
            time_in_force: New time in force (optional).
            trigger_price: New trigger price (optional).
            expires_at: New expiration timestamp (optional).
            executed_at: New execution timestamp (optional).
            
        Returns:
            Updated order object.
            Returns None if update fails.
            
        Example:
            >>> order = client.domain.orders.update_position_order(12345, 100, 200, price=29.0)
        """
        data = {}
        if price is not None:
            data['price'] = price
        if amount is not None:
            data['amount'] = amount
        if side:
            data['side'] = side
        if time_in_force:
            data['time_in_force'] = time_in_force
        if trigger_price is not None:
            data['trigger_price'] = trigger_price
        if expires_at:
            data['expires_at'] = expires_at
        if executed_at:
            data['executed_at'] = executed_at
        
        return self.client.put(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{order_id}',
            data=data
        )
    
    def delete_position_order(
        self,
        portfolio_id: int,
        position_id: int,
        order_id: int
    ) -> Optional[Dict]:
        """
        Cancel position order.
        
        Args:
            portfolio_id: Portfolio ID.
            position_id: Position ID.
            order_id: Order ID.
            
        Returns:
            Cancelled order object or None if 200 OK.
            Returns None if cancellation fails.
            
        Example:
            >>> client.domain.orders.delete_position_order(12345, 100, 200)
        """
        return self.client.delete(
            f'/domain/portfolios/{portfolio_id}/positions/{position_id}/orders/{order_id}'
        )

