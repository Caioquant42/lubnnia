"""
Notification management endpoints.

Provides access to notification CRUD operations, preferences, and bulk actions.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class NotificationsAPI:
    """Notification management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize notifications API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def list_notifications(
        self,
        page: Optional[int] = None,
        per: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        List all user notifications.
        
        Args:
            page: Page number (optional).
            per: Items per page (optional).
            
        Returns:
            List of notification objects.
            Returns None if no data available.
            
        Example:
            >>> notifications = client.domain.notifications.list_notifications(page=1, per=20)
        """
        params = {}
        if page:
            params['page'] = page
        if per:
            params['per'] = per
        
        return self.client.get('/domain/notifications', params=params)
    
    def get_notification(self, notification_id: int) -> Optional[Dict]:
        """
        Get notification details.
        
        Args:
            notification_id: Notification ID.
            
        Returns:
            Notification object.
            Returns None if not found.
            
        Example:
            >>> notification = client.domain.notifications.get_notification(100)
        """
        return self.client.get(f'/domain/notifications/{notification_id}')
    
    def update_notification(
        self,
        notification_id: int,
        ack_at: Optional[str] = None,
        read_at: Optional[str] = None,
        deleted_at: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update notification.
        
        Args:
            notification_id: Notification ID.
            ack_at: Acknowledgment timestamp (optional).
            read_at: Read timestamp (optional).
            deleted_at: Deletion timestamp (optional, null to undelete).
            
        Returns:
            Updated notification object.
            Returns None if update fails.
            
        Example:
            >>> notification = client.domain.notifications.update_notification(
            ...     100, read_at='2024-01-01T12:00:00Z'
            ... )
        """
        data = {}
        if ack_at:
            data['ack_at'] = ack_at
        if read_at:
            data['read_at'] = read_at
        if deleted_at is not None:
            data['deleted_at'] = deleted_at
        
        return self.client.put(f'/domain/notifications/{notification_id}', data=data)
    
    def delete_notification(self, notification_id: int) -> bool:
        """
        Delete notification.
        
        Args:
            notification_id: Notification ID.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.notifications.delete_notification(100)
        """
        result = self.client.delete(f'/domain/notifications/{notification_id}')
        return result is None  # 204 No Content means success
    
    def get_unread_count(self) -> Optional[Dict]:
        """
        Get count of unread notifications.
        
        Returns:
            Object with unread notifications count.
            Returns None if no data available.
            
        Example:
            >>> count = client.domain.notifications.get_unread_count()
        """
        return self.client.get('/domain/notifications/unread')
    
    def mark_all_read(self) -> bool:
        """
        Mark all notifications as read.
        
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.notifications.mark_all_read()
        """
        result = self.client.post('/domain/notifications/read_all')
        return result is None  # 204 No Content means success
    
    def delete_all(self) -> bool:
        """
        Delete all notifications.
        
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.notifications.delete_all()
        """
        result = self.client.post('/domain/notifications/delete_all')
        return result is None  # 204 No Content means success
    
    def get_preferences(self) -> Optional[List[Dict]]:
        """
        Get notification preferences.
        
        Returns:
            List of notification preference objects.
            Returns None if no data available.
            
        Example:
            >>> prefs = client.domain.notifications.get_preferences()
        """
        return self.client.get('/domain/notifications/preferences')
    
    def update_preferences(self, preferences: List[Dict]) -> bool:
        """
        Update notification preferences.
        
        Args:
            preferences: List of preference objects with notification type and enabled status.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> prefs = [{'type': 'order_filled', 'enabled': True}]
            >>> client.domain.notifications.update_preferences(prefs)
        """
        data = {'preferences': preferences}
        result = self.client.post('/domain/notifications/preferences', data=data)
        return result is None  # 204 No Content means success

