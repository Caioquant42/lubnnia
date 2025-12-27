#!/usr/bin/env python3
"""
Z-Score Extreme Strategy for BOVA Options (LONG POSITIONS ONLY)

Analyzes CALL options with delta 0.20 to 0.05 using Z-score extremes:
- Entry: Buy (LONG) when Z-score <= -2 (oversold, using 20-day rolling window)
- Exit: Sell (close LONG) when Z-score >= +2 (overbought)
- Strategy is LONG ONLY - never enters short positions at +2
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import sys
from scipy import stats


def calculate_var_cvar(returns, confidence_level=0.95):
    """
    Calculate Value at Risk (VaR) and Conditional VaR (CVaR).
    
    Args:
        returns: Array of returns
        confidence_level: Confidence level (default 0.95 = 95%)
    
    Returns:
        Tuple of (VaR, CVaR)
    """
    if len(returns) == 0 or np.all(np.isnan(returns)):
        return np.nan, np.nan
    
    # Remove NaN values
    returns = returns[~np.isnan(returns)]
    
    if len(returns) == 0:
        return np.nan, np.nan
    
    # VaR is the negative of the percentile (since we're looking at losses)
    var = -np.percentile(returns, (1 - confidence_level) * 100)
    
    # CVaR is the mean of returns below the VaR threshold
    threshold = -var
    tail_returns = returns[returns <= threshold]
    
    if len(tail_returns) > 0:
        cvar = -np.mean(tail_returns)
    else:
        cvar = var
    
    return var, cvar


def calculate_z_score(prices, window=20):
    """
    Calculate Z-score using rolling window.
    
    Args:
        prices: Array of prices
        window: Rolling window for mean/std calculation (default 20)
    
    Returns:
        DataFrame with rolling mean, std, and Z-score
    """
    df = pd.DataFrame({'LastPremio': prices})
    df['RollingMean'] = df['LastPremio'].rolling(window=window, min_periods=5).mean()
    df['RollingStd'] = df['LastPremio'].rolling(window=window, min_periods=5).std()
    df['ZScore'] = (df['LastPremio'] - df['RollingMean']) / df['RollingStd']
    
    return df


def backtest_strategy(df, entry_z_threshold=-2.0, exit_z_threshold=2.0, initial_capital=100000):
    """
    Backtest Z-score extreme strategy (LONG POSITIONS ONLY).
    
    Strategy (Long positions only, no shorts):
    - ENTER (BUY) when Z-score <= -2 (oversold, using 20-day rolling window)
    - EXIT (SELL) when Z-score >= +2 (overbought)
    - Never enter a position at Z-score = +2 or above
    - Only one position at a time (long only)
    
    Args:
        df: DataFrame with prices and Z-scores
        entry_z_threshold: Z-score threshold for entry (default -2.0, must be negative)
        exit_z_threshold: Z-score threshold for exit (default +2.0, must be positive)
        initial_capital: Initial capital for backtesting
    
    Returns:
        Dictionary with backtest results
    """
    capital = initial_capital
    trades = []
    current_position = None
    
    for i in range(len(df)):
        price = df.iloc[i]['LastPremio']
        z_score = df.iloc[i]['ZScore']
        
        # Skip if Z-score is not available
        if pd.isna(z_score):
            continue
        
        # ENTRY SIGNAL: Only enter LONG position when Z-score <= -2 (oversold)
        # We NEVER enter at +2 or above (no short positions)
        if current_position is None:
            # Only enter when Z-score is at or below entry threshold (negative)
            if z_score <= entry_z_threshold:
                # Buy signal (LONG position only)
                shares = capital / price if price > 0 else 0
                if shares > 0:
                    current_position = {
                        'entry_index': i,
                        'entry_price': price,
                        'entry_date': df.iloc[i]['Data'] if 'Data' in df.columns else i,
                        'shares': shares,
                        'entry_zscore': z_score,
                        'position_type': 'LONG'  # Always long, never short
                    }
                    capital = 0  # All capital invested
        
        # EXIT SIGNAL: Only exit when Z-score >= +2 (overbought)
        # This closes the LONG position, we do NOT enter a short position
        elif current_position is not None:
            # Only exit when Z-score is at or above exit threshold (positive)
            if z_score >= exit_z_threshold:
                # Sell signal (close LONG position)
                exit_price = price
                exit_return = (exit_price - current_position['entry_price']) / current_position['entry_price']
                
                capital = current_position['shares'] * exit_price
                
                trade = {
                    'entry_index': current_position['entry_index'],
                    'exit_index': i,
                    'entry_price': current_position['entry_price'],
                    'exit_price': exit_price,
                    'entry_date': current_position['entry_date'],
                    'exit_date': df.iloc[i]['Data'] if 'Data' in df.columns else i,
                    'shares': current_position['shares'],
                    'return': exit_return,
                    'pnl': capital - initial_capital,
                    'entry_zscore': current_position['entry_zscore'],
                    'exit_zscore': z_score,
                    'holding_period': i - current_position['entry_index'],
                    'position_type': 'LONG'
                }
                
                trades.append(trade)
                current_position = None  # Position closed, ready for next entry at -2
    
    # Close any open position at the end
    if current_position is not None:
        final_price = df.iloc[-1]['LastPremio']
        capital = current_position['shares'] * final_price
        exit_return = (final_price - current_position['entry_price']) / current_position['entry_price']
        
        trade = {
            'entry_index': current_position['entry_index'],
            'exit_index': len(df) - 1,
            'entry_price': current_position['entry_price'],
            'exit_price': final_price,
            'entry_date': current_position['entry_date'],
            'exit_date': df.iloc[-1]['Data'] if 'Data' in df.columns else len(df) - 1,
            'shares': current_position['shares'],
            'return': exit_return,
            'pnl': capital - initial_capital,
            'entry_zscore': current_position['entry_zscore'],
            'exit_zscore': df.iloc[-1]['ZScore'],
            'holding_period': len(df) - 1 - current_position['entry_index']
        }
        trades.append(trade)
    
    if len(trades) == 0:
        return {
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0,
            'win_rate': 0,
            'total_return': 0,
            'final_capital': initial_capital,
            'sharpe_ratio': 0,
            'max_drawdown': 0,
            'trades': []
        }
    
    trades_df = pd.DataFrame(trades)
    
    winning_trades = trades_df[trades_df['return'] > 0]
    losing_trades = trades_df[trades_df['return'] <= 0]
    
    total_return = (capital - initial_capital) / initial_capital
    
    # Calculate Sharpe ratio
    if len(trades_df) > 1:
        returns = trades_df['return'].values
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) > 0 else 0
    else:
        sharpe_ratio = 0
    
    # Calculate max drawdown
    cumulative = (1 + trades_df['return']).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    max_drawdown = drawdown.min()
    
    return {
        'total_trades': len(trades_df),
        'winning_trades': len(winning_trades),
        'losing_trades': len(losing_trades),
        'win_rate': len(winning_trades) / len(trades_df) if len(trades_df) > 0 else 0,
        'total_return': total_return,
        'final_capital': capital,
        'avg_return': trades_df['return'].mean(),
        'avg_win': winning_trades['return'].mean() if len(winning_trades) > 0 else 0,
        'avg_loss': losing_trades['return'].mean() if len(losing_trades) > 0 else 0,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_drawdown,
        'trades': trades_df
    }


def analyze_option_series(option_data, output_dir, option_id):
    """
    Analyze a single option series for VaR, CVaR, and mean reversion.
    
    Args:
        option_data: DataFrame with option price data
        output_dir: Directory to save outputs
        option_id: Identifier for this option series
    """
    if len(option_data) < 30:  # Need minimum data points
        return None
    
    # Sort by date
    option_data = option_data.sort_values('Data').reset_index(drop=True)
    
    # Calculate returns
    option_data['Returns'] = option_data['LastPremio'].pct_change()
    
    # Calculate VaR and CVaR
    returns = option_data['Returns'].dropna().values
    var_95, cvar_95 = calculate_var_cvar(returns, confidence_level=0.95)
    var_99, cvar_99 = calculate_var_cvar(returns, confidence_level=0.99)
    
    # Calculate Z-score with 20-day rolling window
    zscore_df = calculate_z_score(option_data['LastPremio'].values, window=20)
    option_data = pd.concat([option_data, zscore_df[['RollingMean', 'RollingStd', 'ZScore']]], axis=1)
    
    # Calculate Z-score statistics
    entry_signals = (option_data['ZScore'] <= -2.0).sum()
    exit_signals = (option_data['ZScore'] >= 2.0).sum()
    
    # Backtest strategy: Entry at Z-score = -2, Exit at Z-score = +2
    backtest_results = backtest_strategy(option_data, entry_z_threshold=-2.0, exit_z_threshold=2.0)
    
    # Get average days to expiration and delta for this option series
    avg_dias_vencimento = option_data['Dias4Vencimento'].mean() if 'Dias4Vencimento' in option_data.columns else np.nan
    avg_delta = option_data['Delta'].mean() if 'Delta' in option_data.columns else np.nan
    
    return {
        'option_id': option_id,
        'var_95': var_95,
        'cvar_95': cvar_95,
        'var_99': var_99,
        'cvar_99': cvar_99,
        'entry_signals': entry_signals,
        'exit_signals': exit_signals,
        'avg_dias_vencimento': avg_dias_vencimento,
        'avg_delta': avg_delta,
        'backtest_results': backtest_results,
        'option_data': option_data
    }


def load_options_data(db_path):
    """Load CALL options with delta between 0.20 and 0.05."""
    print(f"Loading data from {db_path}...")
    
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database file '{db_path}' not found!")
    
    conn = sqlite3.connect(db_path)
    
    try:
        query = """
            SELECT 
                id, Ativo, Data, Tipo, K, Delta, LastPremio, BS_Price, Bid, Ask,
                Vol_imp, Dias4Vencimento, Vencimento
            FROM options_data
            WHERE Tipo = 'CALL'
            AND Delta >= 0.05
            AND Delta <= 0.20
            AND LastPremio IS NOT NULL
            AND LastPremio > 0
            ORDER BY Ativo, Data
        """
        
        df = pd.read_sql_query(query, conn)
        print(f"Loaded {len(df):,} CALL option records (delta 0.05-0.20)")
        
        # Convert Data to datetime
        df['Data'] = pd.to_datetime(df['Data'], format='%Y.%m.%d %H:%M:%S', errors='coerce')
        
        return df
        
    finally:
        conn.close()


def generate_visualizations(analysis_results, output_dir):
    """Generate visualizations for the analysis."""
    print("\nGenerating visualizations...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sns.set_style("whitegrid")
    
    # Filter valid results with trades
    valid_results = [r for r in analysis_results if r is not None and r['backtest_results']['total_trades'] > 0]
    
    if len(valid_results) == 0:
        print("No valid results with trades to visualize")
        return
    
    # Sort by total return to get top 5 strategies
    valid_results_sorted = sorted(valid_results, 
                                  key=lambda x: x['backtest_results']['total_return'], 
                                  reverse=True)
    
    # Select top 5 performing strategies
    top_5_results = valid_results_sorted[:5]
    
    print(f"Generating visualizations for top {len(top_5_results)} performing strategies...")
    
    for idx, result in enumerate(top_5_results):
        if result is None:
            continue
        
        option_data = result['option_data']
        option_id = result['option_id']
        backtest = result['backtest_results']
        
        # Create figure with subplots (4 plots: price, z-score, returns, equity curve)
        rank = idx + 1
        performance_info = f"Rank #{rank} | Return: {backtest['total_return']:.2%} | Win Rate: {backtest['win_rate']:.2%} | Sharpe: {backtest['sharpe_ratio']:.2f} | Trades: {backtest['total_trades']}"
        fig, axes = plt.subplots(4, 1, figsize=(16, 14))
        fig.suptitle(f'Top Strategy #{rank}: {option_id}\n{performance_info}', fontsize=16, fontweight='bold')
        
        # Plot 1: Price with VaR/CVaR levels and mean reversion signals
        ax1 = axes[0]
        ax1.plot(option_data.index, option_data['LastPremio'], label='LastPremio', linewidth=1.5, alpha=0.7)
        ax1.plot(option_data.index, option_data['RollingMean'], label='Rolling Mean', linewidth=2, color='orange')
        
        # Add Z-score entry/exit zones
        rolling_mean = option_data['RollingMean'].values
        rolling_std = option_data['RollingStd'].values
        
        # Calculate price levels for Z-score = -2 and +2
        entry_level = rolling_mean - 2 * rolling_std  # Z-score = -2
        exit_level = rolling_mean + 2 * rolling_std   # Z-score = +2
        
        ax1.plot(option_data.index, entry_level, '--g', linewidth=2, 
                label='Entry Level (Z = -2)', alpha=0.7)
        ax1.plot(option_data.index, exit_level, '--r', linewidth=2, 
                label='Exit Level (Z = +2)', alpha=0.7)
        ax1.fill_between(option_data.index, entry_level, rolling_mean, 
                        alpha=0.2, color='green', label='Entry Zone (Oversold)')
        ax1.fill_between(option_data.index, rolling_mean, exit_level, 
                        alpha=0.2, color='red', label='Exit Zone (Overbought)')
        
        ax1.set_xlabel('Time Index')
        ax1.set_ylabel('Price (LastPremio)')
        ax1.set_title('Price with Z-Score Entry/Exit Levels and Trading Signals')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Z-Score with entry/exit thresholds
        ax2 = axes[1]
        ax2.plot(option_data.index, option_data['ZScore'], label='Z-Score', linewidth=1.5, color='blue')
        ax2.axhline(y=-2, color='green', linestyle='--', linewidth=2, label='Entry Threshold (Z = -2)')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)
        ax2.axhline(y=2, color='red', linestyle='--', linewidth=2, label='Exit Threshold (Z = +2)')
        ax2.fill_between(option_data.index, -10, -2, alpha=0.2, color='green', label='Entry Zone (Oversold)')
        ax2.fill_between(option_data.index, 2, 10, alpha=0.2, color='red', label='Exit Zone (Overbought)')
        
        # Mark trade entry and exit points on Z-score plot
        if len(backtest['trades']) > 0:
            trades_df = backtest['trades']
            for trade_idx, (_, trade) in enumerate(trades_df.iterrows()):
                entry_idx = int(trade['entry_index'])
                exit_idx = int(trade['exit_index'])
                if entry_idx < len(option_data) and exit_idx < len(option_data):
                    entry_z = option_data.iloc[entry_idx]['ZScore']
                    exit_z = option_data.iloc[exit_idx]['ZScore']
                    trade_return = trade['return']
                    color = 'green' if trade_return > 0 else 'red'
                    ax2.scatter(entry_idx, entry_z, color=color, marker='^', s=150, 
                               zorder=5, edgecolors='black', linewidths=1, alpha=0.8,
                               label='Entry' if trade_idx == 0 else '')
                    ax2.scatter(exit_idx, exit_z, color=color, marker='v', s=150, 
                               zorder=5, edgecolors='black', linewidths=1, alpha=0.8,
                               label='Exit' if trade_idx == 0 else '')
        
        ax2.set_xlabel('Time Index')
        ax2.set_ylabel('Z-Score')
        ax2.set_title('Z-Score: Entry (Z = -2) and Exit (Z = +2) - 20-Day Rolling Window')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Returns distribution
        ax3 = axes[2]
        returns = option_data['Returns'].dropna()
        if len(returns) > 0:
            ax3.hist(returns, bins=50, alpha=0.7, edgecolor='black', label='Returns Distribution')
            ax3.axvline(x=0, color='black', linestyle='-', linewidth=1, alpha=0.3)
            ax3.set_xlabel('Returns')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Returns Distribution')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        # Add trade markers on price chart
        if len(backtest['trades']) > 0:
            trades_df = backtest['trades']
            entry_indices = trades_df['entry_index'].values
            exit_indices = trades_df['exit_index'].values
            
            # Mark entry points (only winning trades in green, losing in red)
            for trade_idx, entry_idx in enumerate(entry_indices):
                if int(entry_idx) < len(option_data):
                    entry_price = option_data.iloc[int(entry_idx)]['LastPremio']
                    trade_return = trades_df.iloc[trade_idx]['return']
                    color = 'green' if trade_return > 0 else 'red'
                    marker = '^'
                    ax1.scatter(entry_idx, entry_price, color=color, marker=marker, s=150, 
                               zorder=6, edgecolors='black', linewidths=1, alpha=0.7)
            
            # Mark exit points
            for trade_idx, exit_idx in enumerate(exit_indices):
                if int(exit_idx) < len(option_data):
                    exit_price = option_data.iloc[int(exit_idx)]['LastPremio']
                    trade_return = trades_df.iloc[trade_idx]['return']
                    color = 'green' if trade_return > 0 else 'red'
                    marker = 'v'
                    ax1.scatter(exit_idx, exit_price, color=color, marker=marker, s=150, 
                               zorder=6, edgecolors='black', linewidths=1, alpha=0.7)
            
            # Add legend for trade markers
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='green', edgecolor='black', label='Winning Trade'),
                Patch(facecolor='red', edgecolor='black', label='Losing Trade')
            ]
            ax1.legend(handles=legend_elements, loc='upper left')
        
        # Plot 4: Equity Curve
        ax4 = axes[3]
        if len(backtest['trades']) > 0:
            trades_df = backtest['trades']
            initial_capital = 100000
            cumulative_capital = [initial_capital]
            equity_time = [0]
            
            current_capital = initial_capital
            for _, trade in trades_df.iterrows():
                # Calculate capital after each trade
                current_capital = current_capital * (1 + trade['return'])
                cumulative_capital.append(current_capital)
                equity_time.append(int(trade['exit_index']))
            
            ax4.plot(equity_time, cumulative_capital, linewidth=2, color='blue', label='Equity Curve', marker='o', markersize=4)
            ax4.axhline(y=initial_capital, color='gray', linestyle='--', linewidth=1, label='Initial Capital')
            
            # Fill profit/loss zones
            if len(equity_time) > 1:
                profit_mask = [c >= initial_capital for c in cumulative_capital]
                if any(profit_mask):
                    ax4.fill_between(equity_time, initial_capital, cumulative_capital, 
                                   where=profit_mask, 
                                   alpha=0.3, color='green', label='Profit Zone', interpolate=True)
                loss_mask = [c < initial_capital for c in cumulative_capital]
                if any(loss_mask):
                    ax4.fill_between(equity_time, initial_capital, cumulative_capital, 
                                   where=loss_mask, 
                                   alpha=0.3, color='red', label='Loss Zone', interpolate=True)
            
            final_capital = cumulative_capital[-1] if len(cumulative_capital) > 0 else initial_capital
            ax4.set_xlabel('Time Index')
            ax4.set_ylabel('Capital (R$)')
            ax4.set_title(f'Equity Curve (Final: R$ {final_capital:,.2f} | Return: {backtest["total_return"]:.2%})')
            ax4.legend()
            ax4.grid(True, alpha=0.3)
            
            # Use log scale if returns are very large
            if final_capital > initial_capital * 2 or final_capital < initial_capital * 0.5:
                ax4.set_yscale('log')
        
        plt.tight_layout()
        plt.savefig(output_dir / f'top_strategy_{rank}_{option_id.replace("/", "_")}.png', dpi=300, bbox_inches='tight')
        plt.close()
    
    print(f"Generated {len(top_5_results)} visualization(s) for top performing strategies")


def _generate_dias_vencimento_analysis(valid_results, output_dir):
    """Generate visualization showing performance by days to expiration."""
    print("Generating Days to Expiration analysis visualization...")
    
    # Prepare data
    data_for_plot = []
    for result in valid_results:
        bt = result['backtest_results']
        avg_dias = result.get('avg_dias_vencimento', np.nan)
        if pd.notna(avg_dias) and bt['total_trades'] > 0:
            data_for_plot.append({
                'Dias4Vencimento': avg_dias,
                'SharpeRatio': bt['sharpe_ratio'] if pd.notna(bt['sharpe_ratio']) else 0,
                'TotalReturn': bt['total_return'],
                'WinRate': bt['win_rate'],
                'TotalTrades': bt['total_trades']
            })
    
    if len(data_for_plot_dias) == 0:
        return
    
    df_plot = pd.DataFrame(data_for_plot_dias)
    
    # Create figure with subplots
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Strategy Performance by Days to Expiration (Dias4Vencimento)', 
                 fontsize=16, fontweight='bold')
    
    # Plot 1: Sharpe Ratio vs Days to Expiration
    ax1 = axes[0, 0]
    ax1.scatter(df_plot['Dias4Vencimento'], df_plot['SharpeRatio'], 
               alpha=0.6, s=50, c=df_plot['SharpeRatio'], cmap='RdYlGn')
    ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax1.set_xlabel('Days to Expiration')
    ax1.set_ylabel('Sharpe Ratio')
    ax1.set_title('Sharpe Ratio by Days to Expiration')
    ax1.grid(True, alpha=0.3)
    
    # Add trend line
    if len(df_plot) > 1:
        z = np.polyfit(df_plot['Dias4Vencimento'], df_plot['SharpeRatio'], 1)
        p = np.poly1d(z)
        ax1.plot(df_plot['Dias4Vencimento'], p(df_plot['Dias4Vencimento']), 
                "r--", alpha=0.8, label=f'Trend: y={z[0]:.3f}x+{z[1]:.2f}')
        ax1.legend()
    
    # Plot 2: Total Return vs Days to Expiration
    ax2 = axes[0, 1]
    colors = ['green' if r > 0 else 'red' for r in df_plot['TotalReturn']]
    ax2.scatter(df_plot['Dias4Vencimento'], df_plot['TotalReturn'], 
               alpha=0.6, s=50, c=colors)
    ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
    ax2.set_xlabel('Days to Expiration')
    ax2.set_ylabel('Total Return')
    ax2.set_title('Total Return by Days to Expiration (Green=Win, Red=Loss)')
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Box plot of Sharpe Ratio by buckets
    ax3 = axes[1, 0]
    dias_buckets = {
        '0-7': (0, 7),
        '8-14': (8, 14),
        '15-21': (15, 21),
        '22-30': (22, 30),
        '31-45': (31, 45),
        '46-60': (46, 60),
        '61+': (61, 999)
    }
    
    bucket_data = []
    bucket_labels = []
    for label, (min_d, max_d) in dias_buckets.items():
        bucket_values = df_plot[(df_plot['Dias4Vencimento'] >= min_d) & 
                                (df_plot['Dias4Vencimento'] <= max_d)]['SharpeRatio'].values
        if len(bucket_values) > 0:
            bucket_data.append(bucket_values)
            bucket_labels.append(label)
    
    if len(bucket_data) > 0:
        ax3.boxplot(bucket_data, labels=bucket_labels)
        ax3.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax3.set_xlabel('Days to Expiration Bucket')
        ax3.set_ylabel('Sharpe Ratio')
        ax3.set_title('Sharpe Ratio Distribution by Days to Expiration Buckets')
        ax3.grid(True, alpha=0.3)
        plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 4: Win Rate vs Days to Expiration
    ax4 = axes[1, 1]
    ax4.scatter(df_plot['Dias4Vencimento'], df_plot['WinRate'], 
               alpha=0.6, s=50, c=df_plot['WinRate'], cmap='RdYlGn')
    ax4.axhline(y=0.5, color='black', linestyle='--', linewidth=1, alpha=0.5, label='50% Win Rate')
    ax4.set_xlabel('Days to Expiration')
    ax4.set_ylabel('Win Rate')
    ax4.set_title('Win Rate by Days to Expiration')
    ax4.set_ylim([0, 1])
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_dir / 'dias_vencimento_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # Generate Delta analysis visualization
    if len(data_for_plot_delta) > 0:
        df_delta = pd.DataFrame(data_for_plot_delta)
        
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Strategy Performance by Delta', fontsize=16, fontweight='bold')
        
        # Plot 1: Sharpe Ratio vs Delta
        ax1 = axes[0, 0]
        ax1.scatter(df_delta['Delta'], df_delta['SharpeRatio'], 
                   alpha=0.6, s=50, c=df_delta['SharpeRatio'], cmap='RdYlGn')
        ax1.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax1.set_xlabel('Delta')
        ax1.set_ylabel('Sharpe Ratio')
        ax1.set_title('Sharpe Ratio by Delta')
        ax1.grid(True, alpha=0.3)
        
        # Add trend line
        if len(df_delta) > 1:
            z = np.polyfit(df_delta['Delta'], df_delta['SharpeRatio'], 1)
            p = np.poly1d(z)
            ax1.plot(df_delta['Delta'], p(df_delta['Delta']), 
                    "r--", alpha=0.8, label=f'Trend: y={z[0]:.3f}x+{z[1]:.2f}')
            ax1.legend()
        
        # Plot 2: Total Return vs Delta
        ax2 = axes[0, 1]
        colors = ['green' if r > 0 else 'red' for r in df_delta['TotalReturn']]
        ax2.scatter(df_delta['Delta'], df_delta['TotalReturn'], 
                   alpha=0.6, s=50, c=colors)
        ax2.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
        ax2.set_xlabel('Delta')
        ax2.set_ylabel('Total Return')
        ax2.set_title('Total Return by Delta (Green=Win, Red=Loss)')
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Box plot of Sharpe Ratio by delta buckets
        ax3 = axes[1, 0]
        delta_buckets = {
            '0.05-0.08': (0.05, 0.08),
            '0.08-0.10': (0.08, 0.10),
            '0.10-0.12': (0.10, 0.12),
            '0.12-0.15': (0.12, 0.15),
            '0.15-0.18': (0.15, 0.18),
            '0.18-0.20': (0.18, 0.20)
        }
        
        bucket_data = []
        bucket_labels = []
        for label, (min_d, max_d) in delta_buckets.items():
            bucket_values = df_delta[(df_delta['Delta'] >= min_d) & 
                                    (df_delta['Delta'] < max_d)]['SharpeRatio'].values
            if len(bucket_values) > 0:
                bucket_data.append(bucket_values)
                bucket_labels.append(label)
        
        if len(bucket_data) > 0:
            ax3.boxplot(bucket_data, labels=bucket_labels)
            ax3.axhline(y=0, color='black', linestyle='--', linewidth=1, alpha=0.5)
            ax3.set_xlabel('Delta Bucket')
            ax3.set_ylabel('Sharpe Ratio')
            ax3.set_title('Sharpe Ratio Distribution by Delta Buckets')
            ax3.grid(True, alpha=0.3)
            plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        # Plot 4: Win Rate vs Delta
        ax4 = axes[1, 1]
        ax4.scatter(df_delta['Delta'], df_delta['WinRate'], 
                   alpha=0.6, s=50, c=df_delta['WinRate'], cmap='RdYlGn')
        ax4.axhline(y=0.5, color='black', linestyle='--', linewidth=1, alpha=0.5, label='50% Win Rate')
        ax4.set_xlabel('Delta')
        ax4.set_ylabel('Win Rate')
        ax4.set_title('Win Rate by Delta')
        ax4.set_ylim([0, 1])
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_dir / 'delta_analysis.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        print("Delta analysis visualization saved")
    
    print("Days to Expiration analysis visualization saved")


def generate_summary_report(analysis_results, output_path):
    """Generate summary report."""
    print("\nGenerating summary report...")
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("Z-SCORE EXTREME STRATEGY ANALYSIS")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("Focus: CALL Options with Delta 0.20 to 0.05")
    report_lines.append("Strategy: Entry at Z-Score = -2, Exit at Z-Score = +2 (20-day rolling window)")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # Aggregate statistics
    valid_results = [r for r in analysis_results if r is not None]
    
    if len(valid_results) == 0:
        report_lines.append("No valid option series found for analysis.")
        report_text = "\n".join(report_lines)
        Path(output_path).write_text(report_text, encoding='utf-8')
        return
    
    report_lines.append(f"Total Option Series Analyzed: {len(valid_results)}")
    report_lines.append("")
    
    # VaR/CVaR Statistics
    report_lines.append("VaR/CVaR Statistics:")
    report_lines.append("-" * 80)
    
    var_95_values = [r['var_95'] for r in valid_results if pd.notna(r['var_95'])]
    cvar_95_values = [r['cvar_95'] for r in valid_results if pd.notna(r['cvar_95'])]
    
    if len(var_95_values) > 0:
        report_lines.append(f"VaR 95% - Mean: {np.mean(var_95_values):.2%}, Median: {np.median(var_95_values):.2%}")
        report_lines.append(f"CVaR 95% - Mean: {np.mean(cvar_95_values):.2%}, Median: {np.median(cvar_95_values):.2%}")
    
    report_lines.append("")
    
    # Z-Score Statistics
    report_lines.append("Z-Score Signal Statistics:")
    report_lines.append("-" * 80)
    
    entry_signals_list = [r['entry_signals'] for r in valid_results]
    exit_signals_list = [r['exit_signals'] for r in valid_results]
    
    if len(entry_signals_list) > 0:
        report_lines.append(f"Entry Signals (Z <= -2) - Total: {sum(entry_signals_list)}, Mean per Option: {np.mean(entry_signals_list):.1f}")
        report_lines.append(f"Exit Signals (Z >= +2) - Total: {sum(exit_signals_list)}, Mean per Option: {np.mean(exit_signals_list):.1f}")
    
    report_lines.append("")
    
    # Analysis by Days to Expiration (Dias4Vencimento)
    report_lines.append("=" * 80)
    report_lines.append("ANALYSIS BY DAYS TO EXPIRATION (Dias4Vencimento)")
    report_lines.append("=" * 80)
    
    # Group results by days to expiration buckets
    dias_buckets = {
        '0-7 days': (0, 7),
        '8-14 days': (8, 14),
        '15-21 days': (15, 21),
        '22-30 days': (22, 30),
        '31-45 days': (31, 45),
        '46-60 days': (46, 60),
        '61+ days': (61, 999)
    }
    
    bucket_stats = {}
    
    for bucket_name, (min_days, max_days) in dias_buckets.items():
        bucket_results = []
        for result in valid_results:
            avg_dias = result.get('avg_dias_vencimento', np.nan)
            if pd.notna(avg_dias) and min_days <= avg_dias <= max_days:
                bt = result['backtest_results']
                if bt['total_trades'] > 0:
                    bucket_results.append({
                        'total_return': bt['total_return'],
                        'win_rate': bt['win_rate'],
                        'sharpe_ratio': bt['sharpe_ratio'] if pd.notna(bt['sharpe_ratio']) else 0,
                        'total_trades': bt['total_trades'],
                        'avg_return': bt.get('avg_return', 0)
                    })
        
        if len(bucket_results) > 0:
            bucket_stats[bucket_name] = {
                'count': len(bucket_results),
                'avg_sharpe': np.mean([r['sharpe_ratio'] for r in bucket_results]),
                'median_sharpe': np.median([r['sharpe_ratio'] for r in bucket_results]),
                'avg_return': np.mean([r['total_return'] for r in bucket_results]),
                'avg_win_rate': np.mean([r['win_rate'] for r in bucket_results]),
                'winning_strategies': sum(1 for r in bucket_results if r['total_return'] > 0),
                'losing_strategies': sum(1 for r in bucket_results if r['total_return'] <= 0),
                'total_trades': sum(r['total_trades'] for r in bucket_results)
            }
    
    if len(bucket_stats) > 0:
        report_lines.append("")
        report_lines.append("Performance by Days to Expiration:")
        report_lines.append("-" * 80)
        report_lines.append(f"{'Bucket':<15} {'Count':<8} {'Avg Sharpe':<12} {'Avg Return':<12} {'Win Rate':<10} {'Winners':<10} {'Losers':<10}")
        report_lines.append("-" * 80)
        
        for bucket_name in sorted(bucket_stats.keys()):
            stats = bucket_stats[bucket_name]
            report_lines.append(f"{bucket_name:<15} {stats['count']:<8} {stats['avg_sharpe']:>11.2f} "
                              f"{stats['avg_return']:>11.2%} {stats['avg_win_rate']:>9.2%} "
                              f"{stats['winning_strategies']:<10} {stats['losing_strategies']:<10}")
        
        report_lines.append("")
        
        # Identify best and worst buckets
        if len(bucket_stats) > 0:
            best_sharpe_bucket = max(bucket_stats.items(), key=lambda x: x[1]['avg_sharpe'])
            worst_sharpe_bucket = min(bucket_stats.items(), key=lambda x: x[1]['avg_sharpe'])
            best_return_bucket = max(bucket_stats.items(), key=lambda x: x[1]['avg_return'])
            worst_return_bucket = min(bucket_stats.items(), key=lambda x: x[1]['avg_return'])
            
            report_lines.append("Key Findings:")
            report_lines.append("-" * 80)
            report_lines.append(f"✓ Highest Sharpe Ratio: {best_sharpe_bucket[0]} (Sharpe: {best_sharpe_bucket[1]['avg_sharpe']:.2f}, "
                              f"Return: {best_sharpe_bucket[1]['avg_return']:.2%}, Win Rate: {best_sharpe_bucket[1]['avg_win_rate']:.2%})")
            report_lines.append(f"⚠ Lowest Sharpe Ratio: {worst_sharpe_bucket[0]} (Sharpe: {worst_sharpe_bucket[1]['avg_sharpe']:.2f}, "
                              f"Return: {worst_sharpe_bucket[1]['avg_return']:.2%}, Win Rate: {worst_sharpe_bucket[1]['avg_win_rate']:.2%})")
            report_lines.append(f"✓ Highest Average Return: {best_return_bucket[0]} (Return: {best_return_bucket[1]['avg_return']:.2%}, "
                              f"Sharpe: {best_return_bucket[1]['avg_sharpe']:.2f})")
            report_lines.append(f"⚠ Lowest Average Return: {worst_return_bucket[0]} (Return: {worst_return_bucket[1]['avg_return']:.2%}, "
                              f"Sharpe: {worst_return_bucket[1]['avg_sharpe']:.2f})")
            
            # Identify losing strategies (negative returns)
            losing_buckets = [(name, stats) for name, stats in bucket_stats.items() if stats['avg_return'] < 0]
            if len(losing_buckets) > 0:
                report_lines.append("")
                report_lines.append("⚠ LOSING STRATEGIES (Negative Average Returns):")
                report_lines.append("-" * 80)
                for name, stats in sorted(losing_buckets, key=lambda x: x[1]['avg_return']):
                    report_lines.append(f"  {name}: Return {stats['avg_return']:.2%}, Sharpe {stats['avg_sharpe']:.2f}, "
                                      f"Win Rate {stats['avg_win_rate']:.2%}, Losers: {stats['losing_strategies']}/{stats['count']}")
            
            # Identify winning strategies (positive returns and good Sharpe)
            winning_buckets = [(name, stats) for name, stats in bucket_stats.items() 
                             if stats['avg_return'] > 0 and stats['avg_sharpe'] > 0]
            if len(winning_buckets) > 0:
                report_lines.append("")
                report_lines.append("✓ WINNING STRATEGIES (Positive Returns & Sharpe > 0):")
                report_lines.append("-" * 80)
                for name, stats in sorted(winning_buckets, key=lambda x: x[1]['avg_sharpe'], reverse=True):
                    report_lines.append(f"  {name}: Return {stats['avg_return']:.2%}, Sharpe {stats['avg_sharpe']:.2f}, "
                                      f"Win Rate {stats['avg_win_rate']:.2%}, Winners: {stats['winning_strategies']}/{stats['count']}")
    
    report_lines.append("")
    
    # Backtest Results
    report_lines.append("Strategy Backtest Results:")
    report_lines.append("-" * 80)
    
    backtest_stats = []
    for result in valid_results:
        bt = result['backtest_results']
        if bt['total_trades'] > 0:
            backtest_stats.append(bt)
    
    if len(backtest_stats) > 0:
        win_rates = [bt['win_rate'] for bt in backtest_stats]
        total_returns = [bt['total_return'] for bt in backtest_stats]
        sharpe_ratios = [bt['sharpe_ratio'] for bt in backtest_stats if pd.notna(bt['sharpe_ratio'])]
        
        report_lines.append(f"Options with Trades: {len(backtest_stats)}/{len(valid_results)}")
        report_lines.append(f"Average Win Rate: {np.mean(win_rates):.2%}")
        report_lines.append(f"Average Total Return: {np.mean(total_returns):.2%}")
        if len(sharpe_ratios) > 0:
            report_lines.append(f"Average Sharpe Ratio: {np.mean(sharpe_ratios):.2f}")
        report_lines.append("")
        
        # Successful strategies
        successful = [bt for bt in backtest_stats if bt['total_return'] > 0 and bt['win_rate'] > 0.5]
        report_lines.append(f"Successful Strategies (Positive Return & Win Rate > 50%): {len(successful)}/{len(backtest_stats)}")
        
        if len(successful) > 0:
            report_lines.append("")
            report_lines.append("Top 5 Performing Strategies:")
            report_lines.append("-" * 80)
            successful_sorted = sorted(successful, key=lambda x: x['total_return'], reverse=True)[:5]
            for i, bt in enumerate(successful_sorted, 1):
                report_lines.append(f"{i}. Win Rate: {bt['win_rate']:.2%}, Total Return: {bt['total_return']:.2%}, "
                                  f"Sharpe: {bt['sharpe_ratio']:.2f}, Trades: {bt['total_trades']}")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("CONCLUSION")
    report_lines.append("=" * 80)
    
    if len(backtest_stats) > 0:
        avg_return = np.mean([bt['total_return'] for bt in backtest_stats])
        avg_win_rate = np.mean([bt['win_rate'] for bt in backtest_stats])
        
        if avg_return > 0 and avg_win_rate > 0.5:
            report_lines.append("✓ Strategy appears to be SUCCESSFUL on average")
            report_lines.append(f"  - Average Return: {avg_return:.2%}")
            report_lines.append(f"  - Average Win Rate: {avg_win_rate:.2%}")
        else:
            report_lines.append("⚠ Strategy results are MIXED")
            report_lines.append(f"  - Average Return: {avg_return:.2%}")
            report_lines.append(f"  - Average Win Rate: {avg_win_rate:.2%}")
    else:
        report_lines.append("⚠ No trades executed - strategy may need parameter adjustment")
    
    report_text = "\n".join(report_lines)
    Path(output_path).write_text(report_text, encoding='utf-8')
    print(f"Summary report saved to: {output_path}")


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='VaR/CVaR and Mean Reversion Analysis for BOVA Options')
    parser.add_argument('--db', type=str, default='BOVA_monthly.db', help='Path to database file')
    parser.add_argument('--output-dir', type=str, default='var_cvar_analysis_output', help='Output directory')
    parser.add_argument('--min-data-points', type=int, default=50, help='Minimum data points per option series')
    
    args = parser.parse_args()
    
    db_path = Path(__file__).parent / args.db
    output_dir = Path(__file__).parent / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("Z-SCORE EXTREME STRATEGY ANALYSIS")
    print("=" * 80)
    print(f"Database: {db_path}")
    print(f"Output directory: {output_dir}")
    print("Focus: CALL Options with Delta 0.20 to 0.05")
    print("Strategy: Entry at Z-Score = -2, Exit at Z-Score = +2 (20-day rolling window)")
    print("=" * 80)
    
    try:
        # Load data
        df = load_options_data(db_path)
        
        if len(df) == 0:
            print("No valid data found!")
            return
        
        # Group by option (Ativo + Vencimento) to analyze each option series
        print("\nGrouping options by ticker and expiration...")
        grouped = df.groupby(['Ativo', 'Vencimento'])
        
        analysis_results = []
        
        for (ativo, vencimento), group in grouped:
            if len(group) < args.min_data_points:
                continue
            
            option_id = f"{ativo}_{vencimento}"
            print(f"\nAnalyzing {option_id} ({len(group)} data points)...")
            
            result = analyze_option_series(group, output_dir, option_id)
            if result:
                analysis_results.append(result)
        
        print(f"\nAnalyzed {len(analysis_results)} option series")
        
        # Generate visualizations
        generate_visualizations(analysis_results, output_dir)
        
        # Generate summary report
        report_path = output_dir / 'var_cvar_mean_reversion_report.txt'
        generate_summary_report(analysis_results, report_path)
        
        # Save detailed results to CSV
        summary_data = []
        for result in analysis_results:
            if result:
                summary_data.append({
                    'OptionID': result['option_id'],
                    'VaR_95': result['var_95'],
                    'CVaR_95': result['cvar_95'],
                    'VaR_99': result['var_99'],
                    'CVaR_99': result['cvar_99'],
                    'EntrySignals': result['entry_signals'],
                    'ExitSignals': result['exit_signals'],
                    'AvgDiasVencimento': result.get('avg_dias_vencimento', np.nan),
                    'AvgDelta': result.get('avg_delta', np.nan),
                    'TotalTrades': result['backtest_results']['total_trades'],
                    'WinRate': result['backtest_results']['win_rate'],
                    'TotalReturn': result['backtest_results']['total_return'],
                    'SharpeRatio': result['backtest_results']['sharpe_ratio'],
                    'MaxDrawdown': result['backtest_results']['max_drawdown']
                })
        
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            csv_path = output_dir / 'var_cvar_summary.csv'
            summary_df.to_csv(csv_path, index=False)
            print(f"Summary CSV saved to: {csv_path}")
        
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print(f"Results saved to: {output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

