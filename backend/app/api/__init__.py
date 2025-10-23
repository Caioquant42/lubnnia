from flask import Blueprint, make_response, jsonify
from flask_restful import Api
from .routes import *

bp = Blueprint('api', __name__)
api = Api(bp)

def index():
    return make_response(jsonify({
        "message": "Welcome to the Zomma Quant API",
        "endpoints": [  
            '/api/rrg',  # RRG (Relative Rotation Graph) endpoint
            'GET /api/rrg?symbol=ABEV3,PETR4',  # Filter by specific symbols
            'GET /api/rrg?quadrant=leading',  # Filter by quadrant (leading, weakening, lagging, improving)
            'GET /api/rrg?min_rs_ratio=100&min_rs_momentum=100',  # Filter by RS values
            'GET /api/rrg?date=2025-05-01',  # Filter by specific date
            'GET /api/rrg?sort_by=rs_ratio&sort_order=desc',  # Sort results
            'GET /api/rrg?limit=10',  # Limit number of results
            '/api/br-recommendations',
            'GET /api/br-recommendations?symbol=PETR4',
            'GET /api/br-recommendations?analysis=buy',
            'GET /api/br-recommendations?analysis=strong_buy',
            'GET /api/br-recommendations?analysis=all_buy',  # New combined endpoint
            'GET /api/br-recommendations?analysis=ibov',
            'GET /api/br-recommendations?analysis=b3',
            '/api/screener-rsi',  # New RSI screener endpoint
            'GET /api/screener-rsi?timeframe=15m',  # Filter by timeframe
            'GET /api/screener-rsi?timeframe=60m&condition=oversold',  # Filter by timeframe and condition
            '/api/volatility-surface',  # New volatility surface endpoint
            'GET /api/volatility-surface?symbol=EMBR3',  # Filter by symbol
            'GET /api/volatility-surface?symbol=EMBR3&option_type=CALL',  # Filter by option type
            'GET /api/volatility-surface?symbol=EMBR3&maturity_type=EUROPEAN',  # Filter by maturity type
            'GET /api/volatility-surface?symbol=EMBR3&moneyness=ATM',  # Filter by moneyness
            '/api/collar',  # New collar strategy endpoint
            'GET /api/collar?category=intrinsic',  # Filter by option category
            'GET /api/collar?maturity_range=less_than_14_days',  # Filter by maturity range
            'GET /api/collar?symbol=BBAS3',  # Filter by specific symbol
            'GET /api/collar?min_gain_to_risk=2',  # Filter by minimum gain-to-risk ratio
            'GET /api/collar?sort_by=combined_score&sort_order=desc',  # Sort by score
            '/api/covered-call',  # New covered call strategy endpoint
            'GET /api/covered-call?maturity_range=less_than_14_days',  # Filter by maturity range
            'GET /api/covered-call?symbol=PETR4',  # Filter by underlying symbol
            'GET /api/covered-call?min_cdi_relative_return=5',  # Filter by minimum CDI relative return
            'GET /api/covered-call?sort_by=annual_return&sort_order=desc',  # Sort by annual return
            'GET /api/covered-call?limit=10',  # Limit number of results
            '/api/pairs-trading',  # New pairs trading endpoint
            'GET /api/pairs-trading?data_type=signals',  # Get only recent trading signals
            'GET /api/pairs-trading?data_type=cointegration',  # Get only cointegration analysis
            'GET /api/pairs-trading?data_type=all',  # Get both cointegration and signals data
            'GET /api/pairs-trading?asset1=ALPA4&asset2=CYRE3',  # Filter by specific asset pair
            'GET /api/pairs-trading?signal_type=buy',  # Filter by signal type (buy or sell)
            'GET /api/pairs-trading?min_zscore=2.0&max_zscore=3.0',  # Filter by z-score range
            'GET /api/pairs-trading?min_beta=0.5&max_beta=1.5',  # Filter by beta (hedge ratio) range
            'GET /api/pairs-trading?max_beta=0.8',  # Filter for pairs with lower beta value
            'GET /api/pairs-trading?min_half_life=2&max_half_life=10',  # Filter by mean reversion half-life in days
            'GET /api/pairs-trading?min_half_life=0.5&max_half_life=5',  # Filter for faster mean reversion
            'GET /api/pairs-trading?period=last_6_months',  # Filter by analysis period
            'GET /api/pairs-trading?sort_by=current_zscore&sort_order=desc',  # Sort by z-score
            'GET /api/pairs-trading?sort_by=beta&sort_order=asc',  # Sort by beta (hedge ratio)
            'GET /api/pairs-trading?sort_by=half_life&sort_order=asc',  # Sort by mean reversion speed
            '/api/ibov-stocks',  # New IBOV stocks endpoint
            'GET /api/ibov-stocks?symbol=PETR4',  # Filter by specific symbol
            'GET /api/ibov-stocks?min_iv_current=20&max_iv_current=40',  # Filter by IV range
            'GET /api/ibov-stocks?min_beta_ibov=0.5&max_beta_ibov=1.0',  # Filter by beta range
            'GET /api/ibov-stocks?min_iv_ewma_ratio=1.0&max_iv_ewma_ratio=2.0',  # Filter by IV/EWMA ratio
            'GET /api/ibov-stocks?sort_by=iv_ewma_ratio&sort_order=desc',  # Sort by IV/EWMA ratio            'GET /api/ibov-stocks?sort_by=iv_current&sort_order=desc',  # Sort by IV current
            'GET /api/ibov-stocks?limit=10',  # Limit number of results            '/api/cumulative-performance',  # New cumulative performance endpoint
            'GET /api/cumulative-performance?start_date=2020-01-01&end_date=2023-12-31',  # Filter by date range
            'GET /api/cumulative-performance?assets=CDI,SP500,IBOV',  # Filter by specific assets
            'GET /api/cumulative-performance?normalize=true',  # Normalize to start at 100
            'GET /api/cumulative-performance?start_date=2020-01-01&assets=SP500,IBOV&normalize=true',  # Combined filters
            '/api/fluxo-ddm',  # New flux DDM endpoint for investment flows
            'GET /api/fluxo-ddm',  # Get all flux DDM data
            'GET /api/fluxo-ddm?limit=10',  # Limit number of results
            'GET /api/fluxo-ddm?sort_order=desc',  # Sort by total flow value (desc/asc)
            'GET /api/fluxo-ddm?min_value=-1000&max_value=1000',  # Filter by total flow value range
            'GET /api/fluxo-ddm?date=21/05/2025',  # Filter by specific date (DD/MM/YYYY)            'GET /api/fluxo-ddm?start_date=2025-01-01&end_date=2025-05-24',  # Filter by date range (YYYY-MM-DD)
            'GET /api/fluxo-ddm?investor_type=Estrangeiro',  # Filter by investor type (Estrangeiro, Institucional, PF, IF, Outros)
            'GET /api/fluxo-ddm?min_value=0&investor_type=PF',  # Combined filters for positive PF flows
            '/api/dividend-calendar',  # New dividend calendar endpoint
            'GET /api/dividend-calendar',  # Get all dividend calendar data
            'GET /api/dividend-calendar?codigo=PETR4',  # Filter by stock code
            'GET /api/dividend-calendar?tipo=Dividendo',  # Filter by dividend type (Dividendo, JCP)
            'GET /api/dividend-calendar?min_value=0.1&max_value=10.0',  # Filter by value range
            'GET /api/dividend-calendar?start_date=01/05/2025&end_date=31/05/2025',  # Filter by date range
            'GET /api/dividend-calendar?payment_date=02/05/2025',  # Filter by specific payment date
            'GET /api/dividend-calendar?upcoming_days=30',  # Get dividends in next 30 days
            'GET /api/dividend-calendar?sort_by=valor_numeric&sort_order=desc',  # Sort by value descending
            'GET /api/dividend-calendar?sort_by=pagamento&sort_order=asc',  # Sort by payment date ascending
            'GET /api/dividend-calendar?limit=50',  # Limit number of results
            'GET /api/dividend-calendar?codigo=PETR4&include_summary=true'  # Include summary statistics
        ]
    }), 200)

