"""
Crypto Collar Strategy Module
Adapts the existing collar strategy logic for cryptocurrency options
Supports Bybit options
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

class CryptoCollarStrategy:
    """
    Calculates collar strategies for cryptocurrency options
    Supports BTC, ETH, and other crypto assets
    """
    
    def __init__(self, exchange: str = 'bybit'):
        """
        Initialize crypto collar strategy
        Args:
            exchange (str): 'bybit' (binance support can be added later)
        """
        self.exchange = exchange.lower()
        
        if self.exchange == 'bybit':
            self.client = BybitOptionsClient()
        else:
            raise ValueError(f"Unsupported exchange: {exchange}. Currently only 'bybit' is supported.")
    
    def calculate_collar_strategy(
        self,
        underlying: str,
        min_days: int = 0,
        max_days: int = 90,
        min_gain_to_risk: float = 0.0
    ) -> Dict[str, Any]:
        """
        Calculate collar strategies for a crypto asset
        Args:
            underlying (str): Crypto asset (BTC, ETH, SOL)
            min_days (int): Minimum days to expiry
            max_days (int): Maximum days to expiry
            min_gain_to_risk (float): Minimum gain-to-risk ratio filter
        Returns:
            dict: Collar strategies organized by protection type and maturity
        """
        # Fetch options data
        print(f"Fetching options data for {underlying}...")
        options_data = self.client.filter_options_by_expiry(
            base_coin=underlying,
            min_days=min_days,
            max_days=max_days
        )
        
        calls = options_data.get('calls', [])
        puts = options_data.get('puts', [])
        
        print(f"Found {len(calls)} calls and {len(puts)} puts")
        
        # Count options with valid pricing
        valid_calls = [c for c in calls if (c.get('mark_price') or c.get('bid', 0) or c.get('ask', 0)) > 0]
        valid_puts = [p for p in puts if (p.get('mark_price') or p.get('bid', 0) or p.get('ask', 0)) > 0]
        
        print(f"Valid pricing: {len(valid_calls)} calls and {len(valid_puts)} puts")
        
        if not valid_calls or not valid_puts:
            return {
                'metadata': {
                    'total_count': 0,
                    'underlying': underlying,
                    'exchange': self.exchange,
                    'spot_price': 0,
                    'timestamp': datetime.now().isoformat()
                },
                'results': {}
            }
        
        # Get spot price
        spot_price = self.client.get_spot_price(underlying)
        if not spot_price:
            # Fallback: estimate from option prices
            spot_price = sum(c['strike'] for c in calls[:5]) / 5 if calls else 0
        
        print(f"Spot price: ${spot_price}")
        
        # Generate collar combinations
        strategies = self._generate_collar_combinations(calls, puts, spot_price)
        print(f"Generated {len(strategies)} collar strategies")
        
        # Count intrinsic vs OTM strategies
        intrinsic_count = sum(1 for s in strategies if s['strategy']['intrinsic_protection'])
        otm_count = len(strategies) - intrinsic_count
        print(f"Intrinsic protection strategies: {intrinsic_count}")
        print(f"OTM strategies: {otm_count}")
        
        # Filter by gain-to-risk ratio
        if min_gain_to_risk > 0:
            strategies = [s for s in strategies if s['strategy'].get('gain_to_risk_ratio', 0) >= min_gain_to_risk]
            print(f"After filtering: {len(strategies)} strategies")
        
        # Organize strategies by protection type and maturity
        organized = self._organize_strategies(strategies)
        
        return {
            'metadata': {
                'total_count': len(strategies),
                'underlying': underlying,
                'exchange': self.exchange,
                'spot_price': spot_price,
                'timestamp': datetime.now().isoformat()
            },
            'results': organized
        }
    
    def _generate_collar_combinations(
        self, 
        calls: List[Dict], 
        puts: List[Dict],
        spot_price: float
    ) -> List[Dict]:
        """
        Generate all valid collar strategy combinations
        Collar = Long underlying + Sell OTM call + Buy OTM put
        """
        strategies = []
        
        for call in calls:
            # Skip if no valid pricing (mark_price, bid, or ask must be > 0)
            call_price = call.get('mark_price') or call.get('bid', 0) or call.get('ask', 0)
            if call_price <= 0:
                continue
                
            for put in puts:
                # Skip if no valid pricing (mark_price, bid, or ask must be > 0)
                put_price = put.get('mark_price') or put.get('bid', 0) or put.get('ask', 0)
                if put_price <= 0:
                    continue
                    
                # Match by expiry date
                if call['expiry_date'] != put['expiry_date']:
                    continue
                
                # Collar structure: put strike < spot (call can be ITM or OTM)
                call_strike = call['strike']
                put_strike = put['strike']
                
                # Basic collar requirement: put strike must be below spot
                # Call can be either ITM (intrinsic protection) or OTM
                if not (put_strike < spot_price):
                    continue
                
                # Calculate strategy metrics
                strategy_data = self._calculate_strategy_metrics(
                    call, put, spot_price
                )
                
                if strategy_data:
                    strategies.append({
                        'call': call,
                        'put': put,
                        'strategy': strategy_data
                    })
        
        return strategies
    
    def _calculate_strategy_metrics(
        self, 
        call: Dict, 
        put: Dict,
        spot_price: float
    ) -> Optional[Dict]:
        """
        Calculate strategy metrics (gain, risk, ratios)
        Similar to the existing collar.py logic but adapted for crypto
        """
        # Prices - use mark price or fallback to bid/ask
        call_price = call.get('mark_price') or call.get('bid', 0) or call.get('ask', 0)
        put_price = put.get('mark_price') or put.get('bid', 0) or put.get('ask', 0)
        
        # Skip if no valid pricing (must have at least one valid price > 0)
        if call_price <= 0 or put_price <= 0:
            return None
        
        # Calculate intrinsic values (same logic as collar.py)
        call_intrinsic_value = max(spot_price - call['strike'], 0)
        put_intrinsic_value = max(put['strike'] - spot_price, 0)
        
        # Calculate extrinsic values
        call_extrinsic_value = max(call_price - call_intrinsic_value, 0)
        put_extrinsic_value = max(put_price - put_intrinsic_value, 0)
        
        # Calculate protection (intrinsic value / spot price)
        call_protection = call_intrinsic_value / spot_price if spot_price != 0 else 0
        put_protection = put_intrinsic_value / spot_price if spot_price != 0 else 0
        
        # Net credit/debit
        net_premium = call_price - put_price
        
        # Maximum gain: call strike - spot + net premium
        max_gain = (call['strike'] - spot_price) + net_premium
        
        # Maximum risk: spot - put strike - net premium
        max_risk = (spot_price - put['strike']) - net_premium
        
        # Gain-to-risk ratio
        gain_to_risk_ratio = max_gain / max_risk if max_risk > 0 else 0
        
        # Intrinsic protection logic (same as collar.py)
        # Intrinsic protection means the call has intrinsic value (ITM call)
        intrinsic_protection = call_protection > 0
        
        # Check for zero risk (net credit covers downside)
        zero_risk = net_premium >= (spot_price - put['strike'])
        
        # Calculate payoff function points
        payoff_points = self._calculate_payoff_function(
            call['strike'], put['strike'], spot_price, net_premium
        )
        
        # Combined score (weighted metrics)
        combined_score = (
            gain_to_risk_ratio * 0.4 +
            (1 if intrinsic_protection else 0) * 0.3 +
            (1 if zero_risk else 0) * 0.3
        )
        
        return {
            'underlying': call['underlying'],
            'spot_price': spot_price,
            'days_to_maturity': call['days_to_expiry'],
            'call_symbol': call['symbol'],
            'put_symbol': put['symbol'],
            'call_strike': call['strike'],
            'put_strike': put['strike'],
            'call_price': call_price,
            'put_price': put_price,
            'net_premium': net_premium,
            'max_gain': max_gain,
            'max_risk': max_risk,
            'gain_to_risk_ratio': gain_to_risk_ratio,
            'combined_score': combined_score,
            'intrinsic_protection': intrinsic_protection,
            'zero_risk': zero_risk,
            # Intrinsic/extrinsic values
            'call_intrinsic_value': call_intrinsic_value,
            'put_intrinsic_value': put_intrinsic_value,
            'call_extrinsic_value': call_extrinsic_value,
            'put_extrinsic_value': put_extrinsic_value,
            'call_protection': call_protection,
            'put_protection': put_protection,
            # Greeks
            'call_delta': call.get('delta'),
            'put_delta': put.get('delta'),
            'call_gamma': call.get('gamma'),
            'put_gamma': put.get('gamma'),
            'call_vega': call.get('vega'),
            'put_vega': put.get('vega'),
            'call_theta': call.get('theta'),
            'put_theta': put.get('theta'),
            # Payoff function
            'payoff_function': payoff_points,
        }
    
    def _calculate_payoff_function(
        self, 
        call_strike: float, 
        put_strike: float, 
        spot_price: float, 
        net_premium: float
    ) -> Dict[str, List[float]]:
        """
        Calculate payoff function points for collar strategy
        Collar = Long underlying + Sell call + Buy put
        
        Args:
            call_strike: Strike price of sold call
            put_strike: Strike price of bought put
            spot_price: Current spot price
            net_premium: Net premium received (call_price - put_price)
        
        Returns:
            dict: Payoff function with price points and corresponding P&L
        """
        # Define price range for payoff calculation
        min_price = min(put_strike * 0.7, spot_price * 0.7)
        max_price = max(call_strike * 1.3, spot_price * 1.3)
        
        # Generate price points
        price_points = []
        pnl_points = []
        
        # Create 20 price points from min to max
        for i in range(21):
            price = min_price + (max_price - min_price) * i / 20
            price_points.append(round(price, 2))
            
            # Calculate P&L at this price
            # Long underlying: price - spot_price
            underlying_pnl = price - spot_price
            
            # Short call: if price > call_strike, lose (price - call_strike)
            call_pnl = -max(price - call_strike, 0)
            
            # Long put: if price < put_strike, gain (put_strike - price)
            put_pnl = max(put_strike - price, 0)
            
            # Net premium received
            premium_pnl = net_premium
            
            # Total P&L
            total_pnl = underlying_pnl + call_pnl + put_pnl + premium_pnl
            pnl_points.append(round(total_pnl, 2))
        
        return {
            'price_points': price_points,
            'pnl_points': pnl_points,
            'breakeven_points': self._find_breakeven_points(price_points, pnl_points),
            'max_profit': max(pnl_points),
            'max_loss': min(pnl_points),
            'profit_range': {
                'start': put_strike,
                'end': call_strike
            }
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
    
    def _organize_strategies(self, strategies: List[Dict]) -> Dict:
        """
        Organize strategies by protection type and maturity buckets
        """
        organized = {
            'intrinsic': {
                'less_than_14_days': [],
                'between_15_and_30_days': [],
                'between_30_and_60_days': [],
                'more_than_60_days': []
            },
            'otm': {
                'less_than_14_days': [],
                'between_15_and_30_days': [],
                'between_30_and_60_days': [],
                'more_than_60_days': []
            }
        }
        
        for strategy in strategies:
            days = strategy['strategy']['days_to_maturity']
            protection_type = 'intrinsic' if strategy['strategy']['intrinsic_protection'] else 'otm'
            
            if days < 15:
                bucket = 'less_than_14_days'
            elif days <= 30:
                bucket = 'between_15_and_30_days'
            elif days <= 60:
                bucket = 'between_30_and_60_days'
            else:
                bucket = 'more_than_60_days'
            
            organized[protection_type][bucket].append(strategy)
        
        # Sort each bucket by combined_score descending
        for protection_type in organized:
            for bucket in organized[protection_type]:
                organized[protection_type][bucket].sort(
                    key=lambda x: x['strategy']['combined_score'],
                    reverse=True
                )
        
        return organized


def get_crypto_collar_analysis(
    underlying: str = 'BTC',
    exchange: str = 'bybit',
    min_days: int = 0,
    max_days: int = 90,
    min_gain_to_risk: float = 0.0
) -> Dict[str, Any]:
    """
    Main function to get crypto collar analysis
    Args:
        underlying (str): Crypto asset (BTC, ETH, SOL)
        exchange (str): 'bybit'
        min_days (int): Minimum days to expiry
        max_days (int): Maximum days to expiry
        min_gain_to_risk (float): Minimum gain-to-risk ratio
    Returns:
        dict: Collar strategies
    """
    strategy_calculator = CryptoCollarStrategy(exchange=exchange)
    return strategy_calculator.calculate_collar_strategy(
        underlying=underlying,
        min_days=min_days,
        max_days=max_days,
        min_gain_to_risk=min_gain_to_risk
    )


def save_crypto_collar_to_json(data: Dict[str, Any], underlying: str, export_directory: str):
    """
    Save crypto collar analysis results to JSON file
    Args:
        data (dict): Collar analysis results
        underlying (str): Crypto asset symbol
        export_directory (str): Path to export directory
    """
    # Ensure export directory exists
    os.makedirs(export_directory, exist_ok=True)
    
    # Define file path
    filename = f"crypto_collar_{underlying.lower()}_organized.json"
    file_path = os.path.join(export_directory, filename)
    
    # Save the data to file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"✅ Crypto collar data saved to {file_path}")
    print(f"   Total strategies: {data['metadata']['total_count']}")
    print(f"   Underlying: {data['metadata']['underlying']}")
    print(f"   Spot price: ${data['metadata']['spot_price']:.2f}")


def main():
    """
    Main execution function for crypto collar analysis
    Can be run directly: python -m backend.app.utils.crypto_collar
    """
    print("=" * 60)
    print("CRYPTO COLLAR STRATEGY ANALYZER")
    print("=" * 60)
    
    # Configuration
    cryptocurrencies = ['BTC', 'ETH']  # Add more as needed: 'SOL', etc.
    exchange = 'bybit'
    min_days = 0
    max_days = 90
    min_gain_to_risk = 0.5  # Filter for strategies with at least 0.5 gain-to-risk ratio
    
    # Get export directory path
    current_directory = os.path.dirname(os.path.abspath(__file__))
    export_directory = os.path.join(current_directory, "export")
    
    # Process each cryptocurrency
    for crypto in cryptocurrencies:
        print(f"\n{'─' * 60}")
        print(f"📊 Analyzing {crypto} collar strategies...")
        print(f"{'─' * 60}")
        
        try:
            # Get collar analysis
            results = get_crypto_collar_analysis(
                underlying=crypto,
                exchange=exchange,
                min_days=min_days,
                max_days=max_days,
                min_gain_to_risk=min_gain_to_risk
            )
            
            # Save to JSON
            save_crypto_collar_to_json(results, crypto, export_directory)
            
            # Print summary
            print(f"\n📈 Strategy Summary:")
            for protection_type in ['intrinsic', 'otm']:
                print(f"\n   {protection_type.upper()} Protection:")
                for bucket, strategies in results['results'][protection_type].items():
                    if strategies:
                        print(f"      • {bucket.replace('_', ' ').title()}: {len(strategies)} strategies")
                        # Show top strategy with payoff info
                        top = strategies[0]['strategy']
                        payoff = top.get('payoff_function', {})
                        print(f"        Top: G/R={top['gain_to_risk_ratio']:.2f}, "
                              f"Score={top['combined_score']:.3f}")
                        print(f"        Max Profit: ${payoff.get('max_profit', 0):,.2f}, "
                              f"Max Loss: ${payoff.get('max_loss', 0):,.2f}")
                        if payoff.get('breakeven_points'):
                            be_points = payoff['breakeven_points']
                            print(f"        Breakeven: ${be_points[0]:,.2f}" + 
                                  (f", ${be_points[1]:,.2f}" if len(be_points) > 1 else ""))
        
        except Exception as e:
            print(f"❌ Error analyzing {crypto}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'=' * 60}")
    print("✅ Analysis complete!")
    print(f"📁 Results saved to: {export_directory}")
    print("=" * 60)


if __name__ == "__main__":
    main()

