"""
Generate example usage and JSON outputs for all working OPLAB API endpoints.

This script calls each working endpoint and saves the JSON responses
so you can analyze the output structure of each method.
"""
import os
import sys
import json
from datetime import datetime, timedelta
from pathlib import Path

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from oplab import create_client

# Get token from environment or hardcode
OPLAB_ACCESS_TOKEN = os.getenv('OPLAB_ACCESS_TOKEN')
if not OPLAB_ACCESS_TOKEN:
    # Fallback to hardcoded token (set this if needed)
    OPLAB_ACCESS_TOKEN = "AMCEz113ZhZQ9jJjVkTo5clBXJah+I5NDoKjz6154NQ=--qLDf12hka7JOGPzQ/8/EHA==--ZGNhNmYxNDliMmEwNGM0NzNjYTQyYjE2MjNhZGMyZjM="

# Create output directory
OUTPUT_DIR = Path(__file__).parent.parent / "docs" / "oplab_examples"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Create examples directory for JSON files
JSON_DIR = OUTPUT_DIR / "json_outputs"
JSON_DIR.mkdir(parents=True, exist_ok=True)


def save_json_output(name: str, data, endpoint_path: str):
    """Save JSON output to file."""
    filename = f"{name.lower().replace(' ', '_').replace('/', '_')}.json"
    filepath = JSON_DIR / filename
    
    output = {
        "endpoint": endpoint_path,
        "generated_at": datetime.now().isoformat(),
        "data": data
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False, default=str)
    
    return filepath


