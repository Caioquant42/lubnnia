"""
User management endpoints.

Provides access to user authentication, authorization, settings, and advisor management.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class UsersAPI:
    """User management endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize users API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def authenticate(
        self,
        email: str,
        password: str,
        context: str = 'default'
    ) -> Optional[Dict]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email.
            password: User password.
            context: Authentication context ('default' or 'chart', default: 'default').
            
        Returns:
            User info object with access token, user data, and preferences.
            Returns None if authentication fails.
            
        Example:
            >>> user = client.domain.users.authenticate('user@example.com', 'password')
            >>> access_token = user['access-token']
        """
        params = {'for': context} if context != 'default' else None
        data = {'email': email, 'password': password}
        return self.client.post('/domain/users/authenticate', data=data, params=params)
    
    def authorize(self, context: str = 'default') -> Optional[Dict]:
        """
        Authorize access using access token.
        
        Args:
            context: Authentication context ('default' or 'chart', default: 'default').
            
        Returns:
            User info object with user data and preferences.
            Returns None if authorization fails.
            
        Example:
            >>> user = client.domain.users.authorize()
        """
        params = {'for': context} if context != 'default' else None
        return self.client.get('/domain/users/authorize', params=params)
    
    def get_settings(self, group: Optional[str] = None) -> Optional[Dict]:
        """
        Get user settings.
        
        Args:
            group: Settings group to filter ('admin' or 'producer').
                Can specify multiple values comma-separated.
                
        Returns:
            User settings object with preferences and configuration.
            Returns None if no data available.
            
        Example:
            >>> settings = client.domain.users.get_settings()
            >>> admin_settings = client.domain.users.get_settings('admin')
        """
        params = {'group': group} if group else None
        return self.client.get('/domain/users/settings', params=params)
    
    def update_settings(self, preferences: str) -> bool:
        """
        Update user settings.
        
        Args:
            preferences: JSON string with user preferences.
                Should include interest_rate_type, interest_rate_value, broker,
                brokerage_fee, order_amount, simulate_price_strategy, etc.
                
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> prefs = json.dumps({
            ...     "interest_rate_type": "SELIC",
            ...     "order_amount": 1000
            ... })
            >>> client.domain.users.update_settings(prefs)
        """
        data = {'preferences': preferences}
        result = self.client.post('/domain/users/settings', data=data)
        return result is None  # 204 No Content means success
    
    def update_producer_settings(
        self,
        logo: Optional[str] = None,
        color: Optional[str] = None,
        text: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update producer/publisher settings.
        
        Args:
            logo: Base64 encoded logo image (data URI format).
            color: Color code (e.g., '#FFFFFF').
            text: Description text.
            
        Returns:
            Updated producer settings object.
            Returns None if update fails.
            
        Example:
            >>> settings = client.domain.users.update_producer_settings(
            ...     color='#FF0000',
            ...     text='My description'
            ... )
        """
        data = {}
        if logo:
            data['logo'] = logo
        if color:
            data['color'] = color
        if text:
            data['text'] = text
        
        return self.client.put('/domain/users/settings/producer', data=data)
    
    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        document_type: Optional[str] = None,
        document_number: Optional[str] = None,
        phone_area_code: Optional[str] = None,
        phone_number: Optional[str] = None
    ) -> bool:
        """
        Update user data.
        
        Args:
            user_id: User ID.
            name: User name.
            document_type: Document type (e.g., 'CPF').
            document_number: Document number.
            phone_area_code: Phone area code.
            phone_number: Phone number.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.users.update_user(
            ...     12345,
            ...     name='João Silva',
            ...     phone_area_code='11',
            ...     phone_number='12345678'
            ... )
        """
        data = {}
        if name:
            data['name'] = name
        if document_type:
            data['document_type'] = document_type
        if document_number:
            data['document_number'] = document_number
        if phone_area_code:
            data['phone_area_code'] = phone_area_code
        if phone_number:
            data['phone_number'] = phone_number
        
        result = self.client.put(f'/domain/users/{user_id}', data=data)
        return result is None  # 204 No Content means success
    
    def list_advisors(self) -> Optional[List[Dict]]:
        """
        List all investment advisor users.
        
        Returns:
            List of advisor user objects.
            Returns None if no data available.
            
        Example:
            >>> advisors = client.domain.users.list_advisors()
        """
        return self.client.get('/domain/users/advisors')
    
    def reset_password(self, email: str) -> bool:
        """
        Request password reset.
        
        Sends password recovery link to user's email.
        
        Args:
            email: User email address.
            
        Returns:
            True if successful, False otherwise.
            
        Example:
            >>> client.domain.users.reset_password('user@example.com')
        """
        data = {'email': email}
        result = self.client.post('/domain/password_reset', data=data)
        return result is None  # 204 No Content means success

