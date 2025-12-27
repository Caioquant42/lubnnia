"""
Statistics and rankings endpoints.

Provides access to market statistics, rankings, and real-time metrics.
"""
from typing import Dict, Optional, List
from ..client import OPLABClient


class StatisticsAPI:
    """Statistics and rankings endpoints."""
    
    def __init__(self, client: OPLABClient):
        """
        Initialize statistics API.
        
        Args:
            client: OPLABClient instance.
        """
        self.client = client
    
    def get_highest_options_volume(
        self,
        order_by: str = 'total',
        limit: int = 20
    ) -> Optional[List[Dict]]:
        """
        Get assets with highest options trading volume.
        
        Args:
            order_by: Property to sort by ('call', 'put', or 'total', default: 'total').
            limit: Maximum number of items (default: 20).
            
        Returns:
            List of assets with highest options volume, including:
            call, put, total (volumes), symbol, name, sector.
            Returns None if no data available.
            
        Example:
            >>> top_volume = client.market.statistics.get_highest_options_volume(order_by='total', limit=10)
        """
        params = {
            'order_by': order_by,
            'limit': limit
        }
        return self.client.get('/market/statistics/realtime/highest_options_volume', params=params)
    
    def get_best_covered_options_rates(
        self,
        option_type: str,
        limit: int = 20
    ) -> Optional[List[Dict]]:
        """
        Get options with highest profit rates.
        
        Only includes PUT OTM and CALL ITM options.
        
        Args:
            option_type: Option type ('CALL' or 'PUT').
            limit: Maximum number of items (default: 20).
            
        Returns:
            List of options with highest profit rates, including:
            symbol, due_date, financial_volume, profit_rate_if_excercised, type,
            underlying, updated_at, ve_over_strike, days_to_maturity, strike,
            spot_strike_ratio, name, sector.
            Returns None if no data available.
            
        Example:
            >>> best_calls = client.market.statistics.get_best_covered_options_rates('CALL', limit=10)
        """
        params = {'limit': limit}
        return self.client.get(
            f'/market/statistics/realtime/best_covered_options_rates/{option_type}',
            params=params
        )
    
    def get_highest_options_variation(
        self,
        option_type: str,
        limit: int = 20
    ) -> Optional[List[Dict]]:
        """
        Get options with highest price variations.
        
        Args:
            option_type: Option type ('CALL' or 'PUT').
            limit: Maximum number of items (default: 20).
            
        Returns:
            List of options with highest variations, including:
            symbol, due_date, financial_volume, profit_rate_if_excercised, type,
            underlying, updated_at, variation, ve_over_strike, days_to_maturity,
            strike, name, sector.
            Returns None if no data available.
            
        Example:
            >>> top_variations = client.market.statistics.get_highest_options_variation('PUT', limit=15)
        """
        params = {'limit': limit}
        return self.client.get(
            f'/market/statistics/realtime/highest_options_variation/{option_type}',
            params=params
        )
    
    def get_m9_m21_ranking(
        self,
        limit: int = 20,
        sort: str = 'asc',
        financial_volume_start: int = 0,
        days: int = 3650
    ) -> Optional[List[Dict]]:
        """
        Get stocks with highest/lowest trends based on 9-day and 21-day moving averages.
        
        Args:
            limit: Maximum number of items (default: 20).
            sort: Sort order ('asc' for lowest trends, 'desc' for highest trends, default: 'asc').
            financial_volume_start: Minimum financial volume (default: 0).
            days: Maximum days since last update (default: 3650).
            
        Returns:
            List of stocks with trend information, including:
            symbol, updated_at, cnpj, attribute (value and trend), attribute_name,
            short_name, name, sector.
            Returns None if no data available.
            
        Example:
            >>> trends = client.market.statistics.get_m9_m21_ranking(sort='desc', limit=30)
        """
        params = {
            'limit': limit,
            'sort': sort,
            'financial_volume_start': financial_volume_start,
            'days': days
        }
        return self.client.get('/market/statistics/ranking/m9_m21', params=params)
    
    def get_correl_ibov_ranking(
        self,
        limit: int = 20,
        sort: str = 'asc',
        financial_volume_start: int = 0,
        days: int = 3650
    ) -> Optional[List[Dict]]:
        """
        Get stocks ordered by correlation with IBOV.
        
        Args:
            limit: Maximum number of items (default: 20).
            sort: Sort order ('asc' for lowest correlation, 'desc' for highest, default: 'asc').
            financial_volume_start: Minimum financial volume (default: 0).
            days: Maximum days since last update (default: 3650).
            
        Returns:
            List of stocks with IBOV correlation data.
            Returns None if no data available.
            
        Example:
            >>> correlations = client.market.statistics.get_correl_ibov_ranking(sort='desc')
        """
        params = {
            'limit': limit,
            'sort': sort,
            'financial_volume_start': financial_volume_start,
            'days': days
        }
        return self.client.get('/market/statistics/ranking/correl_ibov', params=params)
    
    def get_fundamental_ranking(
        self,
        attribute: str,
        group_by: Optional[str] = None,
        limit: int = 20,
        sort: str = 'asc',
        financial_volume_start: int = 0
    ) -> Optional[List[Dict]]:
        """
        Get companies ranked by a fundamentalist attribute.
        
        Args:
            attribute: Fundamentalist attribute. Options include:
                date, cash_and_equivalents, ebit, earnings, market_cap,
                earnings_over_ebit, earnings_over_netrevenue, roic, roa, roe,
                gross_margin, ebit_margin, net_margin, interest_coverage_ratio,
                current_ratio, ev, ev_over_ebit, profit_per_share,
                price_over_profit_per_share, magic_formula.
            group_by: Group by property ('sector' to group by sector).
            limit: Maximum number of items (default: 20).
            sort: Sort order ('asc' for lowest, 'desc' for highest, default: 'asc').
            financial_volume_start: Minimum financial volume (default: 0).
            
        Returns:
            List of companies ranked by the specified attribute.
            Can be grouped by sector if group_by='sector'.
            Returns None if no data available.
            
        Example:
            >>> roe_ranking = client.market.statistics.get_fundamental_ranking('roe', sort='desc')
        """
        params = {
            'limit': limit,
            'sort': sort,
            'financial_volume_start': financial_volume_start
        }
        if group_by:
            params['group_by'] = group_by
        
        return self.client.get(f'/market/statistics/ranking/{attribute}', params=params)
    
    def get_oplab_score_ranking(
        self,
        score_start: Optional[int] = None,
        financial_volume_start: int = 0,
        group_by: Optional[str] = None,
        sort: str = 'asc',
        limit: int = 20
    ) -> Optional[List[Dict]]:
        """
        Get stocks ranked by OpLab score.
        
        Args:
            score_start: Minimum OpLab score.
            financial_volume_start: Minimum financial volume (default: 0).
            group_by: Group by property ('sector' to group by sector).
            sort: Sort order ('asc' for lowest scores, 'desc' for highest, default: 'asc').
            limit: Maximum number of items (default: 20).
            
        Returns:
            List of stocks ranked by OpLab score.
            Can be grouped by sector if group_by='sector'.
            Returns None if no data available.
            
        Example:
            >>> top_scores = client.market.statistics.get_oplab_score_ranking(sort='desc', limit=50)
        """
        params = {
            'financial_volume_start': financial_volume_start,
            'sort': sort,
            'limit': limit
        }
        if score_start is not None:
            params['score_start'] = score_start
        if group_by:
            params['group_by'] = group_by
        
        return self.client.get('/market/statistics/ranking/oplab_score', params=params)

