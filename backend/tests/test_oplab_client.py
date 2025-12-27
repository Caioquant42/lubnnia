"""
Test suite for OPLAB API Client

Tests client initialization, API module attachment, and API calls.
Uses mocking to avoid real API calls during testing.
"""
import os
import sys
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oplab import create_client, OPLABClient
from oplab.exceptions import (
    OPLABUnauthorizedError,
    OPLABNotFoundError,
    OPLABException,
)


class TestOPLABClientInitialization:
    """Test client initialization"""
    
    def test_client_init_with_token(self):
        """Test client initialization with explicit token"""
        client = OPLABClient(access_token="test_token_123")
        assert client.access_token == "test_token_123"
        assert client.headers["Access-Token"] == "test_token_123"
        assert client.BASE_URL == "https://api.oplab.com.br/v3"
    
    @patch.dict(os.environ, {"OPLAB_ACCESS_TOKEN": "env_token_456"})
    def test_client_init_from_env(self):
        """Test client initialization from environment variable"""
        client = OPLABClient()
        assert client.access_token == "env_token_456"
        assert client.headers["Access-Token"] == "env_token_456"
    
    @patch.dict(os.environ, {}, clear=True)
    def test_client_init_no_token_raises_error(self):
        """Test that client raises error when no token is provided"""
        with pytest.raises(ValueError, match="OPLAB_ACCESS_TOKEN must be provided"):
            OPLABClient()
    
    def test_create_client_factory(self):
        """Test create_client factory function"""
        client = create_client(access_token="factory_token_789")
        assert client.access_token == "factory_token_789"
        # Check that APIs are attached
        assert hasattr(client, "market")
        assert hasattr(client, "domain")
        assert hasattr(client.market, "stocks")
        assert hasattr(client.market, "options")
        assert hasattr(client.market, "interest_rates")


class TestOPLABClientAPIModules:
    """Test API module attachment"""
    
    def test_market_apis_attached(self):
        """Test that all market APIs are attached"""
        client = create_client(access_token="test_token")
        
        # Market APIs
        assert hasattr(client.market, "interest_rates")
        assert hasattr(client.market, "options")
        assert hasattr(client.market, "stocks")
        assert hasattr(client.market, "instruments")
        assert hasattr(client.market, "quote")
        assert hasattr(client.market, "historical")
        assert hasattr(client.market, "statistics")
        assert hasattr(client.market, "companies")
        assert hasattr(client.market, "exchanges")
        assert hasattr(client.market, "status")
    
    def test_domain_apis_attached(self):
        """Test that all domain APIs are attached"""
        client = create_client(access_token="test_token")
        
        # Domain APIs
        assert hasattr(client.domain, "users")
        assert hasattr(client.domain, "portfolios")
        assert hasattr(client.domain, "positions")
        assert hasattr(client.domain, "orders")
        assert hasattr(client.domain, "strategies")
        assert hasattr(client.domain, "robots")
        assert hasattr(client.domain, "watchlists")
        assert hasattr(client.domain, "notifications")
        assert hasattr(client.domain, "brokers")
        assert hasattr(client.domain, "trading_accounts")
        assert hasattr(client.domain, "trading")


class TestOPLABClientHTTPMethods:
    """Test HTTP request methods"""
    
    @patch("oplab.client.requests.request")
    def test_get_request_success(self, mock_request):
        """Test successful GET request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response
        
        client = OPLABClient(access_token="test_token")
        result = client.get("/test/endpoint")
        
        assert result == {"data": "test"}
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "GET"
        assert call_args[1]["url"] == "https://api.oplab.com.br/v3/test/endpoint"
        assert call_args[1]["headers"]["Access-Token"] == "test_token"
    
    @patch("oplab.client.requests.request")
    def test_post_request_success(self, mock_request):
        """Test successful POST request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 123, "created": True}
        mock_request.return_value = mock_response
        
        client = OPLABClient(access_token="test_token")
        data = {"name": "Test"}
        result = client.post("/test/endpoint", data=data)
        
        assert result == {"id": 123, "created": True}
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["json"] == data
    
    @patch("oplab.client.requests.request")
    def test_put_request_success(self, mock_request):
        """Test successful PUT request"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"updated": True}
        mock_request.return_value = mock_response
        
        client = OPLABClient(access_token="test_token")
        data = {"name": "Updated"}
        result = client.put("/test/endpoint", data=data)
        
        assert result == {"updated": True}
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "PUT"
    
    @patch("oplab.client.requests.request")
    def test_delete_request_success(self, mock_request):
        """Test successful DELETE request"""
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.content = b""
        mock_request.return_value = mock_response
        
        client = OPLABClient(access_token="test_token")
        result = client.delete("/test/endpoint")
        
        assert result is None  # 204 No Content
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "DELETE"
    
    @patch("oplab.client.requests.request")
    def test_request_with_params(self, mock_request):
        """Test request with query parameters"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response
        
        client = OPLABClient(access_token="test_token")
        params = {"limit": 10, "sort": "asc"}
        result = client.get("/test/endpoint", params=params)
        
        assert result == {"data": "test"}
        call_args = mock_request.call_args
        assert call_args[1]["params"] == params


