"""
MBB Core Module - Python wrapper for C library functions

Provides Moving Block Bootstrap, Monte Carlo simulation, and portfolio optimization
using compiled C functions for performance.
"""

import numpy as np
import ctypes
import os
import sys
from contextlib import contextmanager


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


class MBBCore:
    """Moving Block Bootstrap Core Functions"""
    
    def __init__(self):
        self.c_lib = self._load_c_library()
        self._setup_c_functions()
    
    def _load_c_library(self):
        """Load and verify C library"""
        # Try to find the library in the same directory as this file
        lib_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Try different library extensions based on OS
        lib_extensions = ['.dll', '.so', '.dylib']  # Windows, Linux, macOS
        lib_path = None
        
        for ext in lib_extensions:
            test_path = os.path.join(lib_dir, f'functions{ext}')
            if os.path.exists(test_path):
                lib_path = test_path
                break
        
        if not lib_path:
            raise RuntimeError(
                f"C library not found in {lib_dir}. "
                f"Please compile with: cd {lib_dir} && make (or gcc -shared -o functions.dll functions_optimized.c -lm on Windows)"
            )
        
        try:
            c_lib = ctypes.CDLL(lib_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load C library: {str(e)}")
        
        # Verify required functions exist
        required_functions = [
            'moving_block_bootstrap',
            'monte_carlo_simulation', 
            'optimize_portfolio_newton_raphson'
        ]
        for func_name in required_functions:
            if not hasattr(c_lib, func_name):
                raise RuntimeError(f"C function {func_name} not found in library")
        
        return c_lib
    
    def _setup_c_functions(self):
        """Configure C function signatures"""
        # Moving block bootstrap
        self.c_lib.moving_block_bootstrap.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int,
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        self.c_lib.moving_block_bootstrap.restype = ctypes.POINTER(ctypes.c_double)
        
        # Monte Carlo simulation
        self.c_lib.monte_carlo_simulation.argtypes = [
            ctypes.c_double, ctypes.POINTER(ctypes.c_double),
            ctypes.c_int, ctypes.c_int, ctypes.c_int
        ]
        self.c_lib.monte_carlo_simulation.restype = ctypes.POINTER(ctypes.c_double)
        
        # Newton-Raphson optimization
        self.c_lib.optimize_portfolio_newton_raphson.argtypes = [
            ctypes.POINTER(ctypes.c_double), ctypes.c_int, ctypes.c_int,
            ctypes.POINTER(ctypes.c_double), ctypes.c_double, 
            ctypes.c_int, ctypes.c_double
        ]
        self.c_lib.optimize_portfolio_newton_raphson.restype = ctypes.POINTER(ctypes.c_double)
    
    def _prepare_data(self, data):
        """Clean and prepare data for C functions"""
        if hasattr(data, 'dropna'):
            data = data.dropna()
        arr = np.array(data, dtype=np.float64)
        return arr[~np.isnan(arr)]
    
    def moving_block_bootstrap(self, log_returns, n_bootstrap=1000, sample_size=63,
                               block_size=None, optimize_block_size=True, seed=1987):
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
        seed : int
            Random seed for reproducibility
            
        Returns:
        --------
        np.ndarray
            Bootstrap samples of shape (n_bootstrap, sample_size)
        """
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
        
        # Convert to C array
        c_array = (ctypes.c_double * len(log_returns_array))(*log_returns_array)
        
        # Call C function
        with suppress_output():
            result_ptr = self.c_lib.moving_block_bootstrap(
                c_array, len(log_returns_array), n_bootstrap, 
                sample_size, block_size, seed
            )
        
        if not result_ptr:
            raise RuntimeError("Bootstrap failed - C function returned NULL")
        
        # Convert result to numpy array
        result = np.ctypeslib.as_array(
            result_ptr, 
            shape=(n_bootstrap, sample_size)
        ).copy()
        
        return result
    
    def monte_carlo_simulation(self, S0, bootstrap_samples, iterations=5000, seed=1987):
        """
        Monte Carlo simulation using bootstrap samples
        
        Parameters:
        -----------
        S0 : float
            Initial asset price
        bootstrap_samples : np.ndarray
            Bootstrap samples from moving_block_bootstrap
        iterations : int
            Number of Monte Carlo iterations
        seed : int
            Random seed for reproducibility
            
        Returns:
        --------
        np.ndarray
            Final prices from Monte Carlo simulation
        """
        if not isinstance(bootstrap_samples, np.ndarray) or bootstrap_samples.ndim != 2:
            raise ValueError("bootstrap_samples must be 2D numpy array")
        
        n_bootstrap, sample_size = bootstrap_samples.shape
        
        # Flatten bootstrap samples for C function
        bootstrap_flat = bootstrap_samples.flatten()
        c_array = (ctypes.c_double * len(bootstrap_flat))(*bootstrap_flat)
        
        # Call C function
        with suppress_output():
            result_ptr = self.c_lib.monte_carlo_simulation(
                ctypes.c_double(S0), c_array, 
                n_bootstrap, sample_size, iterations
            )
        
        if not result_ptr:
            raise RuntimeError("Monte Carlo failed - C function returned NULL")
        
        # Convert result to numpy array
        result = np.ctypeslib.as_array(result_ptr, shape=(iterations,)).copy()
        
        return result
    
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
        
        # Flatten arrival values
        arrival_flat = arrival_values.flatten()
        c_arrival = (ctypes.c_double * len(arrival_flat))(*arrival_flat)
        
        # Initial weights (equal allocation)
        initial_weights = np.ones(n_assets) / n_assets
        c_weights = (ctypes.c_double * n_assets)(*initial_weights)
        
        # Call C function
        with suppress_output():
            result_ptr = self.c_lib.optimize_portfolio_newton_raphson(
                c_arrival, n_assets, n_simulations, c_weights,
                ctypes.c_double(risk_free_rate), max_iterations,
                ctypes.c_double(tolerance)
            )
        
        if not result_ptr:
            raise RuntimeError("Newton-Raphson optimization failed")
        
        # Convert result to numpy array
        result = np.ctypeslib.as_array(result_ptr, shape=(n_assets,)).copy()
        
        return result
    
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
            except:
                volatilities.append(np.inf)
        
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

