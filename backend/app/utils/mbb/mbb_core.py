"""
MBB Core Module - Pure Python Implementation

Provides Moving Block Bootstrap, Monte Carlo simulation, and portfolio optimization
using NumPy for performance.
"""

import numpy as np
import logging

logger = logging.getLogger(__name__)


class MBBCore:
    """Moving Block Bootstrap Core Functions - Pure Python Implementation"""
    
    def __init__(self, seed=1987):
        """
        Initialize MBB Core
        
        Parameters:
        -----------
        seed : int
            Random seed for reproducibility (default: 1987)
        """
        self.seed = seed
        self.rng = np.random.default_rng(seed)
    
    def _prepare_data(self, data):
        """Clean and prepare data"""
        if hasattr(data, 'dropna'):
            data = data.dropna()
        arr = np.array(data, dtype=np.float64)
        return arr[~np.isnan(arr)]
    
    def moving_block_bootstrap(self, log_returns, n_bootstrap=1000, sample_size=63,
                               block_size=None, optimize_block_size=True, seed=None):
        """
        Moving block bootstrap to preserve temporal dependencies
        
        Parameters:
        -----------
        log_returns : array-like
            Log returns time series
        n_bootstrap : int
            Number of bootstrap samples to generate
        sample_size : int
            Size of each bootstrap sample
        block_size : int, optional
            Block size for bootstrap. If None, will be optimized
        optimize_block_size : bool
            Whether to optimize block size if not provided
        seed : int, optional
            Random seed (uses instance seed if None)
            
        Returns:
        --------
        np.ndarray
            Bootstrap samples of shape (n_bootstrap, sample_size)
        """
        # Use provided seed or instance seed
        if seed is not None:
            rng = np.random.default_rng(seed)
        else:
            rng = self.rng
        
        if block_size is None and optimize_block_size:
            block_size = self._choose_optimal_block_size(log_returns)
        elif block_size is None:
            block_size = 5
        
        log_returns_array = self._prepare_data(log_returns)
        
        if len(log_returns_array) < block_size:
            raise ValueError(
                f"Time series length ({len(log_returns_array)}) "
                f"must be >= block size ({block_size})"
            )
        
        # Number of possible blocks (overlapping)
        n_blocks = len(log_returns_array) - block_size + 1
        
        # Initialize output array
        bootstrap_samples = np.zeros((n_bootstrap, sample_size), dtype=np.float64)
        
        # Generate bootstrap samples
        for bootstrap_idx in range(n_bootstrap):
            sample_idx = 0
            
            while sample_idx < sample_size:
                # Randomly select a block starting index
                block_start = rng.integers(0, n_blocks)
                
                # Copy block to sample
                block_end = min(block_start + block_size, len(log_returns_array))
                block_length = block_end - block_start
                remaining = sample_size - sample_idx
                copy_length = min(block_length, remaining)
                
                bootstrap_samples[bootstrap_idx, sample_idx:sample_idx + copy_length] = \
                    log_returns_array[block_start:block_start + copy_length]
                
                sample_idx += copy_length
        
        return bootstrap_samples
    
    def monte_carlo_simulation(self, S0, bootstrap_samples, iterations=5000, seed=None):
        """
        Monte Carlo simulation using bootstrap samples
        
        Parameters:
        -----------
        S0 : float
            Initial asset price
        bootstrap_samples : np.ndarray
            Bootstrap samples from moving_block_bootstrap (n_bootstrap x sample_size)
        iterations : int
            Number of Monte Carlo iterations
        seed : int, optional
            Random seed (uses instance seed if None)
            
        Returns:
        --------
        np.ndarray
            Final prices from Monte Carlo simulation
        """
        if not isinstance(bootstrap_samples, np.ndarray) or bootstrap_samples.ndim != 2:
            raise ValueError("bootstrap_samples must be 2D numpy array")
        
        # Use provided seed or instance seed
        if seed is not None:
            rng = np.random.default_rng(seed)
        else:
            rng = self.rng
        
        n_bootstrap, sample_size = bootstrap_samples.shape
        
        if iterations > n_bootstrap:
            logger.warning(
                f"More iterations ({iterations}) than bootstrap samples ({n_bootstrap}). "
                f"Some samples will be reused."
            )
        
        # Initialize output array
        final_prices = np.zeros(iterations, dtype=np.float64)
        
        # Generate Monte Carlo paths
        for iter_idx in range(iterations):
            current_price = S0
            
            # Randomly select a bootstrap sample (with replacement)
            bootstrap_idx = rng.integers(0, n_bootstrap)
            
            # Apply returns sequentially as a temporal path
            for t in range(sample_size):
                log_return = bootstrap_samples[bootstrap_idx, t]
                current_price *= np.exp(log_return)
            
            final_prices[iter_idx] = current_price
        
        return final_prices
    
    def optimize_portfolio_newton_raphson(self, arrival_values, risk_free_rate=0.0,
                                         max_iterations=100, tolerance=1e-6):
        """
        Optimize portfolio weights using Newton-Raphson method
        
        Parameters:
        -----------
        arrival_values : np.ndarray or pd.DataFrame
            Asset arrival values from Monte Carlo (n_simulations x n_assets)
        risk_free_rate : float
            Risk-free rate for Sharpe ratio calculation
        max_iterations : int
            Maximum optimization iterations
        tolerance : float
            Convergence tolerance
            
        Returns:
        --------
        np.ndarray
            Optimal portfolio weights
        """
        # Convert to numpy array if DataFrame
        if hasattr(arrival_values, 'values'):
            arrival_values = arrival_values.values
        
        n_simulations, n_assets = arrival_values.shape
        
        # Initial weights (equal allocation)
        weights = np.ones(n_assets, dtype=np.float64) / n_assets
        
        # Optimization loop
        for iteration in range(max_iterations):
            # Calculate gradient and Hessian numerically
            h = 1e-6  # Step size for numerical differentiation
            gradient = np.zeros(n_assets, dtype=np.float64)
            hessian = np.zeros((n_assets, n_assets), dtype=np.float64)
            
            # Current function value (negative Sharpe ratio)
            f_current = -self._calculate_sharpe_ratio(weights, arrival_values, risk_free_rate)
            
            # Calculate gradient and diagonal of Hessian
            for i in range(n_assets):
                # Forward step
                weights[i] += h
                f_forward = -self._calculate_sharpe_ratio(weights, arrival_values, risk_free_rate)
                
                # Backward step
                weights[i] -= 2 * h
                f_backward = -self._calculate_sharpe_ratio(weights, arrival_values, risk_free_rate)
                
                # Restore value
                weights[i] += h
                
                # Gradient (central difference)
                gradient[i] = (f_forward - f_backward) / (2 * h)
                
                # Hessian diagonal (second derivative)
                hessian[i, i] = (f_forward + f_backward - 2 * f_current) / (h * h)
                # Add small regularization for numerical stability
                hessian[i, i] += 1e-6
            
            # Off-diagonal elements set to zero (simplified Hessian)
            # This matches the C implementation
            
            # Solve linear system: H * delta = -gradient
            # Since Hessian is diagonal, solution is straightforward
            delta = np.zeros(n_assets, dtype=np.float64)
            for i in range(n_assets):
                if abs(hessian[i, i]) > 1e-10:
                    delta[i] = -gradient[i] / hessian[i, i]
            
            # Line search with backtracking
            alpha = 1.0
            best_weights = weights.copy()
            best_f = f_current
            
            for ls_iter in range(10):
                # Update weights
                new_weights = weights + alpha * delta
                
                # Project to simplex (weights >= 0, sum = 1)
                new_weights = np.maximum(new_weights, 0.0)
                sum_weights = np.sum(new_weights)
                if sum_weights > 0:
                    new_weights = new_weights / sum_weights
                
                # Evaluate function
                f_new = -self._calculate_sharpe_ratio(new_weights, arrival_values, risk_free_rate)
                
                if f_new < best_f:
                    best_weights = new_weights
                    best_f = f_new
                    break
                
                # Reduce step size
                alpha *= 0.5
            
            # Update weights
            weights = best_weights
            
            # Check convergence
            grad_norm = np.linalg.norm(gradient)
            if grad_norm < tolerance:
                break
        
        return weights
    
    def _calculate_sharpe_ratio(self, weights, arrival_values, risk_free_rate):
        """Calculate Sharpe ratio for given portfolio weights"""
        # Calculate portfolio returns
        portfolio_returns = np.dot(arrival_values, weights)
        
        # Calculate mean and standard deviation
        mean_return = np.mean(portfolio_returns)
        std_return = np.std(portfolio_returns)
        
        if std_return == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / std_return
    
    def _choose_optimal_block_size(self, log_returns, method='auto'):
        """
        Choose optimal block size for bootstrap
        
        Parameters:
        -----------
        log_returns : array-like
            Log returns time series
        method : str
            Method for block size selection ('auto', 'theoretical', 'empirical')
            
        Returns:
        --------
        int
            Optimal block size
        """
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
                # Small bootstrap for testing
                bootstrap_samples = self.moving_block_bootstrap(
                    log_returns_array, n_bootstrap=100, sample_size=min(63, n),
                    block_size=block_size, optimize_block_size=False
                )
                
                if test_statistic == 'mean':
                    stats = np.mean(bootstrap_samples, axis=1)
                elif test_statistic == 'variance':
                    stats = np.var(bootstrap_samples, axis=1)
                else:  # sharpe
                    means = np.mean(bootstrap_samples, axis=1)
                    stds = np.std(bootstrap_samples, axis=1)
                    stats = np.where(stds > 0, means / stds, 0)
                
                volatilities.append(np.std(stats))
            except Exception as e:
                logger.warning(f"Error testing block size {block_size}: {e}")
                volatilities.append(np.inf)
        
        if not volatilities or all(v == np.inf for v in volatilities):
            # Fallback to theoretical if all empirical tests fail
            return self._theoretical_block_size(n)
        
        return candidate_blocks[np.argmin(volatilities)]
    
    def calculate_portfolio_returns(self, weights, arrival_values):
        """Calculate portfolio returns for given weights"""
        if hasattr(arrival_values, 'values'):
            arrival_values = arrival_values.values
        return np.dot(arrival_values, weights)
    
    def calculate_sharpe_ratio(self, portfolio_returns, risk_free_rate=0.0):
        """Calculate Sharpe ratio"""
        mean_return = np.mean(portfolio_returns)
        std_return = np.std(portfolio_returns)
        
        if std_return == 0:
            return 0.0
        
        return (mean_return - risk_free_rate) / std_return
