import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm

def calculate_hedge_ratio(asset1_prices, asset2_prices):
    """
    Calculate the hedge ratio (beta) between two assets using OLS regression
    
    Parameters:
    -----------
    asset1_prices : numpy.ndarray
        Price series for the first asset
    asset2_prices : numpy.ndarray
        Price series for the second asset
        
    Returns:
    --------
    float
        The hedge ratio (beta) between the two assets
    """
    try:
        # Check if price arrays have enough data
        if len(asset1_prices) < 2 or len(asset2_prices) < 2:
            return 1.0
            
        # Add a constant to the independent variable
        X = sm.add_constant(asset2_prices)
        
        # Perform OLS regression
        model = sm.OLS(asset1_prices, X).fit()
        
        # Extract the beta (hedge ratio)
        beta = model.params[1]
        
        return beta
    except Exception as e:
        print(f"Error calculating hedge ratio: {str(e)}")
        return 1.0  # Default to 1:1 ratio on error

def calculate_half_life(spread):
    """
    Calculate the half life of mean reversion for a spread series
    
    Parameters:
    -----------
    spread : numpy.ndarray
        The spread between two assets
        
    Returns:
    --------
    float
        Half-life of mean reversion in days
    """
    try:
        # Check if spread array has enough data
        if len(spread) < 3:
            return 0.0
            
        # Calculate lagged spread
        spread_lag = np.roll(spread, 1)
        spread_lag[0] = spread_lag[1]  # Avoid using garbage first value
        
        # Calculate delta (change) in spread
        spread_delta = spread[1:] - spread_lag[1:]
        spread_lag = spread_lag[1:]
        
        # Run OLS regression on spread diff vs. lagged spread
        X = sm.add_constant(spread_lag)
        model = sm.OLS(spread_delta, X).fit()
        
        # Extract the beta
        beta = model.params[1]
        
        # Calculate half-life
        if beta < 0:  # Check if mean-reverting
            half_life = -np.log(2) / beta
            return half_life
        else:
            return np.inf  # Not mean-reverting
    except Exception as e:
        print(f"Error calculating half-life: {str(e)}")
        return 0.0

def compute_zscore(spread):
    """
    Compute z-score for a spread series
    
    Parameters:
    -----------
    spread : numpy.ndarray
        The spread between two assets
        
    Returns:
    --------
    numpy.ndarray
        Z-score series
    """
    try:
        # Calculate mean and standard deviation
        mean_spread = np.mean(spread)
        std_spread = np.std(spread)
        
        # Avoid division by zero
        if std_spread == 0:
            return np.zeros_like(spread)
            
        # Calculate z-score
        zscore = (spread - mean_spread) / std_spread
        return zscore
    except Exception as e:
        print(f"Error computing z-score: {str(e)}")
        return np.zeros_like(spread)

def calculate_pair_correlation(asset1_prices, asset2_prices):
    """
    Calculate the correlation coefficient between two asset price series
    
    Parameters:
    -----------
    asset1_prices : numpy.ndarray
        Price series for the first asset
    asset2_prices : numpy.ndarray
        Price series for the second asset
        
    Returns:
    --------
    float
        Pearson correlation coefficient
    """
    try:
        # Check if price arrays have enough data
        if len(asset1_prices) < 2 or len(asset2_prices) < 2:
            return 0.0
            
        # Calculate correlation
        correlation, _ = stats.pearsonr(asset1_prices, asset2_prices)
        return correlation
    except Exception as e:
        print(f"Error calculating correlation: {str(e)}")
        return 0.0