def generate_examples():
    """Generate examples and JSON outputs for all working endpoints."""
    client = create_client(access_token=OPLAB_ACCESS_TOKEN)
    
    examples = []
    errors = []
    
    print("Generating examples for all working OPLAB API endpoints...")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"JSON directory: {JSON_DIR}\n")
    
    # ==================== MARKET ENDPOINTS ====================
    
    print("📊 Market Endpoints")
    print("-" * 80)
    
    # Interest Rates
    print("1. Interest Rates...")
    try:
        # List all rates
        rates = client.market.interest_rates.list_rates()
        save_json_output("interest_rates_list", rates, "market.interest_rates.list_rates()")
        examples.append({
            "category": "Market",
            "subcategory": "Interest Rates",
            "method": "list_rates",
            "example": "client.market.interest_rates.list_rates()",
            "json_file": "interest_rates_list.json",
            "description": "List all available interest rates (SELIC, CETIP)"
        })
        
        # Get SELIC rate
        selic = client.market.interest_rates.get_rate('SELIC')
        save_json_output("interest_rate_selic", selic, "market.interest_rates.get_rate('SELIC')")
        examples.append({
            "category": "Market",
            "subcategory": "Interest Rates",
            "method": "get_rate (SELIC)",
            "example": "client.market.interest_rates.get_rate('SELIC')",
            "json_file": "interest_rate_selic.json",
            "description": "Get current SELIC interest rate"
        })
        
        # Get CETIP rate
        cetip = client.market.interest_rates.get_rate('CETIP')
        save_json_output("interest_rate_cetip", cetip, "market.interest_rates.get_rate('CETIP')")
        examples.append({
            "category": "Market",
            "subcategory": "Interest Rates",
            "method": "get_rate (CETIP)",
            "example": "client.market.interest_rates.get_rate('CETIP')",
            "json_file": "interest_rate_cetip.json",
            "description": "Get current CETIP interest rate"
        })
        print("   ✅ Interest rates")
    except Exception as e:
        errors.append(("Interest Rates", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Stocks
    print("2. Stocks...")
    try:
        # Get stock
        stock = client.market.stocks.get_stock('PETR4')
        save_json_output("stock_get_petr4", stock, "market.stocks.get_stock('PETR4')")
        examples.append({
            "category": "Market",
            "subcategory": "Stocks",
            "method": "get_stock",
            "example": "client.market.stocks.get_stock('PETR4')",
            "json_file": "stock_get_petr4.json",
            "description": "Get detailed stock information for PETR4"
        })
        
        # List stocks with options
        stocks = client.market.stocks.list_stocks(limit=10)
        save_json_output("stocks_list", stocks, "market.stocks.list_stocks(limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Stocks",
            "method": "list_stocks",
            "example": "client.market.stocks.list_stocks(limit=10)",
            "json_file": "stocks_list.json",
            "description": "List stocks that have options available"
        })
        print("   ✅ Stocks")
    except Exception as e:
        errors.append(("Stocks", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Options
    print("3. Options...")
    try:
        # List options
        options = client.market.options.list_options('PETR4')
        save_json_output("options_list_petr4", options, "market.options.list_options('PETR4')")
        examples.append({
            "category": "Market",
            "subcategory": "Options",
            "method": "list_options",
            "example": "client.market.options.list_options('PETR4')",
            "json_file": "options_list_petr4.json",
            "description": "List all options (CALL and PUT) for PETR4 underlying"
        })
        
        # Get option
        option = client.market.options.get_option('PETRE100')
        if option:
            save_json_output("option_get_petre100", option, "market.options.get_option('PETRE100')")
            examples.append({
                "category": "Market",
                "subcategory": "Options",
                "method": "get_option",
                "example": "client.market.options.get_option('PETRE100')",
                "json_file": "option_get_petre100.json",
                "description": "Get detailed information for specific option PETRE100"
            })
        
        # List covered options
        covered = client.market.options.list_covered_options('PETR4')
        save_json_output("options_covered_petr4", covered, "market.options.list_covered_options('PETR4')")
        examples.append({
            "category": "Market",
            "subcategory": "Options",
            "method": "list_covered_options",
            "example": "client.market.options.list_covered_options('PETR4')",
            "json_file": "options_covered_petr4.json",
            "description": "List options suitable for covered strategies"
        })
        
        # List powders
        powders = client.market.options.list_powders()
        save_json_output("options_powders", powders[:100], "market.options.list_powders()")  # Limit to first 100
        examples.append({
            "category": "Market",
            "subcategory": "Options",
            "method": "list_powders",
            "example": "client.market.options.list_powders()",
            "json_file": "options_powders.json",
            "description": "List low-priced 'pozinhos' options (limited to first 100 items)"
        })
        print("   ✅ Options")
    except Exception as e:
        errors.append(("Options", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Instruments
    print("4. Instruments...")
    try:
        # Get instrument
        instrument = client.market.instruments.get_instrument('PETR4')
        save_json_output("instrument_get_petr4", instrument, "market.instruments.get_instrument('PETR4')")
        examples.append({
            "category": "Market",
            "subcategory": "Instruments",
            "method": "get_instrument",
            "example": "client.market.instruments.get_instrument('PETR4')",
            "json_file": "instrument_get_petr4.json",
            "description": "Get instrument details (works for stocks, options, etc.)"
        })
        
        # List instruments
        instruments = client.market.instruments.list_instruments('PETR4,VALE3')
        save_json_output("instruments_list", instruments, "market.instruments.list_instruments('PETR4,VALE3')")
        examples.append({
            "category": "Market",
            "subcategory": "Instruments",
            "method": "list_instruments",
            "example": "client.market.instruments.list_instruments('PETR4,VALE3')",
            "json_file": "instruments_list.json",
            "description": "Get details for multiple instruments"
        })
        
        # Search instruments
        search_results = client.market.instruments.search_instruments('PETR', limit=10)
        save_json_output("instruments_search_petr", search_results, "market.instruments.search_instruments('PETR', limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Instruments",
            "method": "search_instruments",
            "example": "client.market.instruments.search_instruments('PETR', limit=10)",
            "json_file": "instruments_search_petr.json",
            "description": "Search for instruments by symbol or company name"
        })
        
        # Get instrument series
        series = client.market.instruments.get_instrument_series('PETR4')
        save_json_output("instrument_series_petr4", series, "market.instruments.get_instrument_series('PETR4')")
        examples.append({
            "category": "Market",
            "subcategory": "Instruments",
            "method": "get_instrument_series",
            "example": "client.market.instruments.get_instrument_series('PETR4')",
            "json_file": "instrument_series_petr4.json",
            "description": "Get instrument with all option series organized by due date"
        })
        print("   ✅ Instruments")
    except Exception as e:
        errors.append(("Instruments", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Quote
    print("5. Quote...")
    try:
        quotes = client.market.quote.get_quote('PETR4,VALE3')
        save_json_output("quote_petr4_vale3", quotes, "market.quote.get_quote('PETR4,VALE3')")
        examples.append({
            "category": "Market",
            "subcategory": "Quote",
            "method": "get_quote",
            "example": "client.market.quote.get_quote('PETR4,VALE3')",
            "json_file": "quote_petr4_vale3.json",
            "description": "Get real-time quotes for multiple instruments"
        })
        print("   ✅ Quote")
    except Exception as e:
        errors.append(("Quote", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Statistics
    print("6. Statistics...")
    try:
        # Highest options volume
        vol = client.market.statistics.get_highest_options_volume(limit=10)
        save_json_output("statistics_highest_options_volume", vol, "market.statistics.get_highest_options_volume(limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Statistics",
            "method": "get_highest_options_volume",
            "example": "client.market.statistics.get_highest_options_volume(limit=10)",
            "json_file": "statistics_highest_options_volume.json",
            "description": "Get assets with highest options trading volume"
        })
        
        # Best covered options rates
        best_calls = client.market.statistics.get_best_covered_options_rates('CALL', limit=10)
        save_json_output("statistics_best_covered_calls", best_calls, "market.statistics.get_best_covered_options_rates('CALL', limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Statistics",
            "method": "get_best_covered_options_rates (CALL)",
            "example": "client.market.statistics.get_best_covered_options_rates('CALL', limit=10)",
            "json_file": "statistics_best_covered_calls.json",
            "description": "Get CALL options with highest profit rates"
        })
        
        # Highest options variation
        variation = client.market.statistics.get_highest_options_variation('PUT', limit=10)
        save_json_output("statistics_highest_variation_put", variation, "market.statistics.get_highest_options_variation('PUT', limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Statistics",
            "method": "get_highest_options_variation",
            "example": "client.market.statistics.get_highest_options_variation('PUT', limit=10)",
            "json_file": "statistics_highest_variation_put.json",
            "description": "Get PUT options with highest price variations"
        })
        
        # M9_M21 ranking
        m9_m21 = client.market.statistics.get_m9_m21_ranking(limit=10)
        save_json_output("statistics_m9_m21_ranking", m9_m21, "market.statistics.get_m9_m21_ranking(limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Statistics",
            "method": "get_m9_m21_ranking",
            "example": "client.market.statistics.get_m9_m21_ranking(limit=10)",
            "json_file": "statistics_m9_m21_ranking.json",
            "description": "Get stocks ranked by 9-day and 21-day moving average trends"
        })
        
        # IBOV correlation ranking
        ibov_corr = client.market.statistics.get_correl_ibov_ranking(limit=10)
        save_json_output("statistics_ibov_correlation", ibov_corr, "market.statistics.get_correl_ibov_ranking(limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Statistics",
            "method": "get_correl_ibov_ranking",
            "example": "client.market.statistics.get_correl_ibov_ranking(limit=10)",
            "json_file": "statistics_ibov_correlation.json",
            "description": "Get stocks ordered by correlation with IBOV index"
        })
        
        # Fundamental ranking
        fundamental = client.market.statistics.get_fundamental_ranking('roe', limit=10)
        save_json_output("statistics_fundamental_roe", fundamental, "market.statistics.get_fundamental_ranking('roe', limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Statistics",
            "method": "get_fundamental_ranking",
            "example": "client.market.statistics.get_fundamental_ranking('roe', limit=10)",
            "json_file": "statistics_fundamental_roe.json",
            "description": "Get companies ranked by ROE (Return on Equity)"
        })
        
        # OpLab score ranking
        oplab_score = client.market.statistics.get_oplab_score_ranking(limit=10)
        save_json_output("statistics_oplab_score", oplab_score, "market.statistics.get_oplab_score_ranking(limit=10)")
        examples.append({
            "category": "Market",
            "subcategory": "Statistics",
            "method": "get_oplab_score_ranking",
            "example": "client.market.statistics.get_oplab_score_ranking(limit=10)",
            "json_file": "statistics_oplab_score.json",
            "description": "Get stocks ranked by OpLab proprietary score"
        })
        print("   ✅ Statistics")
    except Exception as e:
        errors.append(("Statistics", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Companies
    print("7. Companies...")
    try:
        companies = client.market.companies.get_companies('PETR4,VALE3')
        save_json_output("companies_petr4_vale3", companies, "market.companies.get_companies('PETR4,VALE3')")
        examples.append({
            "category": "Market",
            "subcategory": "Companies",
            "method": "get_companies",
            "example": "client.market.companies.get_companies('PETR4,VALE3')",
            "json_file": "companies_petr4_vale3.json",
            "description": "Get company data for specified stock symbols"
        })
        print("   ✅ Companies")
    except Exception as e:
        errors.append(("Companies", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Exchanges
    print("8. Exchanges...")
    try:
        exchanges = client.market.exchanges.list_exchanges()
        save_json_output("exchanges_list", exchanges, "market.exchanges.list_exchanges()")
        examples.append({
            "category": "Market",
            "subcategory": "Exchanges",
            "method": "list_exchanges",
            "example": "client.market.exchanges.list_exchanges()",
            "json_file": "exchanges_list.json",
            "description": "List all stock exchanges in Brazil"
        })
        
        exchange = client.market.exchanges.get_exchange('BOVESPA')
        save_json_output("exchange_bovespa", exchange, "market.exchanges.get_exchange('BOVESPA')")
        examples.append({
            "category": "Market",
            "subcategory": "Exchanges",
            "method": "get_exchange",
            "example": "client.market.exchanges.get_exchange('BOVESPA')",
            "json_file": "exchange_bovespa.json",
            "description": "Get specific exchange details"
        })
        print("   ✅ Exchanges")
    except Exception as e:
        errors.append(("Exchanges", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Status
    print("9. Market Status...")
    try:
        status = client.market.status.get_market_status()
        save_json_output("market_status", status, "market.status.get_market_status()")
        examples.append({
            "category": "Market",
            "subcategory": "Status",
            "method": "get_market_status",
            "example": "client.market.status.get_market_status()",
            "json_file": "market_status.json",
            "description": "Get current market status (open, closed, pre-opening, etc.)"
        })
        print("   ✅ Market Status")
    except Exception as e:
        errors.append(("Market Status", str(e)))
        print(f"   ❌ Error: {e}")
    
    # ==================== DOMAIN ENDPOINTS ====================
    
    print("\n👤 Domain Endpoints")
    print("-" * 80)
    
    # Users
    print("10. Users...")
    try:
        authorize = client.domain.users.authorize()
        save_json_output("users_authorize", authorize, "domain.users.authorize()")
        examples.append({
            "category": "Domain",
            "subcategory": "Users",
            "method": "authorize",
            "example": "client.domain.users.authorize()",
            "json_file": "users_authorize.json",
            "description": "Get current user authorization context"
        })
        
        settings = client.domain.users.get_settings()
        save_json_output("users_settings", settings, "domain.users.get_settings()")
        examples.append({
            "category": "Domain",
            "subcategory": "Users",
            "method": "get_settings",
            "example": "client.domain.users.get_settings()",
            "json_file": "users_settings.json",
            "description": "Get user settings and preferences"
        })
        
        advisors = client.domain.users.list_advisors()
        save_json_output("users_advisors", advisors, "domain.users.list_advisors()")
        examples.append({
            "category": "Domain",
            "subcategory": "Users",
            "method": "list_advisors",
            "example": "client.domain.users.list_advisors()",
            "json_file": "users_advisors.json",
            "description": "List user advisors"
        })
        print("   ✅ Users")
    except Exception as e:
        errors.append(("Users", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Portfolios
    print("11. Portfolios...")
    try:
        portfolios = client.domain.portfolios.list_portfolios()
        save_json_output("portfolios_list", portfolios, "domain.portfolios.list_portfolios()")
        examples.append({
            "category": "Domain",
            "subcategory": "Portfolios",
            "method": "list_portfolios",
            "example": "client.domain.portfolios.list_portfolios()",
            "json_file": "portfolios_list.json",
            "description": "List all user portfolios"
        })
        print("   ✅ Portfolios")
    except Exception as e:
        errors.append(("Portfolios", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Notifications
    print("12. Notifications...")
    try:
        notifications = client.domain.notifications.list_notifications(page=1, per=10)
        save_json_output("notifications_list", notifications, "domain.notifications.list_notifications(page=1, per=10)")
        examples.append({
            "category": "Domain",
            "subcategory": "Notifications",
            "method": "list_notifications",
            "example": "client.domain.notifications.list_notifications(page=1, per=10)",
            "json_file": "notifications_list.json",
            "description": "List user notifications"
        })
        
        unread_count = client.domain.notifications.get_unread_count()
        save_json_output("notifications_unread_count", unread_count, "domain.notifications.get_unread_count()")
        examples.append({
            "category": "Domain",
            "subcategory": "Notifications",
            "method": "get_unread_count",
            "example": "client.domain.notifications.get_unread_count()",
            "json_file": "notifications_unread_count.json",
            "description": "Get count of unread notifications"
        })
        print("   ✅ Notifications")
    except Exception as e:
        errors.append(("Notifications", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Watchlists
    print("13. Watchlists...")
    try:
        watchlists = client.domain.watchlists.list_watchlists()
        save_json_output("watchlists_list", watchlists, "domain.watchlists.list_watchlists()")
        examples.append({
            "category": "Domain",
            "subcategory": "Watchlists",
            "method": "list_watchlists",
            "example": "client.domain.watchlists.list_watchlists()",
            "json_file": "watchlists_list.json",
            "description": "List all user watchlists"
        })
        print("   ✅ Watchlists")
    except Exception as e:
        errors.append(("Watchlists", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Trading Accounts
    print("14. Trading Accounts...")
    try:
        trading_accounts = client.domain.trading_accounts.list_trading_accounts()
        save_json_output("trading_accounts_list", trading_accounts, "domain.trading_accounts.list_trading_accounts()")
        examples.append({
            "category": "Domain",
            "subcategory": "Trading Accounts",
            "method": "list_trading_accounts",
            "example": "client.domain.trading_accounts.list_trading_accounts()",
            "json_file": "trading_accounts_list.json",
            "description": "List all trading accounts"
        })
        print("   ✅ Trading Accounts")
    except Exception as e:
        errors.append(("Trading Accounts", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Trading
    print("15. Trading...")
    try:
        future_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        business_days = client.domain.trading.get_business_days(future_date)
        save_json_output("trading_business_days", business_days, f"domain.trading.get_business_days('{future_date}')")
        examples.append({
            "category": "Domain",
            "subcategory": "Trading",
            "method": "get_business_days",
            "example": f"client.domain.trading.get_business_days('{future_date}')",
            "json_file": "trading_business_days.json",
            "description": "Calculate business days until a given date"
        })
        print("   ✅ Trading")
    except Exception as e:
        errors.append(("Trading", str(e)))
        print(f"   ❌ Error: {e}")
    
    # Generate markdown documentation
    generate_markdown_doc(examples, errors)
    
    print(f"\n✅ Complete! Generated {len(examples)} examples")
    print(f"📁 JSON files saved to: {JSON_DIR}")
    print(f"📄 Documentation saved to: {OUTPUT_DIR / 'OPLAB_API_EXAMPLES.md'}")


def generate_markdown_doc(examples, errors):
    """Generate markdown documentation with examples."""
    lines = []
    lines.append("# OPLAB API Usage Examples")
    lines.append("")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("")
    lines.append("This document provides example usage for all working OPLAB API endpoints.")
    lines.append("Each example includes the code snippet and a link to the JSON output file")
    lines.append("for analyzing the response structure.")
    lines.append("")
    lines.append("## Table of Contents")
    lines.append("")
    
    # Group examples by category
    market_examples = [e for e in examples if e['category'] == 'Market']
    domain_examples = [e for e in examples if e['category'] == 'Domain']
    
    # Market sections
    market_subcategories = sorted(set(e['subcategory'] for e in market_examples))
    for subcat in market_subcategories:
        anchor = subcat.lower().replace(' ', '-')
        lines.append(f"- [Market - {subcat}](#market---{anchor})")
    
    # Domain sections
    domain_subcategories = sorted(set(e['subcategory'] for e in domain_examples))
    for subcat in domain_subcategories:
        anchor = subcat.lower().replace(' ', '-')
        lines.append(f"- [Domain - {subcat}](#domain---{anchor})")
    
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Market Endpoints")
    lines.append("")
    
    # Market examples by subcategory
    for subcat in market_subcategories:
        lines.append(f"### Market - {subcat}")
        lines.append("")
        subcat_examples = [e for e in market_examples if e['subcategory'] == subcat]
        
        for example in subcat_examples:
            lines.append(f"#### {example['method']}")
            lines.append("")
            lines.append(f"**Description:** {example['description']}")
            lines.append("")
            lines.append("**Example Code:**")
            lines.append("```python")
            lines.append(f"{example['example']}")
            lines.append("```")
            lines.append("")
            lines.append(f"**JSON Output:** [`{example['json_file']}`](json_outputs/{example['json_file']})")
            lines.append("")
    
    lines.append("---")
    lines.append("")
    lines.append("## Domain Endpoints")
    lines.append("")
    
    # Domain examples by subcategory
    for subcat in domain_subcategories:
        lines.append(f"### Domain - {subcat}")
        lines.append("")
        subcat_examples = [e for e in domain_examples if e['subcategory'] == subcat]
        
        for example in subcat_examples:
            lines.append(f"#### {example['method']}")
            lines.append("")
            lines.append(f"**Description:** {example['description']}")
            lines.append("")
            lines.append("**Example Code:**")
            lines.append("```python")
            lines.append(f"{example['example']}")
            lines.append("```")
            lines.append("")
            lines.append(f"**JSON Output:** [`{example['json_file']}`](json_outputs/{example['json_file']})")
            lines.append("")
    
    # Error summary
    if errors:
        lines.append("---")
        lines.append("")
        lines.append("## Errors Encountered")
        lines.append("")
        for category, error in errors:
            lines.append(f"- **{category}**: {error}")
        lines.append("")
    
    # Write to file
    output_file = OUTPUT_DIR / "OPLAB_API_EXAMPLES.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    
    print(f"\n📄 Generated documentation: {output_file}")


if __name__ == "__main__":
    generate_examples()




