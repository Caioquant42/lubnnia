#!/usr/bin/env python3
"""
Portfolio Optimization System - Optimized Version

High-performance portfolio optimization using C implementations for computational bottlenecks.
Implements Moving Block Bootstrap, Monte Carlo simulation, and Newton-Raphson optimization.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import time
import os
import sys
import ctypes
from datetime import datetime
from itertools import combinations
from contextlib import contextmanager
from get_data_optimized import DataGatherer

# Configuration
plt.style.use('fivethirtyeight')
sns.set_palette('colorblind')
warnings.filterwarnings('ignore')
np.random.seed(1987)

@contextmanager
def suppress_output():
    """Suppress stdout/stderr during C function calls"""
    with open(os.devnull, "w") as devnull:
        old_stdout, old_stderr = sys.stdout, sys.stderr
        sys.stdout = sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout, sys.stderr = old_stdout, old_stderr

class PortfolioOptimizer:
    """Portfolio optimization using C implementations for performance"""
    
    def __init__(self, portfolio_size=4):
        self.portfolio_size = portfolio_size
        self.data_gatherer = DataGatherer(use_monte_carlo_selection=True, top_n_assets=15)
        self.c_lib = self._load_c_library()
        
    def _load_c_library(self):
        """Load and configure C library"""
        lib_path = './functions.so'
        if not os.path.exists(lib_path):
            raise RuntimeError("C library not found. Compile with: gcc -shared -fPIC -o functions.so functions.c -lm")
        
        c_lib = ctypes.CDLL(lib_path)
        self._setup_c_functions(c_lib)
        print("✅ C library loaded successfully")
        
        # Verify C functions are available
        required_functions = ['moving_block_bootstrap', 'monte_carlo_simulation', 'optimize_portfolio_newton_raphson']
        for func_name in required_functions:
            if not hasattr(c_lib, func_name):
                raise RuntimeError(f"C function {func_name} not found in library")
        
        print("✅ All C functions verified and ready")
        return c_lib
    
    def _setup_c_functions(self, c_lib):
        """Configure C function signatures"""
        # Moving block bootstrap
        c_lib.moving_block_bootstrap.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int, 
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        c_lib.moving_block_bootstrap.restype = ctypes.POINTER(ctypes.c_double)
        
        # Monte Carlo simulation
        c_lib.monte_carlo_simulation.argtypes = [
            ctypes.c_double, ctypes.POINTER(ctypes.c_double), 
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        c_lib.monte_carlo_simulation.restype = ctypes.POINTER(ctypes.c_double)
        
        # Newton-Raphson optimization
        c_lib.optimize_portfolio_newton_raphson.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_double), ctypes.c_double, ctypes.c_int, ctypes.c_double
        ]
        c_lib.optimize_portfolio_newton_raphson.restype = ctypes.POINTER(ctypes.c_double)
    
    def _prepare_data(self, data):
        """Clean and prepare data for C functions"""
        if hasattr(data, 'dropna'):
            data = data.dropna()
        return np.array(data)[~np.isnan(data)]
    
    def moving_block_bootstrap(self, log_returns, n_bootstrap=1000, sample_size=63, 
                             block_size=None, optimize_block_size=True):
        """Moving block bootstrap with optimized block size"""
        if block_size is None and optimize_block_size:
            block_size = self._choose_optimal_block_size(log_returns)
        elif block_size is None:
            block_size = 5
        
        log_returns_array = self._prepare_data(log_returns)
        c_array = (ctypes.c_double * len(log_returns_array))(*log_returns_array)
        
        with suppress_output():
            result_ptr = self.c_lib.moving_block_bootstrap(
                c_array, len(log_returns_array), n_bootstrap, sample_size, block_size, 1987
            )
        
        if not result_ptr:
            raise RuntimeError("Bootstrap failed - C function returned NULL")
        
        return np.ctypeslib.as_array(result_ptr, shape=(n_bootstrap, sample_size)).copy()
    
    def monte_carlo_simulation(self, S0, bootstrap_samples, iterations=5000):
        """Monte Carlo simulation using bootstrap samples"""
        if not isinstance(bootstrap_samples, np.ndarray) or bootstrap_samples.ndim != 2:
            raise ValueError("bootstrap_samples must be 2D numpy array")
        
        n_bootstrap, sample_size = bootstrap_samples.shape
        bootstrap_flat = bootstrap_samples.flatten()
        c_array = (ctypes.c_double * len(bootstrap_flat))(*bootstrap_flat)
        
        with suppress_output():
            result_ptr = self.c_lib.monte_carlo_simulation(
                ctypes.c_double(S0), c_array, n_bootstrap, sample_size, iterations, 1987
            )
        
        if not result_ptr:
            raise RuntimeError("Monte Carlo failed - C function returned NULL")
        
        return np.ctypeslib.as_array(result_ptr, shape=(iterations,)).copy()
    
    def optimize_portfolio_newton_raphson(self, arrival_values_df, asset_combination, 
                                        risk_free_rate=0.0, max_iterations=100, tolerance=1e-6):
        """Newton-Raphson portfolio optimization"""
        selected_values = arrival_values_df[list(asset_combination)]
        n_assets = len(asset_combination)
        
        arrival_flat = selected_values.values.flatten()
        c_arrival = (ctypes.c_double * len(arrival_flat))(*arrival_flat)
        
        initial_weights = np.ones(n_assets) / n_assets
        c_weights = (ctypes.c_double * n_assets)(*initial_weights)
        
        with suppress_output():
            result_ptr = self.c_lib.optimize_portfolio_newton_raphson(
                c_arrival, n_assets, len(selected_values), c_weights,
                ctypes.c_double(risk_free_rate), max_iterations, ctypes.c_double(tolerance)
            )
        
        if not result_ptr:
            raise RuntimeError("Newton-Raphson optimization failed")
        
        return np.ctypeslib.as_array(result_ptr, shape=(n_assets,)).copy()
    
    def _choose_optimal_block_size(self, log_returns, method='auto'):
        """Choose optimal block size using theoretical and empirical methods"""
        log_returns_array = self._prepare_data(log_returns)
        n = len(log_returns_array)
        
        if method == 'theoretical':
            return self._theoretical_block_size(n)
        elif method == 'empirical':
            return self._empirical_block_size(log_returns_array)
        else:  # auto
            theoretical = self._theoretical_block_size(n)
            empirical = self._empirical_block_size(log_returns_array)
            return min(theoretical, empirical)
    
    def _theoretical_block_size(self, n):
        """Calculate theoretical optimal block size"""
        b_opt = max(1, int(1.5 * (n ** (1/3))))
        return min(b_opt, n // 4)
    
    def _empirical_block_size(self, log_returns_array, test_statistic='mean'):
        """Calculate empirical optimal block size"""
        n = len(log_returns_array)
        max_block = min(max(2, int(2 * (n ** (1/3)))), n // 4)
        candidate_blocks = list(range(2, max_block + 1))
        
        volatilities = []
        for block_size in candidate_blocks:
            try:
                bootstrap_samples = self.moving_block_bootstrap(
                    log_returns_array, n_bootstrap=100, sample_size=min(63, n), 
                    block_size=block_size, optimize_block_size=False
                )
                
                if test_statistic == 'mean':
                    stats = np.mean(bootstrap_samples, axis=1)
                elif test_statistic == 'variance':
                    stats = np.var(bootstrap_samples, axis=1)
                else:  # sharpe
                    means, stds = np.mean(bootstrap_samples, axis=1), np.std(bootstrap_samples, axis=1)
                    stats = np.where(stds > 0, means / stds, 0)
                
                volatilities.append(np.std(stats))
            except:
                volatilities.append(np.inf)
        
        return candidate_blocks[np.argmin(volatilities)]
    
    def calculate_portfolio_returns(self, weights, arrival_values):
        """Calculate portfolio returns for given weights"""
        return np.dot(arrival_values.values, weights)
    
    def calculate_sharpe_ratio(self, portfolio_returns, risk_free_rate=0.0):
        """Calculate Sharpe ratio"""
        mean_return, std_return = np.mean(portfolio_returns), np.std(portfolio_returns)
        return (mean_return - risk_free_rate) / std_return if std_return > 0 else 0
    
    def optimize_single_portfolio(self, asset_combination, arrival_values_df, risk_free_rate=0.0):
        """Optimize a single portfolio combination"""
        try:
            optimal_weights = self.optimize_portfolio_newton_raphson(
                arrival_values_df, asset_combination, risk_free_rate
            )
            
            portfolio_values = self.calculate_portfolio_returns(optimal_weights, arrival_values_df[list(asset_combination)])
            
            return {
                'asset_combination': asset_combination,
                'success': True,
                'optimal_weights': optimal_weights,
                'optimal_sharpe': self.calculate_sharpe_ratio(portfolio_values, risk_free_rate),
                'optimal_mean': np.mean(portfolio_values),
                'optimal_std': np.std(portfolio_values),
                'method': 'Newton-Raphson'
            }
        except Exception as e:
            return {
                'asset_combination': asset_combination,
                'success': False,
                'optimal_sharpe': -np.inf,
                'error': str(e)
            }
    
    def optimize_all_combinations(self, portfolio_combinations, arrival_values_df, risk_free_rate=0.0):
        """Optimize all portfolio combinations"""
        print(f"Optimizing {len(portfolio_combinations)} portfolio combinations...")
        print("=" * 60)
        
        results = []
        for i, combination in enumerate(portfolio_combinations, 1):
            if i % 50 == 0:
                print(f"Progress: {i}/{len(portfolio_combinations)} combinations processed")
            
            result = self.optimize_single_portfolio(combination, arrival_values_df, risk_free_rate)
            results.append(result)
        
        return results
    
    def run_full_optimization(self):
        """Run complete portfolio optimization pipeline"""
        print("🚀 Starting Portfolio Optimization")
        print("=" * 50)
        
        # Get data
        print("📊 Gathering and processing data...")
        closing_prices = self.data_gatherer.get_data()
        log_returns = closing_prices.pct_change().dropna()
        current_prices = self.data_gatherer.get_current_prices()
        
        # Ensure we only use assets with both historical data and current prices
        available_assets = set(closing_prices.columns) & set(current_prices.keys())
        if len(available_assets) < self.portfolio_size:
            raise RuntimeError(f"Not enough assets with complete data ({len(available_assets)}) for portfolio size {self.portfolio_size}")
        
        # Filter data to only available assets
        log_returns = log_returns[list(available_assets)]
        print(f"📈 Using {len(available_assets)} assets with complete data")
        
        # Generate arrival values using Monte Carlo
        print("🎲 Running Monte Carlo simulations...")
        print(f"   Bootstrap: 1000 samples per asset")
        print(f"   Monte Carlo: 5000 iterations per asset")
        print(f"   Sample size: 63 days (consistent across all assets)")
        
        arrival_values = {}
        for i, asset in enumerate(log_returns.columns, 1):
            print(f"   Processing asset {i}/{len(log_returns.columns)}: {asset}")
            S0 = current_prices[asset]
            bootstrap_samples = self.moving_block_bootstrap(log_returns[asset], n_bootstrap=1000, sample_size=63)
            arrival_values[asset] = self.monte_carlo_simulation(S0, bootstrap_samples, iterations=5000)
            
            # Create Monte Carlo visualization for this asset
            self._create_asset_monte_carlo_plot(asset, S0, arrival_values[asset], bootstrap_samples)
        
        arrival_values_df = pd.DataFrame(arrival_values)
        
        # Check if we have enough assets
        n_assets = len(arrival_values_df.columns)
        if n_assets < self.portfolio_size:
            raise RuntimeError(f"Not enough assets available ({n_assets}) for portfolio size {self.portfolio_size}")
        
        # Generate portfolio combinations
        portfolio_combinations = list(combinations(arrival_values_df.columns, self.portfolio_size))
        print(f"📈 Testing {len(portfolio_combinations)} combinations of {self.portfolio_size} assets from {n_assets} total")
        
        # Optimize all combinations
        all_results = self.optimize_all_combinations(portfolio_combinations, arrival_values_df)
        
        # Find best portfolio
        successful_results = [r for r in all_results if r['success']]
        if not successful_results:
            raise RuntimeError("No successful portfolio optimizations")
        
        best_portfolio = max(successful_results, key=lambda x: x['optimal_sharpe'])
        
        print(f"\n🏆 Best Portfolio Found:")
        print(f"   Assets: {best_portfolio['asset_combination']}")
        print(f"   Sharpe Ratio: {best_portfolio['optimal_sharpe']:.6f}")
        print(f"   Expected Return: {best_portfolio['optimal_mean']:.6f}")
        print(f"   Volatility: {best_portfolio['optimal_std']:.6f}")
        
        # Save results
        self._save_results(best_portfolio, current_prices, arrival_values_df, all_results)
        self._create_visualizations(best_portfolio, current_prices, arrival_values_df, all_results)
        
        return best_portfolio, all_results
    
    def _save_results(self, best_portfolio, current_prices, arrival_values_df, all_results):
        """Save optimization results to CSV files"""
        # Best portfolio details
        best_details = pd.DataFrame({
            'Asset': best_portfolio['asset_combination'],
            'Weight': best_portfolio['optimal_weights'],
            'Current_Price': [current_prices[asset] for asset in best_portfolio['asset_combination']],
            'Allocation': best_portfolio['optimal_weights'] * 10000  # $10k portfolio
        })
        best_details.to_csv('best_portfolio_details.csv', index=False)
        
        # All results
        results_df = pd.DataFrame([
            {
                'Assets': str(r['asset_combination']),
                'Sharpe_Ratio': r.get('optimal_sharpe', -np.inf),
                'Expected_Return': r.get('optimal_mean', 0),
                'Volatility': r.get('optimal_std', 0),
                'Success': r['success']
            }
            for r in all_results
        ])
        results_df.to_csv('all_portfolio_results.csv', index=False)
        
        # Arrival values
        arrival_values_df.to_csv('arrival_values.csv')
        
        print("💾 Results saved to CSV files")
    
    def _create_visualizations(self, best_portfolio, current_prices, arrival_values_df, all_results):
        """Create comprehensive visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle('Portfolio Optimization Results', fontsize=16)
        
        # Portfolio weights
        assets = best_portfolio['asset_combination']
        weights = best_portfolio['optimal_weights']
        axes[0, 0].pie(weights, labels=assets, autopct='%1.1f%%', startangle=90)
        axes[0, 0].set_title('Optimal Portfolio Weights')
        
        # Sharpe ratio distribution
        sharpe_ratios = [r.get('optimal_sharpe', -np.inf) for r in all_results if r['success']]
        axes[0, 1].hist(sharpe_ratios, bins=30, alpha=0.7, edgecolor='black')
        axes[0, 1].axvline(best_portfolio['optimal_sharpe'], color='red', linestyle='--', 
                           label=f"Best: {best_portfolio['optimal_sharpe']:.3f}")
        axes[0, 1].set_xlabel('Sharpe Ratio')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].set_title('Sharpe Ratio Distribution')
        axes[0, 1].legend()
        
        # Risk-return scatter
        returns = [r.get('optimal_mean', 0) for r in all_results if r['success']]
        volatilities = [r.get('optimal_std', 0) for r in all_results if r['success']]
        axes[1, 0].scatter(volatilities, returns, alpha=0.6)
        axes[1, 0].scatter(best_portfolio['optimal_std'], best_portfolio['optimal_mean'], 
                           color='red', s=100, marker='*', label='Best Portfolio')
        axes[1, 0].set_xlabel('Volatility')
        axes[1, 0].set_ylabel('Expected Return')
        axes[1, 0].set_title('Risk-Return Profile')
        axes[1, 0].legend()
        
        # Asset correlation heatmap
        selected_returns = arrival_values_df[list(assets)]
        correlation_matrix = selected_returns.corr()
        im = axes[1, 1].imshow(correlation_matrix, cmap='coolwarm', aspect='auto')
        axes[1, 1].set_xticks(range(len(assets)))
        axes[1, 1].set_yticks(range(len(assets)))
        axes[1, 1].set_xticklabels(assets, rotation=45)
        axes[1, 1].set_yticklabels(assets)
        axes[1, 1].set_title('Asset Correlation Matrix')
        plt.colorbar(im, ax=axes[1, 1])
        
        plt.tight_layout()
        plt.savefig('portfolio_optimization_results.png', dpi=150, bbox_inches='tight')
        plt.close()
        
        print("📊 Visualizations saved to portfolio_optimization_results.png")
    
    def _create_asset_monte_carlo_plot(self, asset_name, S0, final_prices, bootstrap_samples):
        """Create comprehensive Monte Carlo visualization for a single asset"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle(f'Monte Carlo Analysis: {asset_name}', fontsize=16)
        
        # Plot 1: Final price distribution histogram
        axes[0, 0].hist(final_prices, bins=50, alpha=0.7, edgecolor='black', density=True)
        axes[0, 0].axvline(S0, color='red', linestyle='--', linewidth=2, label=f'Initial Price: {S0:.2f}')
        axes[0, 0].axvline(np.mean(final_prices), color='green', linestyle='--', linewidth=2, 
                           label=f'Mean: {np.mean(final_prices):.2f}')
        axes[0, 0].set_xlabel('Final Price')
        axes[0, 0].set_ylabel('Density')
        axes[0, 0].set_title('Final Price Distribution')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Plot 2: Return distribution
        returns = (final_prices - S0) / S0
        axes[0, 1].hist(returns, bins=50, alpha=0.7, edgecolor='black', density=True)
        axes[0, 1].axvline(0, color='red', linestyle='--', linewidth=2, label='No Change')
        axes[0, 1].axvline(np.mean(returns), color='green', linestyle='--', linewidth=2,
                           label=f'Mean Return: {np.mean(returns)*100:.2f}%')
        axes[0, 1].set_xlabel('Return')
        axes[0, 1].set_ylabel('Density')
        axes[0, 1].set_title('Return Distribution')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Plot 3: Sample price paths (first 100 simulations)
        n_paths = min(100, len(final_prices))
        sample_prices = final_prices[:n_paths]
        axes[1, 0].plot(range(n_paths), sample_prices, alpha=0.6, linewidth=0.5)
        axes[1, 0].axhline(S0, color='red', linestyle='--', linewidth=2, label=f'Initial: {S0:.2f}')
        axes[1, 0].axhline(np.mean(final_prices), color='green', linestyle='--', linewidth=2,
                           label=f'Mean: {np.mean(final_prices):.2f}')
        axes[1, 0].set_xlabel('Simulation')
        axes[1, 0].set_ylabel('Final Price')
        axes[1, 0].set_title(f'Sample Price Paths (First {n_paths})')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Plot 4: Bootstrap sample statistics
        bootstrap_means = np.mean(bootstrap_samples, axis=1)
        bootstrap_stds = np.std(bootstrap_samples, axis=1)
        axes[1, 1].scatter(bootstrap_stds, bootstrap_means, alpha=0.6, s=20)
        axes[1, 1].set_xlabel('Bootstrap Sample Std Dev')
        axes[1, 1].set_ylabel('Bootstrap Sample Mean')
        axes[1, 1].set_title('Bootstrap Sample Statistics')
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save the plot
        safe_asset_name = asset_name.replace('/', '_').replace('.', '_')
        plot_filename = f'monte_carlo_{safe_asset_name}.png'
        plt.savefig(plot_filename, dpi=150, bbox_inches='tight')
        plt.close()
        
        # Print statistics
        print(f"     📊 {asset_name} Statistics:")
        print(f"        Initial Price: {S0:.2f}")
        print(f"        Mean Final Price: {np.mean(final_prices):.2f}")
        print(f"        Std Dev: {np.std(final_prices):.2f}")
        print(f"        Min: {np.min(final_prices):.2f}, Max: {np.max(final_prices):.2f}")
        print(f"        Plot saved: {plot_filename}")

def main():
    """Main execution function"""
    portfolio_size = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    
    print("Portfolio Optimization System")
    print("=" * 40)
    print(f"Portfolio size: {portfolio_size}")
    
    optimizer = PortfolioOptimizer(portfolio_size)
    best_portfolio, all_results = optimizer.run_full_optimization()
    
    print("\n✅ Optimization completed successfully!")

if __name__ == "__main__":
    main() 