class TestOPLABClientErrorHandling:
    """Test error handling"""
    
    @patch("oplab.client.requests.request")
    def test_unauthorized_error(self, mock_request):
        """Test 401 Unauthorized error"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response
        
        client = OPLABClient(access_token="invalid_token")
        
        with pytest.raises(OPLABUnauthorizedError, match="Invalid access token"):
            client.get("/test/endpoint")
    
    @patch("oplab.client.requests.request")
    def test_not_found_error(self, mock_request):
        """Test 404 Not Found error"""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        
        client = OPLABClient(access_token="test_token")
        
        with pytest.raises(OPLABNotFoundError, match="Not Found"):
            client.get("/test/nonexistent")
    
    @patch("oplab.client.requests.request")
    def test_retry_on_network_error(self, mock_request):
        """Test retry logic on network errors"""
        import requests
        
        # First two calls fail, third succeeds
        mock_request.side_effect = [
            requests.exceptions.ConnectionError("Connection failed"),
            requests.exceptions.ConnectionError("Connection failed"),
            Mock(status_code=200, json=lambda: {"data": "success"})
        ]
        
        client = OPLABClient(access_token="test_token")
        result = client.get("/test/endpoint", max_retries=3, delay=0.1)
        
        assert result == {"data": "success"}
        assert mock_request.call_count == 3
    
    @patch("oplab.client.requests.request")
    def test_max_retries_exceeded(self, mock_request):
        """Test that exception is raised after max retries"""
        import requests
        
        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")
        
        client = OPLABClient(access_token="test_token")
        
        with pytest.raises(OPLABException, match="Request failed after"):
            client.get("/test/endpoint", max_retries=2, delay=0.1)
        
        assert mock_request.call_count == 2


class TestOPLABClientMarketAPIs:
    """Test market API methods"""
    
    @patch("oplab.client.requests.request")
    def test_get_interest_rate(self, mock_request):
        """Test getting interest rate"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "uid": "SELIC",
            "name": "SELIC",
            "value": 14.15,
            "updated_at": "2024-01-01T00:00:00Z"
        }
        mock_request.return_value = mock_response
        
        client = create_client(access_token="test_token")
        result = client.market.interest_rates.get_rate("SELIC")
        
        assert result["uid"] == "SELIC"
        assert result["value"] == 14.15
        mock_request.assert_called_once()
        assert "/market/interest_rates/SELIC" in mock_request.call_args[1]["url"]
    
    @patch("oplab.client.requests.request")
    def test_list_stocks(self, mock_request):
        """Test listing stocks"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"symbol": "PETR4", "name": "Petrobras", "close": 28.50},
            {"symbol": "VALE3", "name": "Vale", "close": 65.20}
        ]
        mock_request.return_value = mock_response
        
        client = create_client(access_token="test_token")
        result = client.market.stocks.list_stocks(limit=10)
        
        assert len(result) == 2
        assert result[0]["symbol"] == "PETR4"
        call_args = mock_request.call_args
        assert call_args[1]["params"]["limit"] == 10
    
    @patch("oplab.client.requests.request")
    def test_list_options(self, mock_request):
        """Test listing options"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"symbol": "PETRE100", "category": "CALL", "strike": 30.0},
            {"symbol": "PETRP100", "category": "PUT", "strike": 30.0}
        ]
        mock_request.return_value = mock_response
        
        client = create_client(access_token="test_token")
        result = client.market.options.list_options("PETR4")
        
        assert len(result) == 2
        assert "/market/options/PETR4" in mock_request.call_args[1]["url"]


class TestOPLABClientDomainAPIs:
    """Test domain API methods"""
    
    @patch("oplab.client.requests.request")
    def test_list_portfolios(self, mock_request):
        """Test listing portfolios"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": 1, "name": "Portfolio 1"},
            {"id": 2, "name": "Portfolio 2"}
        ]
        mock_request.return_value = mock_response
        
        client = create_client(access_token="test_token")
        result = client.domain.portfolios.list_portfolios()
        
        assert len(result) == 2
        assert result[0]["id"] == 1
        assert "/domain/portfolios" in mock_request.call_args[1]["url"]
    
    @patch("oplab.client.requests.request")
    def test_create_portfolio(self, mock_request):
        """Test creating portfolio"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": 3, "name": "New Portfolio"}
        mock_request.return_value = mock_response
        
        client = create_client(access_token="test_token")
        result = client.domain.portfolios.create_portfolio("New Portfolio")
        
        assert result["id"] == 3
        call_args = mock_request.call_args
        assert call_args[1]["method"] == "POST"
        assert call_args[1]["json"]["name"] == "New Portfolio"


def test_integration_flow():
    """Integration test showing typical usage flow"""
    with patch("oplab.client.requests.request") as mock_request:
        # Mock multiple API calls
        responses = [
            Mock(status_code=200, json=lambda: {"value": 14.15}),  # Interest rate
            Mock(status_code=200, json=lambda: [{"symbol": "PETR4", "close": 28.50}]),  # Stocks
            Mock(status_code=200, json=lambda: [{"symbol": "PETRE100", "strike": 30.0}])  # Options
        ]
        mock_request.side_effect = responses
        
        client = create_client(access_token="test_token")
        
        # Get interest rate
        rate = client.market.interest_rates.get_rate("SELIC")
        assert rate["value"] == 14.15
        
        # Get stocks
        stocks = client.market.stocks.list_stocks()
        assert stocks[0]["symbol"] == "PETR4"
        
        # Get options
        options = client.market.options.list_options("PETR4")
        assert options[0]["symbol"] == "PETRE100"
        
        assert mock_request.call_count == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