# Import the Config class directly
from config import Config

# Get API paths from config
api_paths = Config.API_PATHS if hasattr(Config, 'API_PATHS') else {}

# Register resources using config paths
api.add_resource(RRGDataResource, api_paths.get('rrg', '/rrg'))
api.add_resource(BrRecommendationsResource, api_paths.get('br_recommendations', '/br-recommendations'))
api.add_resource(ScreenerRSIResource, api_paths.get('screener_rsi', '/screener-rsi'))
api.add_resource(VolatilitySurfaceResource, api_paths.get('volatility_surface', '/volatility-surface'))
api.add_resource(CollarResource, api_paths.get('collar', '/collar'))
api.add_resource(CoveredCallResource, api_paths.get('covered_call', '/covered-call'))
api.add_resource(PairsTradingResource, api_paths.get('pairs_trading', '/pairs-trading'))
api.add_resource(IBOVStocksResource, api_paths.get('ibov_stocks', '/ibov-stocks'))
api.add_resource(CumulativePerformanceResource, api_paths.get('cumulative_performance', '/cumulative-performance'))
api.add_resource(FluxoDDMResource, api_paths.get('fluxo_ddm', '/fluxo-ddm'))
api.add_resource(DividendCalendarResource, api_paths.get('dividend_calendar', '/dividend-calendar'))
bp.add_url_rule('/', 'index', index)