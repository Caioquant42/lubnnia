"""
Test suite to verify which OPLAB API endpoints are accessible with the current plan.

This test makes actual API calls to determine which endpoints return 403 Forbidden
(plan limitation) vs which endpoints work successfully.

Results are collected and can be exported to a markdown report.
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pytest
import json

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oplab import create_client
from oplab.exceptions import (
    OPLABUnauthorizedError,
    OPLABForbiddenError,
    OPLABNotFoundError,
    OPLABException,
)


# Hardcoded OPLAB access token - REPLACE WITH YOUR ACTUAL TOKEN
OPLAB_ACCESS_TOKEN = "AMCEz113ZhZQ9jJjVkTo5clBXJah+I5NDoKjz6154NQ=--qLDf12hka7JOGPzQ/8/EHA==--ZGNhNmYxNDliMmEwNGM0NzNjYTQyYjE2MjNhZGMyZjM="  # Replace this with your actual token


class TestOPLABEndpointAccess:
    """Test which endpoints are accessible with current plan."""
    
    @pytest.fixture(scope="class")
    def client(self):
        """Create OPLAB client instance."""
        # Use hardcoded token or fallback to environment variable
        token = OPLAB_ACCESS_TOKEN if OPLAB_ACCESS_TOKEN != "your_token_here" else os.getenv('OPLAB_ACCESS_TOKEN')
        
        if not token:
            pytest.skip(
                "OPLAB_ACCESS_TOKEN not configured. "
                "Set it as OPLAB_ACCESS_TOKEN constant in this file or as environment variable."
            )
        
        try:
            return create_client(access_token=token)
        except ValueError as e:
            pytest.skip(f"Failed to create OPLAB client: {e}")
    
    # Class-level storage for results
    _results = {
        'market': {},
        'domain': {},
        'tested_at': datetime.now().isoformat()
    }
    
    def _check_endpoint(self, client, category: str, subcategory: str, 
                     method_name: str, test_func, *args, **kwargs) -> Dict:
        """
        Generic endpoint test helper.
        
        Returns:
            Dict with status: 'success', 'forbidden', 'not_found', 'error', etc.
        """
        endpoint_key = f"{subcategory}.{method_name}"
        result = {
            'category': category,
            'subcategory': subcategory,
            'method': method_name,
            'status': 'unknown',
            'error': None,
            'status_code': None
        }
        
        try:
            response = test_func(*args, **kwargs)
            result['status'] = 'success'
            result['has_data'] = response is not None
            if isinstance(response, list):
                result['data_count'] = len(response)
            elif isinstance(response, dict):
                result['has_keys'] = list(response.keys())[:5]  # First 5 keys
        except OPLABForbiddenError as e:
            result['status'] = 'forbidden'
            result['error'] = str(e)
            result['status_code'] = 403
        except OPLABNotFoundError as e:
            result['status'] = 'not_found'
            result['error'] = str(e)
            result['status_code'] = 404
        except OPLABUnauthorizedError as e:
            result['status'] = 'unauthorized'
            result['error'] = str(e)
            result['status_code'] = 401
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
        
        # Store result in class-level dictionary
        if category not in TestOPLABEndpointAccess._results:
            TestOPLABEndpointAccess._results[category] = {}
        if subcategory not in TestOPLABEndpointAccess._results[category]:
            TestOPLABEndpointAccess._results[category][subcategory] = {}
        TestOPLABEndpointAccess._results[category][subcategory][method_name] = result
        
        return result
    
    # ==================== MARKET API TESTS ====================
    
    @pytest.mark.slow
    def test_market_interest_rates_list(self, client):
        """Test listing all interest rates."""
        result = self._check_endpoint(
            client, 'market', 'interest_rates', 'list_rates',
            client.market.interest_rates.list_rates
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_interest_rates_get_selic(self, client):
        """Test getting SELIC rate."""
        result = self._check_endpoint(
            client, 'market', 'interest_rates', 'get_rate_SELIC',
            client.market.interest_rates.get_rate, 'SELIC'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_interest_rates_get_cetip(self, client):
        """Test getting CETIP rate."""
        result = self._check_endpoint(
            client, 'market', 'interest_rates', 'get_rate_CETIP',
            client.market.interest_rates.get_rate, 'CETIP'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_stocks_get_stock(self, client):
        """Test getting stock details."""
        result = self._check_endpoint(
            client, 'market', 'stocks', 'get_stock',
            client.market.stocks.get_stock, 'PETR4'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_stocks_list_stocks(self, client):
        """Test listing stocks with options."""
        result = self._check_endpoint(
            client, 'market', 'stocks', 'list_stocks',
            client.market.stocks.list_stocks, limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_stocks_list_all_stocks(self, client):
        """Test listing all stocks."""
        result = self._check_endpoint(
            client, 'market', 'stocks', 'list_all_stocks',
            client.market.stocks.list_all_stocks, limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found', 'error']
    
    @pytest.mark.slow
    def test_market_options_list_options(self, client):
        """Test listing options for an underlying."""
        result = self._check_endpoint(
            client, 'market', 'options', 'list_options',
            client.market.options.list_options, 'PETR4'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_options_get_option(self, client):
        """Test getting option details."""
        # Try to get a real option symbol (this might fail if we don't have one)
        result = self._check_endpoint(
            client, 'market', 'options', 'get_option',
            client.market.options.get_option, 'PETRE100'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found', 'error']
    
    @pytest.mark.slow
    def test_market_options_black_scholes(self, client):
        """Test Black-Scholes calculation."""
        result = self._check_endpoint(
            client, 'market', 'options', 'get_black_scholes',
            client.market.options.get_black_scholes,
            symbol='PETRE100', irate=14.15
        )
        assert result['status'] in ['success', 'forbidden', 'not_found', 'error']
    
    @pytest.mark.slow
    def test_market_options_covered_options(self, client):
        """Test listing covered options."""
        result = self._check_endpoint(
            client, 'market', 'options', 'list_covered_options',
            client.market.options.list_covered_options, 'PETR4'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_options_powders(self, client):
        """Test listing powders."""
        result = self._check_endpoint(
            client, 'market', 'options', 'list_powders',
            client.market.options.list_powders
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_instruments_get_instrument(self, client):
        """Test getting instrument details."""
        result = self._check_endpoint(
            client, 'market', 'instruments', 'get_instrument',
            client.market.instruments.get_instrument, 'PETR4'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_instruments_list_instruments(self, client):
        """Test listing multiple instruments."""
        result = self._check_endpoint(
            client, 'market', 'instruments', 'list_instruments',
            client.market.instruments.list_instruments, 'PETR4,VALE3'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_instruments_search(self, client):
        """Test searching instruments."""
        result = self._check_endpoint(
            client, 'market', 'instruments', 'search_instruments',
            client.market.instruments.search_instruments, 'PETR', limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_instruments_series(self, client):
        """Test getting instrument series."""
        result = self._check_endpoint(
            client, 'market', 'instruments', 'get_instrument_series',
            client.market.instruments.get_instrument_series, 'PETR4'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_quote_get_quote(self, client):
        """Test getting quotes."""
        result = self._check_endpoint(
            client, 'market', 'quote', 'get_quote',
            client.market.quote.get_quote, 'PETR4,VALE3'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_historical_get_historical_data(self, client):
        """Test getting historical data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        result = self._check_endpoint(
            client, 'market', 'historical', 'get_historical_data',
            client.market.historical.get_historical_data,
            'PETR4', '1d',
            start_date.strftime('%Y-%m-%dT00:00:00Z'),
            end_date.strftime('%Y-%m-%dT23:59:59Z')
        )
        assert result['status'] in ['success', 'forbidden', 'not_found', 'error']
    
    @pytest.mark.slow
    def test_market_historical_historical_options(self, client):
        """Test getting historical options."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        result = self._check_endpoint(
            client, 'market', 'historical', 'get_historical_options',
            client.market.historical.get_historical_options,
            'PETR4',
            start_date.strftime('%Y-%m-%d'),
            end_date.strftime('%Y-%m-%d')
        )
        assert result['status'] in ['success', 'forbidden', 'not_found', 'error']
    
    @pytest.mark.slow
    def test_market_historical_historical_instruments(self, client):
        """Test getting historical instruments."""
        test_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        result = self._check_endpoint(
            client, 'market', 'historical', 'get_historical_instruments',
            client.market.historical.get_historical_instruments,
            'PETR4,VALE3', test_date
        )
        assert result['status'] in ['success', 'forbidden', 'not_found', 'error']
    
    @pytest.mark.slow
    def test_market_statistics_highest_options_volume(self, client):
        """Test highest options volume."""
        result = self._check_endpoint(
            client, 'market', 'statistics', 'get_highest_options_volume',
            client.market.statistics.get_highest_options_volume, limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_statistics_best_covered_options_rates(self, client):
        """Test best covered options rates."""
        result = self._check_endpoint(
            client, 'market', 'statistics', 'get_best_covered_options_rates_CALL',
            client.market.statistics.get_best_covered_options_rates, 'CALL', limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_statistics_highest_options_variation(self, client):
        """Test highest options variation."""
        result = self._check_endpoint(
            client, 'market', 'statistics', 'get_highest_options_variation',
            client.market.statistics.get_highest_options_variation, 'PUT', limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_statistics_m9_m21_ranking(self, client):
        """Test M9_M21 ranking."""
        result = self._check_endpoint(
            client, 'market', 'statistics', 'get_m9_m21_ranking',
            client.market.statistics.get_m9_m21_ranking, limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_statistics_correl_ibov_ranking(self, client):
        """Test IBOV correlation ranking."""
        result = self._check_endpoint(
            client, 'market', 'statistics', 'get_correl_ibov_ranking',
            client.market.statistics.get_correl_ibov_ranking, limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_statistics_fundamental_ranking(self, client):
        """Test fundamental ranking."""
        result = self._check_endpoint(
            client, 'market', 'statistics', 'get_fundamental_ranking',
            client.market.statistics.get_fundamental_ranking, 'roe', limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_statistics_oplab_score_ranking(self, client):
        """Test OpLab score ranking."""
        result = self._check_endpoint(
            client, 'market', 'statistics', 'get_oplab_score_ranking',
            client.market.statistics.get_oplab_score_ranking, limit=10
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_companies_get_companies(self, client):
        """Test getting companies."""
        result = self._check_endpoint(
            client, 'market', 'companies', 'get_companies',
            client.market.companies.get_companies, 'PETR4,VALE3'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_exchanges_list_exchanges(self, client):
        """Test listing exchanges."""
        result = self._check_endpoint(
            client, 'market', 'exchanges', 'list_exchanges',
            client.market.exchanges.list_exchanges
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_exchanges_get_exchange(self, client):
        """Test getting exchange details."""
        result = self._check_endpoint(
            client, 'market', 'exchanges', 'get_exchange',
            client.market.exchanges.get_exchange, 'BOVESPA'
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    @pytest.mark.slow
    def test_market_status_get_market_status(self, client):
        """Test getting market status."""
        result = self._check_endpoint(
            client, 'market', 'status', 'get_market_status',
            client.market.status.get_market_status
        )
        assert result['status'] in ['success', 'forbidden', 'not_found']
    
    # ==================== DOMAIN API TESTS ====================
    
    @pytest.mark.slow
    def test_domain_users_authorize(self, client):
        """Test user authorization."""
        result = self._check_endpoint(
            client, 'domain', 'users', 'authorize',
            client.domain.users.authorize
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_users_get_settings(self, client):
        """Test getting user settings."""
        result = self._check_endpoint(
            client, 'domain', 'users', 'get_settings',
            client.domain.users.get_settings
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_users_list_advisors(self, client):
        """Test listing advisors."""
        result = self._check_endpoint(
            client, 'domain', 'users', 'list_advisors',
            client.domain.users.list_advisors
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_portfolios_list_portfolios(self, client):
        """Test listing portfolios."""
        result = self._check_endpoint(
            client, 'domain', 'portfolios', 'list_portfolios',
            client.domain.portfolios.list_portfolios
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_brokers_list_brokers(self, client):
        """Test listing brokers."""
        result = self._check_endpoint(
            client, 'domain', 'brokers', 'list_brokers',
            client.domain.brokers.list_brokers
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_trading_accounts_list_trading_accounts(self, client):
        """Test listing trading accounts."""
        result = self._check_endpoint(
            client, 'domain', 'trading_accounts', 'list_trading_accounts',
            client.domain.trading_accounts.list_trading_accounts
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_notifications_list_notifications(self, client):
        """Test listing notifications."""
        result = self._check_endpoint(
            client, 'domain', 'notifications', 'list_notifications',
            client.domain.notifications.list_notifications, page=1, per=10
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_notifications_unread_count(self, client):
        """Test getting unread notifications count."""
        result = self._check_endpoint(
            client, 'domain', 'notifications', 'get_unread_count',
            client.domain.notifications.get_unread_count
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_watchlists_list_watchlists(self, client):
        """Test listing watchlists."""
        result = self._check_endpoint(
            client, 'domain', 'watchlists', 'list_watchlists',
            client.domain.watchlists.list_watchlists
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.mark.slow
    def test_domain_trading_get_business_days(self, client):
        """Test calculating business days."""
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        result = self._check_endpoint(
            client, 'domain', 'trading', 'get_business_days',
            client.domain.trading.get_business_days, future_date
        )
        assert result['status'] in ['success', 'forbidden', 'unauthorized', 'not_found']
    
    @pytest.fixture(scope="class", autouse=True)
    def generate_final_report(self, request):
        """Generate markdown report after all tests complete."""
        yield
        # This runs after all tests in the class complete
        if hasattr(TestOPLABEndpointAccess, '_results'):
            report_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'docs',
                'OPLAB_ENDPOINT_ACCESS_REPORT.md'
            )
            generate_markdown_report(TestOPLABEndpointAccess._results, report_path)


def generate_markdown_report(results: Dict, output_path: str):
    """Generate markdown report from test results."""
    lines = []
    lines.append("# OPLAB API Endpoint Access Report")
    lines.append("")
    lines.append(f"Generated: {results.get('tested_at', 'Unknown')}")
    lines.append("")
    lines.append("This report shows which OPLAB API endpoints are accessible")
    lines.append("with the current plan based on actual API tests.")
    lines.append("")
    lines.append("## Legend")
    lines.append("")
    lines.append("- ✅ **Success**: Endpoint is accessible and working")
    lines.append("- ❌ **Forbidden**: Endpoint requires a higher plan (403)")
    lines.append("- ⚠️ **Not Found**: Endpoint returned 404 (may be invalid request)")
    lines.append("- 🔒 **Unauthorized**: Authentication failed (401)")
    lines.append("- ⚡ **Error**: Other error occurred")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    # Market endpoints
    lines.append("## Market Endpoints")
    lines.append("")
    
    if 'market' in results:
        for subcategory, methods in sorted(results['market'].items()):
            lines.append(f"### {subcategory.replace('_', ' ').title()}")
            lines.append("")
            lines.append("| Method | Status | Details |")
            lines.append("|--------|--------|---------|")
            
            for method_name, result in sorted(methods.items()):
                status = result.get('status', 'unknown')
                if status == 'success':
                    icon = "✅"
                    details = f"Working"
                    if result.get('has_data'):
                        if 'data_count' in result:
                            details += f" ({result['data_count']} items)"
                        else:
                            details += " (data returned)"
                elif status == 'forbidden':
                    icon = "❌"
                    details = "Plan limitation (403 Forbidden)"
                elif status == 'not_found':
                    icon = "⚠️"
                    details = f"Not found (404) - {result.get('error', 'Unknown')}"
                elif status == 'unauthorized':
                    icon = "🔒"
                    details = "Unauthorized (401)"
                else:
                    icon = "⚡"
                    details = f"Error: {result.get('error', 'Unknown')[:50]}"
                
                method_display = method_name.replace('_', ' ').title()
                lines.append(f"| `{method_display}` | {icon} {status.upper()} | {details} |")
            
            lines.append("")
    
    # Domain endpoints
    lines.append("## Domain Endpoints")
    lines.append("")
    lines.append("*Note: Domain endpoints typically require authentication and may have additional plan restrictions.*")
    lines.append("")
    
    if 'domain' in results:
        for subcategory, methods in sorted(results['domain'].items()):
            lines.append(f"### {subcategory.replace('_', ' ').title()}")
            lines.append("")
            lines.append("| Method | Status | Details |")
            lines.append("|--------|--------|---------|")
            
            for method_name, result in sorted(methods.items()):
                status = result.get('status', 'unknown')
                if status == 'success':
                    icon = "✅"
                    details = f"Working"
                    if result.get('has_data'):
                        if 'data_count' in result:
                            details += f" ({result['data_count']} items)"
                        else:
                            details += " (data returned)"
                elif status == 'forbidden':
                    icon = "❌"
                    details = "Plan limitation (403 Forbidden)"
                elif status == 'not_found':
                    icon = "⚠️"
                    details = f"Not found (404)"
                elif status == 'unauthorized':
                    icon = "🔒"
                    details = "Unauthorized (401)"
                else:
                    icon = "⚡"
                    details = f"Error: {result.get('error', 'Unknown')[:50]}"
                
                method_display = method_name.replace('_', ' ').title()
                lines.append(f"| `{method_display}` | {icon} {status.upper()} | {details} |")
            
            lines.append("")
    
    # Summary statistics
    lines.append("---")
    lines.append("")
    lines.append("## Summary Statistics")
    lines.append("")
    
    total_tested = 0
    total_success = 0
    total_forbidden = 0
    total_not_found = 0
    total_unauthorized = 0
    total_errors = 0
    
    for category in ['market', 'domain']:
        if category in results:
            for subcategory, methods in results[category].items():
                for method_name, result in methods.items():
                    total_tested += 1
                    status = result.get('status', 'unknown')
                    if status == 'success':
                        total_success += 1
                    elif status == 'forbidden':
                        total_forbidden += 1
                    elif status == 'not_found':
                        total_not_found += 1
                    elif status == 'unauthorized':
                        total_unauthorized += 1
                    else:
                        total_errors += 1
    
    lines.append(f"- **Total Endpoints Tested**: {total_tested}")
    lines.append(f"- **✅ Accessible**: {total_success} ({total_success/total_tested*100:.1f}%)" if total_tested > 0 else "- **✅ Accessible**: 0")
    lines.append(f"- **❌ Forbidden (403)**: {total_forbidden} ({total_forbidden/total_tested*100:.1f}%)" if total_tested > 0 else "- **❌ Forbidden (403)**: 0")
    lines.append(f"- **⚠️ Not Found (404)**: {total_not_found}")
    lines.append(f"- **🔒 Unauthorized (401)**: {total_unauthorized}")
    lines.append(f"- **⚡ Other Errors**: {total_errors}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    
    if total_forbidden > 0:
        lines.append(f"### Endpoints Requiring Plan Upgrade")
        lines.append("")
        lines.append("The following endpoints returned 403 Forbidden, indicating they require a higher subscription plan:")
        lines.append("")
        
        for category in ['market', 'domain']:
            if category in results:
                forbidden_found = False
                for subcategory, methods in sorted(results[category].items()):
                    forbidden_methods = [
                        (name, result) for name, result in methods.items()
                        if result.get('status') == 'forbidden'
                    ]
                    if forbidden_methods:
                        if not forbidden_found:
                            forbidden_found = True
                        for method_name, result in forbidden_methods:
                            lines.append(f"- `{category}.{subcategory}.{method_name}`")
                
                if forbidden_found:
                    lines.append("")
    else:
        lines.append("All tested endpoints are accessible with the current plan! ✅")
    
    lines.append("")
    lines.append("*Report generated automatically by test suite*")
    
    # Write to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n{'='*80}")
    print("REPORT GENERATED")
    print(f"{'='*80}")
    print(f"Report saved to: {output_path}")
    print(f"Total endpoints tested: {total_tested}")
    print(f"✅ Accessible: {total_success}")
    print(f"❌ Forbidden (403): {total_forbidden}")
    print(f"⚠️  Not Found (404): {total_not_found}")
    print(f"{'='*80}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

