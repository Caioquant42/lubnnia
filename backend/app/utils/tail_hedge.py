"""
Tail Hedge Strategy Module
Implements tail hedging strategy for cryptocurrency portfolios
Combines long puts (delta -0.10 to -0.20, shorter maturity) with short calls (delta 0.05, longer maturity)
to provide portfolio protection with flexible financing
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import json

# Handle both direct execution and module import
try:
    from .bybit_options import BybitOptionsClient
except ImportError:
    from bybit_options import BybitOptionsClient

class TailHedgeStrategy:
    """
    Calculates tail hedge strategies for cryptocurrency portfolios
    Supports flexible portfolio hedge percentage and financing percentage
    """
    
    def __init__(self, exchange: str = 'bybit'):
        """
        Initialize tail hedge strategy
        Args:
            exchange (str): 'bybit' (binance support can be added later)
        """
        self.exchange = exchange.lower()
        
        if self.exchange == 'bybit':
            self.client = BybitOptionsClient()
        else:
            raise ValueError(f"Unsupported exchange: {exchange}. Currently only 'bybit' is supported.")
    
    def calculate_tail_hedge_strategies(
        self,
        underlying: str,
        portfolio_size: float,
        portfolio_type: str,  # 'units' or 'usd'
        portfolio_hedge_percentage: float = 0.50,  # 50%, 75%, or 100% (0.50, 0.75, 1.0)
        financing_percentage: float = 0.50,  # 50%, 75%, or 100% (0.50, 0.75, 1.0)
        put_delta_min: float = -0.20,
        put_delta_max: float = -0.10,
        call_delta: float = 0.05,
        put_min_days: int = 30,
        put_max_days: int = 60,
        call_min_days: int = 60,
        call_max_days: int = 90,
        min_maturity_diff: int = 7,  # Minimum days between put and call expiry
    ) -> Dict[str, Any]:
        """
        Calculate tail hedge strategies for a crypto portfolio
        Args:
            underlying (str): Crypto asset (BTC, ETH, SOL)
            portfolio_size (float): Portfolio size (units or USD value)
            portfolio_type (str): 'units' or 'usd'
            portfolio_hedge_percentage (float): Percentage of portfolio to hedge (0.50, 0.75, 1.0)
            financing_percentage (float): Percentage of put costs to finance (0.50, 0.75, 1.0)
            put_delta_min (float): Minimum put delta (default: -0.20)
            put_delta_max (float): Maximum put delta (default: -0.10)
            call_delta (float): Target call delta (default: 0.05)
            put_min_days (int): Minimum days to expiry for puts
            put_max_days (int): Maximum days to expiry for puts
            call_min_days (int): Minimum days to expiry for calls
            call_max_days (int): Maximum days to expiry for calls
            min_maturity_diff (int): Minimum days difference between call and put expiry
        Returns:
            dict: Tail hedge strategies with metrics
        """
        # Fetch options data
        print(f"Fetching options data for {underlying}...")
        
        # Fetch puts with shorter maturity
        puts_data = self.client.filter_options_by_expiry(
            base_coin=underlying,
            min_days=put_min_days,
            max_days=put_max_days
        )
        
        # Fetch calls with longer maturity
        calls_data = self.client.filter_options_by_expiry(
            base_coin=underlying,
            min_days=call_min_days,
            max_days=call_max_days
        )
        
        puts = puts_data.get('puts', [])
        calls = calls_data.get('calls', [])
        
        print(f"Found {len(puts)} puts and {len(calls)} calls")
        
        # Get spot price
        spot_price = self.client.get_spot_price(underlying)
        if not spot_price:
            # Fallback: estimate from option prices
            if puts:
                spot_price = sum(p['strike'] for p in puts[:5]) / 5
            elif calls:
                spot_price = sum(c['strike'] for c in calls[:5]) / 5
            else:
                spot_price = 0
        
        print(f"Spot price: ${spot_price}")
        
        # Calculate portfolio protection
        if portfolio_type == 'units':
            portfolio_value = portfolio_size * spot_price
            put_quantity = portfolio_size * portfolio_hedge_percentage
        else:
            portfolio_value = portfolio_size
            put_quantity = (portfolio_value * portfolio_hedge_percentage) / spot_price
        
        protection_target = portfolio_value * portfolio_hedge_percentage
        
        print(f"Portfolio value: ${portfolio_value:,.2f}")
        print(f"Protection target ({portfolio_hedge_percentage*100}%): ${protection_target:,.2f}")
        print(f"Put quantity needed: {put_quantity:.2f}")
        
        # Filter puts by delta range
        valid_puts = []
        for put in puts:
            put_delta = put.get('delta', 0)
            put_price = put.get('mark_price') or put.get('bid', 0) or put.get('ask', 0)
            
            if (put_delta_min <= put_delta <= put_delta_max and put_price > 0):
                valid_puts.append(put)
        
        # Filter calls by delta (target 0.05, allow small range)
        valid_calls = []
        call_delta_tolerance = 0.02  # Allow ±0.02 tolerance
        for call in calls:
            call_delta_val = call.get('delta', 0)
            call_price = call.get('mark_price') or call.get('bid', 0) or call.get('ask', 0)
            
            if (abs(call_delta_val - call_delta) <= call_delta_tolerance and call_price > 0):
                valid_calls.append(call)
        
        print(f"Valid puts (delta {put_delta_min} to {put_delta_max}): {len(valid_puts)}")
        print(f"Valid calls (delta ~{call_delta}): {len(valid_calls)}")
        
        if not valid_puts or not valid_calls:
            return {
                'metadata': {
                    'total_count': 0,
                    'underlying': underlying,
                    'exchange': self.exchange,
                    'spot_price': spot_price,
                    'portfolio_size': portfolio_size,
                    'portfolio_type': portfolio_type,
                    'portfolio_value_usd': portfolio_value,
                    'portfolio_hedge_percentage': portfolio_hedge_percentage,
                    'financing_percentage': financing_percentage,
                    'protection_target': protection_target,
                    'timestamp': datetime.now().isoformat()
                },
                'strategies': []
            }
        
        # Generate tail hedge combinations
        strategies = self._generate_tail_hedge_combinations(
            valid_puts, valid_calls, spot_price, put_quantity,
            portfolio_value, protection_target, portfolio_hedge_percentage,
            financing_percentage, min_maturity_diff
        )
        
        print(f"Generated {len(strategies)} tail hedge strategies")
        
        # Sort strategies by net cost (ascending - lower cost is better)
        strategies.sort(key=lambda x: x['strategy_metrics']['net_cost'])
        
        return {
            'metadata': {
                'total_count': len(strategies),
                'underlying': underlying,
                'exchange': self.exchange,
                'spot_price': spot_price,
                'portfolio_size': portfolio_size,
                'portfolio_type': portfolio_type,
                'portfolio_value_usd': portfolio_value,
                'portfolio_hedge_percentage': portfolio_hedge_percentage,
                'financing_percentage': financing_percentage,
                'protection_target': protection_target,
                'timestamp': datetime.now().isoformat()
            },
            'strategies': strategies
        }
    
    def _generate_tail_hedge_combinations(
        self,
        puts: List[Dict],
        calls: List[Dict],
        spot_price: float,
        put_quantity: float,
        portfolio_value: float,
        protection_target: float,
        portfolio_hedge_percentage: float,
        financing_percentage: float,
        min_maturity_diff: int
    ) -> List[Dict]:
        """
        Generate tail hedge strategy combinations
        """
        strategies = []
        
        for put in puts:
            put_price = put.get('mark_price') or put.get('bid', 0) or put.get('ask', 0)
            if put_price <= 0:
                continue
            
            put_days = put.get('days_to_expiry', 0)
            total_put_cost = put_price * put_quantity
            
            # Target call premium to finance selected percentage of put costs
            target_call_premium = total_put_cost * financing_percentage
            
            for call in calls:
                call_price = call.get('mark_price') or call.get('bid', 0) or call.get('ask', 0)
                if call_price <= 0:
                    continue
                
                call_days = call.get('days_to_expiry', 0)
                
                # Check maturity difference requirement
                if call_days <= put_days + min_maturity_diff:
                    continue
                
                # Calculate number of calls needed to finance target percentage
                call_quantity_needed = target_call_premium / call_price
                
                # Calculate actual financing
                actual_call_premium = call_price * call_quantity_needed
                financing_ratio = actual_call_premium / total_put_cost if total_put_cost > 0 else 0
                
                # Allow 95% tolerance for financing target
                if financing_ratio >= financing_percentage * 0.95:
                    # Valid strategy found
                    net_cost = total_put_cost - actual_call_premium
                    
                    # Calculate strategy metrics
                    strategy_metrics = self._calculate_strategy_metrics(
                        put, call, spot_price, put_quantity, call_quantity_needed,
                        total_put_cost, actual_call_premium, net_cost,
                        financing_ratio, portfolio_value, protection_target,
                        portfolio_hedge_percentage, financing_percentage
                    )
                    
                    # Calculate payoff function
                    payoff_function = self._calculate_payoff_function(
                        put, call, spot_price, put_quantity, call_quantity_needed,
                        put_price, call_price, net_cost
                    )
                    
                    strategies.append({
                        'put': {
                            'symbol': put.get('symbol'),
                            'underlying': put.get('underlying'),
                            'strike': put.get('strike'),
                            'delta': put.get('delta'),
                            'price': put_price,
                            'expiry_date': put.get('expiry_date'),
                            'days_to_expiry': put_days,
                            'gamma': put.get('gamma'),
                            'vega': put.get('vega'),
                            'theta': put.get('theta'),
                            'iv': put.get('iv')
                        },
                        'call': {
                            'symbol': call.get('symbol'),
                            'underlying': call.get('underlying'),
                            'strike': call.get('strike'),
                            'delta': call.get('delta'),
                            'price': call_price,
                            'expiry_date': call.get('expiry_date'),
                            'days_to_expiry': call_days,
                            'gamma': call.get('gamma'),
                            'vega': call.get('vega'),
                            'theta': call.get('theta'),
                            'iv': call.get('iv')
                        },
                        'strategy_metrics': strategy_metrics,
                        'payoff_function': payoff_function
                    })
        
        return strategies
    
    def _calculate_strategy_metrics(
        self,
        put: Dict,
        call: Dict,
        spot_price: float,
        put_quantity: float,
        call_quantity: float,
        total_put_cost: float,
        total_call_premium: float,
        net_cost: float,
        financing_ratio: float,
        portfolio_value: float,
        protection_target: float,
        portfolio_hedge_percentage: float,
        financing_percentage: float
    ) -> Dict[str, Any]:
        """
        Calculate strategy metrics
        """
        put_strike = put.get('strike', 0)
        call_strike = call.get('strike', 0)
        
        # Calculate max loss protected (from spot to put strike)
        max_loss_protected = (spot_price - put_strike) * put_quantity if spot_price > put_strike else 0
        
        # Breakeven price (where put protection kicks in)
        breakeven_price = put_strike
        
        return {
            'put_quantity': round(put_quantity, 2),
            'call_quantity': round(call_quantity, 2),
            'total_put_cost': round(total_put_cost, 2),
            'total_call_premium': round(total_call_premium, 2),
            'net_cost': round(net_cost, 2),
            'financing_ratio': round(financing_ratio, 4),
            'financing_percentage': financing_percentage,
            'protection_coverage': round(protection_target, 2),
            'protection_percentage': portfolio_hedge_percentage,
            'max_loss_protected': round(max_loss_protected, 2),
            'breakeven_price': round(breakeven_price, 2),
            'put_strike': put_strike,
            'call_strike': call_strike
        }
    
    def _calculate_payoff_function(
        self,
        put: Dict,
        call: Dict,
        spot_price: float,
        put_quantity: float,
        call_quantity: float,
        put_price: float,
        call_price: float,
        net_cost: float
    ) -> Dict[str, List[float]]:
        """
        Calculate payoff function for tail hedge strategy
        """
        put_strike = put.get('strike', 0)
        call_strike = call.get('strike', 0)
        
        # Define price range for payoff calculation
        min_price = min(put_strike * 0.7, spot_price * 0.7)
        max_price = max(call_strike * 1.3, spot_price * 1.3)
        
        price_points = []
        pnl_points = []
        
        # Generate 50 price points
        for i in range(51):
            price = min_price + (max_price - min_price) * i / 50
            price_points.append(round(price, 2))
            
            # Calculate P&L at this price
            # Long put payoff: max(put_strike - price, 0) - put_price
            put_pnl = (max(put_strike - price, 0) - put_price) * put_quantity
            
            # Short call payoff: call_price - max(price - call_strike, 0)
            call_pnl = (call_price - max(price - call_strike, 0)) * call_quantity
            
            # Total P&L (net of initial cost)
            total_pnl = put_pnl + call_pnl
            pnl_points.append(round(total_pnl, 2))
        
        # Find breakeven points
        breakeven_points = self._find_breakeven_points(price_points, pnl_points)
        
        return {
            'price_points': price_points,
            'pnl_points': pnl_points,
            'breakeven_points': breakeven_points,
            'max_profit': max(pnl_points),
            'max_loss': min(pnl_points)
        }
    
    def _find_breakeven_points(self, prices: List[float], pnls: List[float]) -> List[float]:
        """
        Find breakeven points where P&L crosses zero
        """
        breakevens = []
        
        for i in range(len(pnls) - 1):
            if pnls[i] * pnls[i + 1] <= 0:  # Sign change
                # Linear interpolation to find exact breakeven
                if pnls[i + 1] != pnls[i]:
                    ratio = -pnls[i] / (pnls[i + 1] - pnls[i])
                    breakeven_price = prices[i] + ratio * (prices[i + 1] - prices[i])
                    breakevens.append(round(breakeven_price, 2))
        
        return breakevens


def get_tail_hedge_analysis(
    underlying: str = 'BTC',
    exchange: str = 'bybit',
    portfolio_size: float = 1000,
    portfolio_type: str = 'units',
    portfolio_hedge_percentage: float = 0.50,
    financing_percentage: float = 0.50,
    put_delta_min: float = -0.20,
    put_delta_max: float = -0.10,
    call_delta: float = 0.05,
    put_min_days: int = 30,
    put_max_days: int = 60,
    call_min_days: int = 60,
    call_max_days: int = 90,
    min_maturity_diff: int = 7
) -> Dict[str, Any]:
    """
    Main function to get tail hedge analysis
    Args:
        underlying (str): Crypto asset (BTC, ETH, SOL)
        exchange (str): 'bybit'
        portfolio_size (float): Portfolio size (units or USD)
        portfolio_type (str): 'units' or 'usd'
        portfolio_hedge_percentage (float): Percentage of portfolio to hedge (0.50, 0.75, 1.0)
        financing_percentage (float): Percentage of put costs to finance (0.50, 0.75, 1.0)
        put_delta_min (float): Minimum put delta
        put_delta_max (float): Maximum put delta
        call_delta (float): Target call delta
        put_min_days (int): Minimum days to expiry for puts
        put_max_days (int): Maximum days to expiry for puts
        call_min_days (int): Minimum days to expiry for calls
        call_max_days (int): Maximum days to expiry for calls
        min_maturity_diff (int): Minimum days difference between call and put expiry
    Returns:
        dict: Tail hedge strategies
    """
    strategy_calculator = TailHedgeStrategy(exchange=exchange)
    return strategy_calculator.calculate_tail_hedge_strategies(
        underlying=underlying,
        portfolio_size=portfolio_size,
        portfolio_type=portfolio_type,
        portfolio_hedge_percentage=portfolio_hedge_percentage,
        financing_percentage=financing_percentage,
        put_delta_min=put_delta_min,
        put_delta_max=put_delta_max,
        call_delta=call_delta,
        put_min_days=put_min_days,
        put_max_days=put_max_days,
        call_min_days=call_min_days,
        call_max_days=call_max_days,
        min_maturity_diff=min_maturity_diff
    )

