#!/usr/bin/env python3
"""
Value at Risk (VaR) and Conditional VaR (CVaR) Analysis for BOVA Options
Mean Reversion Strategy Backtesting

Analyzes CALL options with delta 0.20 to 0.05 to identify mean reversion opportunities.
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


def calculate_rolling_var_cvar(returns, window=20, confidence_level=0.95):
    """
    Calculate rolling VaR and CVaR for each time point.
    
    Args:
        returns: Series of returns
        window: Rolling window size
        confidence_level: Confidence level for VaR/CVaR
    
    Returns:
        Series of VaR and CVaR values
    """
    var_series = []
    cvar_series = []
    
    for i in range(len(returns)):
        if i < window:
            var_series.append(np.nan)
            cvar_series.append(np.nan)
        else:
            window_returns = returns.iloc[i-window:i].dropna()
            if len(window_returns) > 0:
                var, cvar = calculate_var_cvar(window_returns.values, confidence_level)
                var_series.append(var)
                cvar_series.append(cvar)
            else:
                var_series.append(np.nan)
                cvar_series.append(np.nan)
    
    return pd.Series(var_series, index=returns.index), pd.Series(cvar_series, index=returns.index)


def detect_mean_reversion(prices, window=20, z_threshold=2.0):
    """
    Detect mean reversion signals.
    
    Args:
        prices: Array of prices
        window: Rolling window for mean/std calculation
        z_threshold: Z-score threshold for mean reversion signal
    
    Returns:
        DataFrame with mean reversion signals
    """
    df = pd.DataFrame({'LastPremio': prices})
    df['RollingMean'] = df['LastPremio'].rolling(window=window, min_periods=5).mean()
    df['RollingStd'] = df['LastPremio'].rolling(window=window, min_periods=5).std()
    df['ZScore'] = (df['LastPremio'] - df['RollingMean']) / df['RollingStd']
    
    # Mean reversion signal: price is significantly below mean (oversold)
    df['MeanReversionSignal'] = df['ZScore'] < -z_threshold
    
    # Mean reversion completion: price returns to mean (Z-score = 0)
    df['MeanReversionComplete'] = (df['ZScore'] >= 0) & (df['ZScore'].shift(1) < 0)
    
    return df


def backtest_strategy(df, strategy_type='var', initial_capital=100000):
    """
    Backtest mean reversion strategy using rolling VaR or CVaR.
    
    Strategy VAR:
    - Buy when price hits rolling 20-day VaR threshold
    - Sell when price hits 120% return
    
    Strategy CVAR (Conservative):
    - Buy when price hits rolling 20-day CVaR threshold
    - Sell when price hits 120% return
    
    Args:
        df: DataFrame with prices, rolling VaR/CVaR, and Z-scores
        strategy_type: 'var' or 'cvar'
        initial_capital: Initial capital for backtesting
    
    Returns:
        Dictionary with backtest results
    """
    capital = initial_capital
    trades = []
    current_position = None
    
    # Determine which threshold column to use
    threshold_col = 'RollingVaR' if strategy_type == 'var' else 'RollingCVaR'
    
    for i in range(len(df)):
        price = df.iloc[i]['LastPremio']
        rolling_mean = df.iloc[i]['RollingMean']
        z_score = df.iloc[i]['ZScore']
        rolling_threshold = df.iloc[i].get(threshold_col, np.nan)
        
        # Skip if we don't have enough data for rolling calculation
        if pd.isna(rolling_threshold) or pd.isna(rolling_mean) or rolling_mean <= 0:
            continue
        
        # Entry signal: price hits rolling VaR or CVaR threshold
        if current_position is None:
            # Calculate price deviation from mean
            price_return = (price - rolling_mean) / rolling_mean
            
            # Buy when price drops to or below the rolling threshold
            # rolling_threshold is negative (VaR/CVaR represent losses)
            if price_return <= rolling_threshold:
                # Buy signal
                shares = capital / price if price > 0 else 0
                if shares > 0:
                    current_position = {
                        'entry_index': i,
                        'entry_price': price,
                        'entry_date': df.iloc[i]['Data'] if 'Data' in df.columns else i,
                        'shares': shares,
                        'entry_zscore': z_score,
                        'entry_threshold': rolling_threshold
                    }
                    capital = 0  # All capital invested
        
        # Exit signal: price hits 120% return
        elif current_position is not None:
            # Check for 120% return exit (price is 2.2x entry price = 120% gain)
            price_return = (price - current_position['entry_price']) / current_position['entry_price']
            if price_return >= 1.20:  # 120% return
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
                    'strategy_type': strategy_type,
                    'exit_reason': '120% Return Target'
                }
                
                trades.append(trade)
                current_position = None
    
    # Close any open position at the end
    if current_position is not None:
        final_price = df.iloc[-1]['LastPremio']
        capital = current_position['shares'] * final_price
        exit_return = (final_price - current_position['entry_price']) / current_position['entry_price']
        
        # Determine exit reason for final trade
        if exit_return >= 1.20:
            exit_reason = '120% Return Target (End of Data)'
        else:
            exit_reason = 'End of Data'
        
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
            'holding_period': len(df) - 1 - current_position['entry_index'],
            'strategy_type': strategy_type,
            'exit_reason': exit_reason
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
    if len(option_data) < 50:  # Need minimum data points for rolling calculations
        return None
    
    # Sort by date
    option_data = option_data.sort_values('Data').reset_index(drop=True)
    
    # Calculate returns
    option_data['Returns'] = option_data['LastPremio'].pct_change()
    
    # Detect mean reversion (rolling mean, std, Z-score)
    mr_df = detect_mean_reversion(option_data['LastPremio'].values, window=20)
    option_data = pd.concat([option_data, mr_df[['RollingMean', 'RollingStd', 'ZScore', 
                                                  'MeanReversionSignal', 'MeanReversionComplete']]], axis=1)
    
    # Calculate rolling 20-day VaR and CVaR
    rolling_var_95, rolling_cvar_95 = calculate_rolling_var_cvar(
        option_data['Returns'], window=20, confidence_level=0.95
    )
    option_data['RollingVaR'] = rolling_var_95
    option_data['RollingCVaR'] = rolling_cvar_95
    
    # Calculate overall statistics for reporting
    returns = option_data['Returns'].dropna().values
    var_95, cvar_95 = calculate_var_cvar(returns, confidence_level=0.95) if len(returns) > 0 else (np.nan, np.nan)
    var_99, cvar_99 = calculate_var_cvar(returns, confidence_level=0.99) if len(returns) > 0 else (np.nan, np.nan)
    
    # Calculate mean reversion statistics
    mean_reversion_signals = option_data['MeanReversionSignal'].sum()
    mean_reversion_complete = option_data['MeanReversionComplete'].sum()
    mean_reversion_rate = mean_reversion_complete / mean_reversion_signals if mean_reversion_signals > 0 else 0
    
    # Backtest both strategies
    backtest_var = backtest_strategy(option_data.copy(), strategy_type='var')
    backtest_cvar = backtest_strategy(option_data.copy(), strategy_type='cvar')
    
    return {
        'option_id': option_id,
        'var_95': var_95,
        'cvar_95': cvar_95,
        'var_99': var_99,
        'cvar_99': cvar_99,
        'mean_reversion_signals': mean_reversion_signals,
        'mean_reversion_complete': mean_reversion_complete,
        'mean_reversion_rate': mean_reversion_rate,
        'backtest_var': backtest_var,
        'backtest_cvar': backtest_cvar,
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
    """Generate visualizations for both VAR and CVAR strategies."""
    print("\nGenerating visualizations...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    sns.set_style("whitegrid")
    
    # Filter valid results with trades for both strategies
    valid_results = [r for r in analysis_results if r is not None]
    
    if len(valid_results) == 0:
        print("No valid results to visualize")
        return
    
    # Separate VAR and CVAR strategies
    var_results = [r for r in valid_results if r['backtest_var']['total_trades'] > 0]
    cvar_results = [r for r in valid_results if r['backtest_cvar']['total_trades'] > 0]
    
    # Sort by total return to get top 5 strategies for each
    var_sorted = sorted(var_results, 
                       key=lambda x: x['backtest_var']['total_return'], 
                       reverse=True)
    cvar_sorted = sorted(cvar_results, 
                        key=lambda x: x['backtest_cvar']['total_return'], 
                        reverse=True)
    
    top_5_var = var_sorted[:5]
    top_5_cvar = cvar_sorted[:5]
    
    print(f"Generating visualizations for top {len(top_5_var)} VAR strategies...")
    print(f"Generating visualizations for top {len(top_5_cvar)} CVAR strategies...")
    
    # Generate plots for VAR strategy
    for idx, result in enumerate(top_5_var):
        if result is None:
            continue
        
        option_data = result['option_data']
        option_id = result['option_id']
        backtest = result['backtest_var']
        strategy_name = 'VAR Strategy'
        
        _generate_single_strategy_plot(option_data, option_id, backtest, strategy_name, idx + 1, output_dir)
    
    # Generate plots for CVAR strategy
    for idx, result in enumerate(top_5_cvar):
        if result is None:
            continue
        
        option_data = result['option_data']
        option_id = result['option_id']
        backtest = result['backtest_cvar']
        strategy_name = 'CVAR Strategy (Conservative)'
        
        _generate_single_strategy_plot(option_data, option_id, backtest, strategy_name, idx + 1, output_dir)
    
    print(f"Generated {len(top_5_var)} VAR strategy visualizations")
    print(f"Generated {len(top_5_cvar)} CVAR strategy visualizations")


def _generate_single_strategy_plot(option_data, option_id, backtest, strategy_name, rank, output_dir):
    """Generate visualization for a single strategy."""
    if option_data is None or len(option_data) == 0:
        return
    
    # Determine threshold column based on strategy
    threshold_col = 'RollingVaR' if 'VAR' in strategy_name.upper() else 'RollingCVaR'
    threshold_label = 'Rolling VaR' if 'VAR' in strategy_name.upper() else 'Rolling CVaR'
    
    # Create figure with subplots (4 plots: price, z-score, returns, equity curve)
    performance_info = f"Rank #{rank} | Return: {backtest['total_return']:.2%} | Win Rate: {backtest['win_rate']:.2%} | Sharpe: {backtest['sharpe_ratio']:.2f} | Trades: {backtest['total_trades']}"
    fig, axes = plt.subplots(4, 1, figsize=(16, 14))
    fig.suptitle(f'{strategy_name} - Top #{rank}: {option_id}\n{performance_info}', fontsize=16, fontweight='bold')
    
    # Plot 1: Price with Rolling VaR/CVaR levels and trading signals
    ax1 = axes[0]
    ax1.plot(option_data.index, option_data['LastPremio'], label='LastPremio', linewidth=1.5, alpha=0.7)
    ax1.plot(option_data.index, option_data['RollingMean'], label='Rolling Mean (20 days)', linewidth=2, color='orange')
    
    # Add rolling VaR/CVaR threshold line
    rolling_mean = option_data['RollingMean'].values
    rolling_threshold = option_data[threshold_col].values
    
    if pd.notna(rolling_threshold).any():
        # Calculate threshold price level
        threshold_price = rolling_mean * (1 + rolling_threshold)
        ax1.plot(option_data.index, threshold_price, '--r', linewidth=2, 
                label=f'{threshold_label} Entry Level', alpha=0.7)
        ax1.fill_between(option_data.index, threshold_price, rolling_mean, 
                        where=(option_data['LastPremio'].values <= threshold_price),
                        alpha=0.2, color='red', label='Entry Zone')
    
    # Add 120% return target line for trades
    if len(backtest['trades']) > 0:
        trades_df = backtest['trades']
        for _, trade in trades_df.iterrows():
            entry_idx = int(trade['entry_index'])
            if entry_idx < len(option_data):
                entry_price = trade['entry_price']
                target_price = entry_price * 2.2  # 120% return = 2.2x price
                # Draw horizontal line from entry to end of data or exit
                exit_idx = min(int(trade['exit_index']), len(option_data) - 1)
                ax1.plot([entry_idx, exit_idx], [target_price, target_price], 
                        '--', color='orange', linewidth=1.5, alpha=0.5, 
                        label='120% Return Target' if _ == 0 else '')
    
    # Mark trade entry and exit points
    if len(backtest['trades']) > 0:
        trades_df = backtest['trades']
        entry_indices = trades_df['entry_index'].values
        exit_indices = trades_df['exit_index'].values
        
        # Mark entry points (winning trades in green, losing in red)
        for trade_idx, entry_idx in enumerate(entry_indices):
            if int(entry_idx) < len(option_data):
                entry_price = option_data.iloc[int(entry_idx)]['LastPremio']
                trade_return = trades_df.iloc[trade_idx]['return']
                color = 'green' if trade_return > 0 else 'red'
                ax1.scatter(entry_idx, entry_price, color=color, marker='^', s=150, 
                           zorder=6, edgecolors='black', linewidths=1, alpha=0.8, label='Entry' if trade_idx == 0 else '')
        
        # Mark exit points (120% return target)
        for trade_idx, exit_idx in enumerate(exit_indices):
            if int(exit_idx) < len(option_data):
                exit_price = option_data.iloc[int(exit_idx)]['LastPremio']
                trade_return = trades_df.iloc[trade_idx]['return']
                color = 'orange'
                marker = '*'
                label = 'Exit (120% Return)' if trade_idx == 0 else ''
                
                ax1.scatter(exit_idx, exit_price, color=color, marker=marker, s=200, 
                           zorder=6, edgecolors='black', linewidths=1, alpha=0.8, label=label)
    
    ax1.set_xlabel('Time Index')
    ax1.set_ylabel('Price (LastPremio)')
    ax1.set_title(f'Price with {threshold_label} Entry Level and Trading Signals')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Z-Score with entry zone
    ax2 = axes[1]
    ax2.plot(option_data.index, option_data['ZScore'], label='Z-Score', linewidth=1.5, color='blue')
    ax2.axhline(y=-2, color='green', linestyle='--', alpha=0.5, label='Oversold Threshold (-2σ)')
    ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)
    ax2.fill_between(option_data.index, -10, 0, alpha=0.2, color='green', label='Oversold Zone (Entry)')
    
    # Mark 120% return exit points
    if len(backtest['trades']) > 0:
        trades_df = backtest['trades']
        for _, trade in trades_df.iterrows():
            exit_idx = int(trade['exit_index'])
            if exit_idx < len(option_data):
                ax2.scatter(exit_idx, option_data.iloc[exit_idx]['ZScore'], 
                          color='orange', marker='*', s=200, zorder=5, 
                          label='120% Return Exit' if _ == 0 else '')
    
    ax2.set_xlabel('Time Index')
    ax2.set_ylabel('Z-Score')
    ax2.set_title('Z-Score: Entry (Oversold) and Exit (120% Return)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Plot 3: Rolling VaR/CVaR over time
    ax3 = axes[2]
    if threshold_col in option_data.columns:
        ax3.plot(option_data.index, option_data[threshold_col] * 100, 
                label=f'{threshold_label} (%)', linewidth=2, color='purple')
        ax3.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.3)
        ax3.set_xlabel('Time Index')
        ax3.set_ylabel(f'{threshold_label} (%)')
        ax3.set_title(f'Rolling 20-Day {threshold_label} Over Time')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
    
    # Plot 4: Equity Curve
    ax4 = axes[3]
    if len(backtest['trades']) > 0:
        trades_df = backtest['trades']
        initial_capital = 100000
        cumulative_capital = [initial_capital]
        equity_time = [0]
        
        current_capital = initial_capital
        for _, trade in trades_df.iterrows():
            current_capital = current_capital * (1 + trade['return'])
            cumulative_capital.append(current_capital)
            equity_time.append(int(trade['exit_index']))
        
        ax4.plot(equity_time, cumulative_capital, linewidth=2, color='blue', 
                label='Equity Curve', marker='o', markersize=4)
        ax4.axhline(y=initial_capital, color='gray', linestyle='--', linewidth=1, label='Initial Capital')
        
        if len(equity_time) > 1:
            profit_mask = [c >= initial_capital for c in cumulative_capital]
            if any(profit_mask):
                ax4.fill_between(equity_time, initial_capital, cumulative_capital, 
                               where=profit_mask, alpha=0.3, color='green', 
                               label='Profit Zone', interpolate=True)
            loss_mask = [c < initial_capital for c in cumulative_capital]
            if any(loss_mask):
                ax4.fill_between(equity_time, initial_capital, cumulative_capital, 
                               where=loss_mask, alpha=0.3, color='red', 
                               label='Loss Zone', interpolate=True)
        
        final_capital = cumulative_capital[-1] if len(cumulative_capital) > 0 else initial_capital
        ax4.set_xlabel('Time Index')
        ax4.set_ylabel('Capital (R$)')
        ax4.set_title(f'Equity Curve (Final: R$ {final_capital:,.2f} | Return: {backtest["total_return"]:.2%})')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        
        if final_capital > initial_capital * 2 or final_capital < initial_capital * 0.5:
            ax4.set_yscale('log')
    
    # Create filename based on strategy type
    strategy_prefix = 'var' if 'VAR' in strategy_name.upper() else 'cvar'
    plt.tight_layout()
    plt.savefig(output_dir / f'top_{strategy_prefix}_strategy_{rank}_{option_id.replace("/", "_")}.png', 
                dpi=300, bbox_inches='tight')
    plt.close()


def generate_summary_report(analysis_results, output_path):
    """Generate summary report comparing VAR and CVAR strategies."""
    print("\nGenerating summary report...")
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("VAR vs CVAR MEAN REVERSION STRATEGY ANALYSIS")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("Focus: CALL Options with Delta 0.20 to 0.05")
    report_lines.append("Strategy VAR: Buy at Rolling 20-Day VaR, Sell at 120% Return")
    report_lines.append("Strategy CVAR: Buy at Rolling 20-Day CVaR, Sell at 120% Return")
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
    
    # Separate VAR and CVAR backtest results
    var_backtests = []
    cvar_backtests = []
    
    for result in valid_results:
        if result['backtest_var']['total_trades'] > 0:
            var_backtests.append(result['backtest_var'])
        if result['backtest_cvar']['total_trades'] > 0:
            cvar_backtests.append(result['backtest_cvar'])
    
    # VAR Strategy Results
    report_lines.append("=" * 80)
    report_lines.append("VAR STRATEGY RESULTS")
    report_lines.append("=" * 80)
    report_lines.append("Entry: Rolling 20-Day VaR | Exit: 120% Return")
    report_lines.append("-" * 80)
    
    if len(var_backtests) > 0:
        var_win_rates = [bt['win_rate'] for bt in var_backtests]
        var_returns = [bt['total_return'] for bt in var_backtests]
        var_sharpes = [bt['sharpe_ratio'] for bt in var_backtests if pd.notna(bt['sharpe_ratio'])]
        var_trades = [bt['total_trades'] for bt in var_backtests]
        
        report_lines.append(f"Options with Trades: {len(var_backtests)}/{len(valid_results)}")
        report_lines.append(f"Average Win Rate: {np.mean(var_win_rates):.2%}")
        report_lines.append(f"Average Total Return: {np.mean(var_returns):.2%}")
        report_lines.append(f"Average Sharpe Ratio: {np.mean(var_sharpes):.2f}" if len(var_sharpes) > 0 else "Average Sharpe Ratio: N/A")
        report_lines.append(f"Average Trades per Option: {np.mean(var_trades):.1f}")
        report_lines.append("")
        
        # Top 5 VAR strategies
        var_successful = [bt for bt in var_backtests if bt['total_return'] > 0 and bt['win_rate'] > 0.5]
        report_lines.append(f"Successful VAR Strategies: {len(var_successful)}/{len(var_backtests)}")
        
        if len(var_successful) > 0:
            report_lines.append("")
            report_lines.append("Top 5 VAR Strategies:")
            report_lines.append("-" * 80)
            var_sorted = sorted(var_successful, key=lambda x: x['total_return'], reverse=True)[:5]
            for i, bt in enumerate(var_sorted, 1):
                report_lines.append(f"{i}. Return: {bt['total_return']:.2%} | Win Rate: {bt['win_rate']:.2%} | "
                                  f"Sharpe: {bt['sharpe_ratio']:.2f} | Trades: {bt['total_trades']}")
    else:
        report_lines.append("No VAR strategy trades executed")
    
    report_lines.append("")
    
    # CVAR Strategy Results
    report_lines.append("=" * 80)
    report_lines.append("CVAR STRATEGY RESULTS (CONSERVATIVE)")
    report_lines.append("=" * 80)
    report_lines.append("Entry: Rolling 20-Day CVaR | Exit: 120% Return")
    report_lines.append("-" * 80)
    
    if len(cvar_backtests) > 0:
        cvar_win_rates = [bt['win_rate'] for bt in cvar_backtests]
        cvar_returns = [bt['total_return'] for bt in cvar_backtests]
        cvar_sharpes = [bt['sharpe_ratio'] for bt in cvar_backtests if pd.notna(bt['sharpe_ratio'])]
        cvar_trades = [bt['total_trades'] for bt in cvar_backtests]
        
        report_lines.append(f"Options with Trades: {len(cvar_backtests)}/{len(valid_results)}")
        report_lines.append(f"Average Win Rate: {np.mean(cvar_win_rates):.2%}")
        report_lines.append(f"Average Total Return: {np.mean(cvar_returns):.2%}")
        report_lines.append(f"Average Sharpe Ratio: {np.mean(cvar_sharpes):.2f}" if len(cvar_sharpes) > 0 else "Average Sharpe Ratio: N/A")
        report_lines.append(f"Average Trades per Option: {np.mean(cvar_trades):.1f}")
        report_lines.append("")
        
        # Top 5 CVAR strategies
        cvar_successful = [bt for bt in cvar_backtests if bt['total_return'] > 0 and bt['win_rate'] > 0.5]
        report_lines.append(f"Successful CVAR Strategies: {len(cvar_successful)}/{len(cvar_backtests)}")
        
        if len(cvar_successful) > 0:
            report_lines.append("")
            report_lines.append("Top 5 CVAR Strategies:")
            report_lines.append("-" * 80)
            cvar_sorted = sorted(cvar_successful, key=lambda x: x['total_return'], reverse=True)[:5]
            for i, bt in enumerate(cvar_sorted, 1):
                report_lines.append(f"{i}. Return: {bt['total_return']:.2%} | Win Rate: {bt['win_rate']:.2%} | "
                                  f"Sharpe: {bt['sharpe_ratio']:.2f} | Trades: {bt['total_trades']}")
    else:
        report_lines.append("No CVAR strategy trades executed")
    
    report_lines.append("")
    
    # Comparison
    report_lines.append("=" * 80)
    report_lines.append("STRATEGY COMPARISON")
    report_lines.append("=" * 80)
    
    if len(var_backtests) > 0 and len(cvar_backtests) > 0:
        var_avg_return = np.mean([bt['total_return'] for bt in var_backtests])
        cvar_avg_return = np.mean([bt['total_return'] for bt in cvar_backtests])
        var_avg_win = np.mean([bt['win_rate'] for bt in var_backtests])
        cvar_avg_win = np.mean([bt['win_rate'] for bt in cvar_backtests])
        var_avg_sharpe = np.mean([bt['sharpe_ratio'] for bt in var_backtests if pd.notna(bt['sharpe_ratio'])])
        cvar_avg_sharpe = np.mean([bt['sharpe_ratio'] for bt in cvar_backtests if pd.notna(bt['sharpe_ratio'])])
        
        report_lines.append("")
        report_lines.append("Average Performance Comparison:")
        report_lines.append("-" * 80)
        report_lines.append(f"{'Metric':<25} {'VAR Strategy':<20} {'CVAR Strategy':<20}")
        report_lines.append("-" * 80)
        report_lines.append(f"{'Average Return':<25} {var_avg_return:>18.2%} {cvar_avg_return:>18.2%}")
        report_lines.append(f"{'Average Win Rate':<25} {var_avg_win:>18.2%} {cvar_avg_win:>18.2%}")
        report_lines.append(f"{'Average Sharpe Ratio':<25} {var_avg_sharpe:>18.2f} {cvar_avg_sharpe:>18.2f}")
        report_lines.append("")
        
        if var_avg_return > cvar_avg_return:
            report_lines.append("✓ VAR Strategy has higher average returns")
        elif cvar_avg_return > var_avg_return:
            report_lines.append("✓ CVAR Strategy has higher average returns")
        else:
            report_lines.append("= Both strategies have similar average returns")
        
        if var_avg_sharpe > cvar_avg_sharpe:
            report_lines.append("✓ VAR Strategy has better risk-adjusted returns (Sharpe)")
        elif cvar_avg_sharpe > var_avg_sharpe:
            report_lines.append("✓ CVAR Strategy has better risk-adjusted returns (Sharpe)")
        else:
            report_lines.append("= Both strategies have similar risk-adjusted returns")
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("CONCLUSION")
    report_lines.append("=" * 80)
    
    if len(var_backtests) > 0 and len(cvar_backtests) > 0:
        var_avg_return = np.mean([bt['total_return'] for bt in var_backtests])
        cvar_avg_return = np.mean([bt['total_return'] for bt in cvar_backtests])
        var_avg_win = np.mean([bt['win_rate'] for bt in var_backtests])
        cvar_avg_win = np.mean([bt['win_rate'] for bt in cvar_backtests])
        
        if var_avg_return > 0 and var_avg_win > 0.5:
            report_lines.append("✓ VAR Strategy appears SUCCESSFUL")
            report_lines.append(f"  - Average Return: {var_avg_return:.2%}")
            report_lines.append(f"  - Average Win Rate: {var_avg_win:.2%}")
        else:
            report_lines.append("⚠ VAR Strategy results are MIXED")
        
        report_lines.append("")
        
        if cvar_avg_return > 0 and cvar_avg_win > 0.5:
            report_lines.append("✓ CVAR Strategy appears SUCCESSFUL")
            report_lines.append(f"  - Average Return: {cvar_avg_return:.2%}")
            report_lines.append(f"  - Average Win Rate: {cvar_avg_win:.2%}")
        else:
            report_lines.append("⚠ CVAR Strategy results are MIXED")
    else:
        report_lines.append("⚠ No trades executed - strategies may need parameter adjustment")
    
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
    print("VaR/CVaR AND MEAN REVERSION STRATEGY ANALYSIS")
    print("=" * 80)
    print(f"Database: {db_path}")
    print(f"Output directory: {output_dir}")
    print("Focus: CALL Options with Delta 0.20 to 0.05")
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
        
        # Save detailed results to CSV for both strategies
        var_summary_data = []
        cvar_summary_data = []
        
        for result in analysis_results:
            if result:
                # VAR strategy summary
                var_summary_data.append({
                    'OptionID': result['option_id'],
                    'VaR_95': result['var_95'],
                    'CVaR_95': result['cvar_95'],
                    'MeanReversionSignals': result['mean_reversion_signals'],
                    'MeanReversionComplete': result['mean_reversion_complete'],
                    'MeanReversionRate': result['mean_reversion_rate'],
                    'TotalTrades': result['backtest_var']['total_trades'],
                    'WinRate': result['backtest_var']['win_rate'],
                    'TotalReturn': result['backtest_var']['total_return'],
                    'SharpeRatio': result['backtest_var']['sharpe_ratio'],
                    'MaxDrawdown': result['backtest_var']['max_drawdown']
                })
                
                # CVAR strategy summary
                cvar_summary_data.append({
                    'OptionID': result['option_id'],
                    'VaR_95': result['var_95'],
                    'CVaR_95': result['cvar_95'],
                    'MeanReversionSignals': result['mean_reversion_signals'],
                    'MeanReversionComplete': result['mean_reversion_complete'],
                    'MeanReversionRate': result['mean_reversion_rate'],
                    'TotalTrades': result['backtest_cvar']['total_trades'],
                    'WinRate': result['backtest_cvar']['win_rate'],
                    'TotalReturn': result['backtest_cvar']['total_return'],
                    'SharpeRatio': result['backtest_cvar']['sharpe_ratio'],
                    'MaxDrawdown': result['backtest_cvar']['max_drawdown']
                })
        
        if var_summary_data:
            var_df = pd.DataFrame(var_summary_data)
            var_csv_path = output_dir / 'var_strategy_summary.csv'
            var_df.to_csv(var_csv_path, index=False)
            print(f"VAR Strategy CSV saved to: {var_csv_path}")
        
        if cvar_summary_data:
            cvar_df = pd.DataFrame(cvar_summary_data)
            cvar_csv_path = output_dir / 'cvar_strategy_summary.csv'
            cvar_df.to_csv(cvar_csv_path, index=False)
            print(f"CVAR Strategy CSV saved to: {cvar_csv_path}")
        
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

