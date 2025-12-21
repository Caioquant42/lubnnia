"""
Bybit Options API Client (V5 Unified)
Handles fetching options data, Greeks, and market information from Bybit
"""
import requests
import hmac
import hashlib
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class BybitOptionsClient:
    """Client for Bybit Options API V5"""
    
    BASE_URL = "https://api.bybit.com"
    WS_URL = "wss://stream.bybit.com/v5/public/option"
    
    def __init__(self, api_key: str = None, api_secret: str = None):
        self.api_key = api_key or os.getenv('BYBIT_API_KEY')
        self.api_secret = api_secret or os.getenv('BYBIT_API_SECRET')
    
    def _generate_signature(self, params: Dict, timestamp: int) -> str:
        """Generate HMAC SHA256 signature for authenticated requests"""
        param_str = str(timestamp) + self.api_key + '5000' + '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
        signature = hmac.new(
            self.api_secret.encode('utf-8'),
            param_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _get_headers(self, params: Dict = None) -> Dict:
        """Generate headers for authenticated requests"""
        timestamp = int(time.time() * 1000)
        headers = {
            'X-BAPI-API-KEY': self.api_key,
            'X-BAPI-TIMESTAMP': str(timestamp),
            'X-BAPI-RECV-WINDOW': '5000'
        }
        
        if params and self.api_secret:
            headers['X-BAPI-SIGN'] = self._generate_signature(params, timestamp)
        
        return headers
    
    def get_instruments_info(self, symbol: str = None, base_coin: str = None) -> Dict:
        """
        Get instruments information for options
        Args:
            symbol (str): Specific option symbol
            base_coin (str): Base coin (BTC, ETH, SOL)
        Returns:
            dict: Instrument information
        """
        endpoint = f"{self.BASE_URL}/v5/market/instruments-info"
        params = {'category': 'option'}
        
        if symbol:
            params['symbol'] = symbol
        if base_coin:
            params['baseCoin'] = base_coin
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching instruments info: {str(e)}")
            return None
    
    def get_tickers(self, symbol: str = None, base_coin: str = None) -> Dict:
        """
        Get tickers with Greeks for options
        Args:
            symbol (str): Specific option symbol
            base_coin (str): Base coin (BTC, ETH, SOL)
        Returns:
            dict: Ticker data including Greeks (delta, gamma, vega, theta) and IV
        """
        endpoint = f"{self.BASE_URL}/v5/market/tickers"
        params = {'category': 'option'}
        
        if symbol:
            params['symbol'] = symbol
        if base_coin:
            params['baseCoin'] = base_coin
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching tickers: {str(e)}")
            return None
    
    def get_order_book(self, symbol: str, limit: int = 25) -> Dict:
        """
        Get order book for an option
        Args:
            symbol (str): Option symbol
            limit (int): Depth limit (1, 25, 50, 100, 200)
        Returns:
            dict: Order book with bids and asks
        """
        endpoint = f"{self.BASE_URL}/v5/market/orderbook"
        params = {
            'category': 'option',
            'symbol': symbol,
            'limit': limit
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching order book: {str(e)}")
            return None
    
    def get_recent_trades(self, symbol: str, limit: int = 100) -> Dict:
        """
        Get recent trades for an option
        Args:
            symbol (str): Option symbol
            limit (int): Number of trades (max 1000)
        Returns:
            dict: Recent trades
        """
        endpoint = f"{self.BASE_URL}/v5/market/recent-trade"
        params = {
            'category': 'option',
            'symbol': symbol,
            'limit': limit
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching trades: {str(e)}")
            return None
    
    def get_spot_price(self, base_coin: str = "BTC") -> Optional[float]:
        """
        Get current spot price for the base coin
        Args:
            base_coin (str): Base coin (BTC, ETH, SOL)
        Returns:
            float: Current spot price or None
        """
        endpoint = f"{self.BASE_URL}/v5/market/tickers"
        params = {
            'category': 'spot',
            'symbol': f"{base_coin}USDT"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            if data.get('retCode') == 0 and data.get('result', {}).get('list'):
                return float(data['result']['list'][0].get('lastPrice', 0))
            return None
        except Exception as e:
            print(f"Error fetching spot price: {str(e)}")
            return None
    
    def filter_options_by_expiry(
        self, 
        base_coin: str = "BTC", 
        min_days: int = 0, 
        max_days: int = 90
    ) -> Dict[str, List[Dict]]:
        """
        Filter options by days to expiry and separate calls/puts
        Args:
            base_coin (str): Base coin (BTC, ETH, SOL)
            min_days (int): Minimum days to expiry
            max_days (int): Maximum days to expiry
        Returns:
            dict: {'calls': [...], 'puts': [...]}
        """
        instruments = self.get_instruments_info(base_coin=base_coin)
        if not instruments or instruments.get('retCode') != 0:
            print(f"Failed to fetch instruments: {instruments}")
            return {'calls': [], 'puts': []}
        
        calls = []
        puts = []
        current_time = datetime.now()
        
        for instrument in instruments.get('result', {}).get('list', []):
            symbol = instrument.get('symbol', '')
            
            # Get expiry timestamp
            delivery_time = instrument.get('deliveryTime')
            if not delivery_time:
                continue
            
            try:
                expiry_date = datetime.fromtimestamp(int(delivery_time) / 1000)
                days_to_expiry = (expiry_date - current_time).days
                
                if min_days <= days_to_expiry <= max_days:
                    option_type = instrument.get('optionsType', '')
                    
                    # Parse strike from symbol (Bybit API bug: strikePrice returns 0)
                    # Symbol format: BTC-26DEC25-125000-C-USDT
                    strike = 0
                    try:
                        parts = symbol.split('-')
                        if len(parts) >= 3:
                            strike = float(parts[2])
                    except (ValueError, IndexError):
                        # Fallback to API field (which may be 0)
                        strike = float(instrument.get('strikePrice', 0))
                    
                    option_data = {
                        'symbol': symbol,
                        'underlying': base_coin,
                        'strike': strike,
                        'expiry_date': expiry_date.strftime('%Y-%m-%d'),
                        'days_to_expiry': days_to_expiry,
                        'type': 'CALL' if option_type == 'Call' else 'PUT',
                        'mark_price': 0,  # Will be filled by ticker data
                        'bid': 0,
                        'ask': 0,
                        'last_price': 0,
                        'volume': 0,
                        'delta': 0,
                        'gamma': 0,
                        'vega': 0,
                        'theta': 0,
                        'iv': 0,
                    }
                    
                    if option_type == 'Call':
                        calls.append(option_data)
                    else:
                        puts.append(option_data)
            except (ValueError, TypeError) as e:
                print(f"Error parsing instrument {symbol}: {str(e)}")
                continue
        
        # Fetch ticker data for all options
        tickers = self.get_tickers(base_coin=base_coin)
        if tickers and tickers.get('retCode') == 0:
            ticker_map = {
                ticker['symbol']: ticker 
                for ticker in tickers.get('result', {}).get('list', [])
            }
            
            # Update calls with ticker data
            for call in calls:
                ticker_data = ticker_map.get(call['symbol'], {})
                call['mark_price'] = float(ticker_data.get('markPrice', 0))
                call['bid'] = float(ticker_data.get('bid1Price', 0))
                call['ask'] = float(ticker_data.get('ask1Price', 0))
                call['last_price'] = float(ticker_data.get('lastPrice', 0))
                call['volume'] = float(ticker_data.get('volume24h', 0))
                call['delta'] = float(ticker_data.get('delta', 0))
                call['gamma'] = float(ticker_data.get('gamma', 0))
                call['vega'] = float(ticker_data.get('vega', 0))
                call['theta'] = float(ticker_data.get('theta', 0))
                call['iv'] = float(ticker_data.get('markIv', 0))
            
            # Update puts with ticker data
            for put in puts:
                ticker_data = ticker_map.get(put['symbol'], {})
                put['mark_price'] = float(ticker_data.get('markPrice', 0))
                put['bid'] = float(ticker_data.get('bid1Price', 0))
                put['ask'] = float(ticker_data.get('ask1Price', 0))
                put['last_price'] = float(ticker_data.get('lastPrice', 0))
                put['volume'] = float(ticker_data.get('volume24h', 0))
                put['delta'] = float(ticker_data.get('delta', 0))
                put['gamma'] = float(ticker_data.get('gamma', 0))
                put['vega'] = float(ticker_data.get('vega', 0))
                put['theta'] = float(ticker_data.get('theta', 0))
                put['iv'] = float(ticker_data.get('markIv', 0))
        
        return {'calls': calls, 'puts': puts}

