"""
Option Pricing Module using Moving Block Bootstrap

Calculates theoretical option prices using MBB methodology for probability estimation.
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
import logging

logger = logging.getLogger(__name__)


class OptionPricer:
    """Option pricing using Moving Block Bootstrap methodology"""
    
    def __init__(self, mbb_core, data_gatherer):
        """
        Initialize Option Pricer
        
        Parameters:
        -----------
        mbb_core : MBBCore
            Moving Block Bootstrap core functions
        data_gatherer : DataGatherer
            Data gathering utilities
        """
        self.mbb_core = mbb_core
        self.data_gatherer = data_gatherer
    
    def price_options(self, ticker, expiry_date=None, n_bootstrap=1000, 
                     iterations=5000, risk_free_rate=0.1375):
        """
        Calculate theoretical option prices for all strikes
        
        Parameters:
        -----------
        ticker : str
            Stock ticker (e.g., 'PETR4')
        expiry_date : str, optional
            Expiry date. If None, uses first available
        n_bootstrap : int
            Number of bootstrap samples
        iterations : int
            Number of Monte Carlo iterations
        risk_free_rate : float
            Risk-free rate (default: 13.75% - current CDI)
            
        Returns:
        --------
        dict
            Complete pricing results with strike grid
        """
        logger.info(f"Pricing options for {ticker}, expiry: {expiry_date}")
        
        # Get options chain
        options_chain = self.data_gatherer.get_options_chain(ticker)
        
        if not options_chain:
            raise ValueError(f"No options available for {ticker}")
        
        # Select expiry date
        if expiry_date is None:
            expiry_date = list(options_chain.keys())[0]
        elif expiry_date not in options_chain:
            raise ValueError(f"Expiry {expiry_date} not found. Available: {list(options_chain.keys())}")
        
        # Get current price and historical data
        ticker_with_suffix = ticker if ticker.endswith('.SA') else f"{ticker}.SA"
        current_prices = self.data_gatherer.get_current_prices([ticker_with_suffix])
        S0 = current_prices.get(ticker_with_suffix)
        
        if S0 is None:
            raise ValueError(f"Could not get current price for {ticker}")
        
        # Get historical data for MBB
        hist_data = self.data_gatherer.get_data(
            asset_list=[ticker_with_suffix],
            period='252d'  # 1 year of trading days
        )
        
        if hist_data.empty:
            raise ValueError(f"No historical data for {ticker}")
        
        # Calculate log returns
        log_returns = hist_data[ticker_with_suffix].pct_change().dropna()
        
        # Run MBB and Monte Carlo
        logger.info("Running Moving Block Bootstrap...")
        bootstrap_samples = self.mbb_core.moving_block_bootstrap(
            log_returns, 
            n_bootstrap=n_bootstrap,
            sample_size=63
        )
        
        logger.info("Running Monte Carlo simulation...")
        final_prices = self.mbb_core.monte_carlo_simulation(
            S0,
            bootstrap_samples,
            iterations=iterations
        )
        
        # Calculate days to expiry
        from datetime import datetime
        expiry_dt = datetime.strptime(expiry_date, '%Y-%m-%d')
        days_to_expiry = (expiry_dt - datetime.now()).days
        T = days_to_expiry / 252.0  # Convert to years
        
        if T <= 0:
            raise ValueError(f"Expiry date {expiry_date} has already passed")
        
        # Get option chain data
        calls_df = options_chain[expiry_date]['calls']
        puts_df = options_chain[expiry_date]['puts']
        
        # Price all strikes
        call_prices = self._price_call_options(
            calls_df, final_prices, S0, risk_free_rate, T
        )
        put_prices = self._price_put_options(
            puts_df, final_prices, S0, risk_free_rate, T
        )
        
        # Calculate statistics
        stats = self._calculate_statistics(final_prices, bootstrap_samples)
        
        result = {
            'ticker': ticker,
            'current_price': S0,
            'expiry_date': expiry_date,
            'days_to_expiry': days_to_expiry,
            'risk_free_rate': risk_free_rate,
            'calls': call_prices,
            'puts': put_prices,
            'statistics': stats,
            'final_prices_sample': final_prices[:100].tolist()  # Sample for visualization
        }
        
        logger.info(
            f"Priced {len(call_prices)} call strikes and {len(put_prices)} put strikes"
        )
        
        return result
    
    def _price_call_options(self, calls_df, final_prices, S0, r, T):
        """Price call options for all strikes"""
        results = []
        
        for _, row in calls_df.iterrows():
            strike = row['strike']
            market_price = row.get('lastPrice', 0)
            
            # Calculate theoretical price using Monte Carlo
            payoffs = np.maximum(0, final_prices - strike)
            expected_payoff = np.mean(payoffs)
            theoretical_price = np.exp(-r * T) * expected_payoff
            
            # Calculate probability of exercise
            prob_exercise = np.sum(final_prices > strike) / len(final_prices)
            
            # Calculate Greeks approximations
            greeks = self._calculate_greeks(
                S0, strike, T, r, final_prices, option_type='call'
            )
            
            result = {
                'strike': strike,
                'market_price': market_price,
                'theoretical_price': theoretical_price,
                'difference': market_price - theoretical_price,
                'pct_difference': ((market_price - theoretical_price) / theoretical_price * 100) if theoretical_price > 0 else 0,
                'prob_exercise': prob_exercise,
                'bid': row.get('bid', 0),
                'ask': row.get('ask', 0),
                'volume': row.get('volume', 0),
                'open_interest': row.get('openInterest', 0),
                'implied_volatility': row.get('impliedVolatility', 0),
                **greeks
            }
            
            results.append(result)
        
        return results
    
    def _price_put_options(self, puts_df, final_prices, S0, r, T):
        """Price put options for all strikes"""
        results = []
        
        for _, row in puts_df.iterrows():
            strike = row['strike']
            market_price = row.get('lastPrice', 0)
            
            # Calculate theoretical price using Monte Carlo
            payoffs = np.maximum(0, strike - final_prices)
            expected_payoff = np.mean(payoffs)
            theoretical_price = np.exp(-r * T) * expected_payoff
            
            # Calculate probability of exercise
            prob_exercise = np.sum(final_prices < strike) / len(final_prices)
            
            # Calculate Greeks approximations
            greeks = self._calculate_greeks(
                S0, strike, T, r, final_prices, option_type='put'
            )
            
            result = {
                'strike': strike,
                'market_price': market_price,
                'theoretical_price': theoretical_price,
                'difference': market_price - theoretical_price,
                'pct_difference': ((market_price - theoretical_price) / theoretical_price * 100) if theoretical_price > 0 else 0,
                'prob_exercise': prob_exercise,
                'bid': row.get('bid', 0),
                'ask': row.get('ask', 0),
                'volume': row.get('volume', 0),
                'open_interest': row.get('openInterest', 0),
                'implied_volatility': row.get('impliedVolatility', 0),
                **greeks
            }
            
            results.append(result)
        
        return results
    
    def _calculate_greeks(self, S0, K, T, r, final_prices, option_type='call'):
        """Calculate approximate option Greeks"""
        # Historical volatility from simulated prices
        returns = np.diff(final_prices) / final_prices[:-1]
        sigma = np.std(returns) * np.sqrt(252)
        
        # Black-Scholes d1 and d2
        d1 = (np.log(S0 / K) + (r + 0.5 * sigma**2) * T) / (sigma * np.sqrt(T)) if T > 0 and sigma > 0 else 0
        d2 = d1 - sigma * np.sqrt(T) if T > 0 and sigma > 0 else 0
        
        # Delta
        if option_type == 'call':
            delta = norm.cdf(d1) if T > 0 else (1 if S0 > K else 0)
        else:
            delta = norm.cdf(d1) - 1 if T > 0 else (-1 if S0 < K else 0)
        
        # Gamma
        gamma = norm.pdf(d1) / (S0 * sigma * np.sqrt(T)) if T > 0 and sigma > 0 else 0
        
        # Vega
        vega = S0 * norm.pdf(d1) * np.sqrt(T) / 100 if T > 0 else 0
        
        # Theta (approximate)
        if option_type == 'call':
            theta = (-(S0 * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - 
                    r * K * np.exp(-r * T) * norm.cdf(d2)) / 252 if T > 0 else 0
        else:
            theta = (-(S0 * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + 
                    r * K * np.exp(-r * T) * norm.cdf(-d2)) / 252 if T > 0 else 0
        
        return {
            'delta': delta,
            'gamma': gamma,
            'vega': vega,
            'theta': theta,
            'sigma': sigma
        }
    
    def _calculate_statistics(self, final_prices, bootstrap_samples):
        """Calculate MBB and Monte Carlo statistics"""
        return {
            'monte_carlo': {
                'mean': float(np.mean(final_prices)),
                'median': float(np.median(final_prices)),
                'std': float(np.std(final_prices)),
                'min': float(np.min(final_prices)),
                'max': float(np.max(final_prices)),
                'percentile_5': float(np.percentile(final_prices, 5)),
                'percentile_25': float(np.percentile(final_prices, 25)),
                'percentile_75': float(np.percentile(final_prices, 75)),
                'percentile_95': float(np.percentile(final_prices, 95)),
            },
            'bootstrap': {
                'n_samples': bootstrap_samples.shape[0],
                'sample_size': bootstrap_samples.shape[1],
                'mean_of_means': float(np.mean(np.mean(bootstrap_samples, axis=1))),
                'std_of_means': float(np.std(np.mean(bootstrap_samples, axis=1))),
                'mean_of_stds': float(np.mean(np.std(bootstrap_samples, axis=1))),
            }
        }

