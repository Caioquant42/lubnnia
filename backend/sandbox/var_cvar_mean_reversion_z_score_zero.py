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
    
    # Mean reversion completion: price returns to mean
    df['MeanReversionComplete'] = (df['ZScore'] > 0) & (df['ZScore'].shift(1) < 0)
    
    return df


def backtest_strategy(df, var_threshold, cvar_threshold, initial_capital=100000):
    """
    Backtest mean reversion strategy.
    
    Strategy:
    - Buy when price drops to VaR or CVaR level
    - Sell when mean reversion completes (price returns to mean)
    
    Args:
        df: DataFrame with prices and signals
        var_threshold: VaR threshold (negative value)
        cvar_threshold: CVaR threshold (negative value)
        initial_capital: Initial capital for backtesting
    
    Returns:
        Dictionary with backtest results
    """
    capital = initial_capital
    positions = []
    trades = []
    current_position = None
    
    for i in range(len(df)):
        price = df.iloc[i]['LastPremio']
        rolling_mean = df.iloc[i]['RollingMean']
        z_score = df.iloc[i]['ZScore']
        
        # Entry signal: price drops to VaR or CVaR level
        if current_position is None:
            # Check if price is at or below VaR/CVaR threshold
            price_return = (price - rolling_mean) / rolling_mean if pd.notna(rolling_mean) and rolling_mean > 0 else 0
            
            if price_return <= var_threshold or price_return <= cvar_threshold:
                # Buy signal
                shares = capital / price if price > 0 else 0
                if shares > 0:
                    current_position = {
                        'entry_index': i,
                        'entry_price': price,
                        'entry_date': df.iloc[i]['Data'] if 'Data' in df.columns else i,
                        'shares': shares,
                        'entry_zscore': z_score
                    }
                    capital = 0  # All capital invested
        
        # Exit signal: mean reversion complete
        elif current_position is not None:
            if df.iloc[i]['MeanReversionComplete'] or z_score > 0:
                # Sell signal
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
                    'holding_period': i - current_position['entry_index']
                }
                
                trades.append(trade)
                current_position = None
    
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
    
    # Detect mean reversion
    mr_df = detect_mean_reversion(option_data['LastPremio'].values)
    option_data = pd.concat([option_data, mr_df[['RollingMean', 'RollingStd', 'ZScore', 
                                                  'MeanReversionSignal', 'MeanReversionComplete']]], axis=1)
    
    # Calculate mean reversion statistics
    mean_reversion_signals = option_data['MeanReversionSignal'].sum()
    mean_reversion_complete = option_data['MeanReversionComplete'].sum()
    mean_reversion_rate = mean_reversion_complete / mean_reversion_signals if mean_reversion_signals > 0 else 0
    
    # Get average delta for this option series
    avg_delta = option_data['Delta'].mean() if 'Delta' in option_data.columns else np.nan
    
    # Backtest strategy
    # Use negative VaR as threshold (since VaR is already negative for losses)
    backtest_results = backtest_strategy(option_data, var_threshold=-var_95, cvar_threshold=-cvar_99)
    
    return {
        'option_id': option_id,
        'var_95': var_95,
        'cvar_95': cvar_95,
        'var_99': var_99,
        'cvar_99': cvar_99,
        'mean_reversion_signals': mean_reversion_signals,
        'mean_reversion_complete': mean_reversion_complete,
        'mean_reversion_rate': mean_reversion_rate,
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
        
        # Add VaR/CVaR bands
        rolling_mean = option_data['RollingMean'].values
        var_95 = result['var_95']
        cvar_95 = result['cvar_95']
        
        if pd.notna(var_95) and pd.notna(cvar_95):
            var_level = rolling_mean * (1 + var_95)
            cvar_level = rolling_mean * (1 + cvar_95)
            ax1.fill_between(option_data.index, var_level, cvar_level, alpha=0.3, color='red', label='VaR/CVaR Zone')
            ax1.plot(option_data.index, var_level, '--r', linewidth=1, label=f'VaR 95% ({var_95:.2%})')
            ax1.plot(option_data.index, cvar_level, '--r', linewidth=1, alpha=0.5, label=f'CVaR 95% ({cvar_95:.2%})')
        
        # Mark mean reversion signals
        signals = option_data[option_data['MeanReversionSignal']]
        if len(signals) > 0:
            ax1.scatter(signals.index, signals['LastPremio'], color='green', marker='^', 
                       s=100, label='Buy Signal (Mean Reversion)', zorder=5)
        
        completes = option_data[option_data['MeanReversionComplete']]
        if len(completes) > 0:
            ax1.scatter(completes.index, completes['LastPremio'], color='red', marker='v', 
                       s=100, label='Sell Signal (Mean Reversion Complete)', zorder=5)
        
        ax1.set_xlabel('Time Index')
        ax1.set_ylabel('Price (LastPremio)')
        ax1.set_title('Price with VaR/CVaR Levels and Trading Signals')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Z-Score
        ax2 = axes[1]
        ax2.plot(option_data.index, option_data['ZScore'], label='Z-Score', linewidth=1.5, color='blue')
        ax2.axhline(y=-2, color='green', linestyle='--', label='Mean Reversion Threshold (-2σ)')
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5, alpha=0.5)
        ax2.axhline(y=2, color='red', linestyle='--', alpha=0.5)
        ax2.fill_between(option_data.index, -2, 0, alpha=0.2, color='green', label='Oversold Zone')
        ax2.set_xlabel('Time Index')
        ax2.set_ylabel('Z-Score')
        ax2.set_title('Z-Score (Mean Reversion Indicator)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Returns distribution with VaR/CVaR
        ax3 = axes[2]
        returns = option_data['Returns'].dropna()
        if len(returns) > 0:
            ax3.hist(returns, bins=50, alpha=0.7, edgecolor='black', label='Returns Distribution')
            if pd.notna(var_95):
                ax3.axvline(x=-var_95, color='red', linestyle='--', linewidth=2, label=f'VaR 95% ({var_95:.2%})')
            if pd.notna(cvar_95):
                ax3.axvline(x=-cvar_95, color='darkred', linestyle='--', linewidth=2, label=f'CVaR 95% ({cvar_95:.2%})')
            ax3.set_xlabel('Returns')
            ax3.set_ylabel('Frequency')
            ax3.set_title('Returns Distribution with VaR/CVaR')
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


def generate_summary_report(analysis_results, output_path):
    """Generate summary report."""
    print("\nGenerating summary report...")
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("VaR/CVaR AND MEAN REVERSION STRATEGY ANALYSIS")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("Focus: CALL Options with Delta 0.20 to 0.05")
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
    
    # Mean Reversion Statistics
    report_lines.append("Mean Reversion Statistics:")
    report_lines.append("-" * 80)
    
    mr_rates = [r['mean_reversion_rate'] for r in valid_results if pd.notna(r['mean_reversion_rate'])]
    if len(mr_rates) > 0:
        report_lines.append(f"Mean Reversion Rate - Mean: {np.mean(mr_rates):.2%}, Median: {np.median(mr_rates):.2%}")
        report_lines.append(f"Options with Mean Reversion: {sum(1 for r in mr_rates if r > 0)}/{len(mr_rates)}")
    
    report_lines.append("")
    
    # Analysis by Delta
    report_lines.append("=" * 80)
    report_lines.append("ANALYSIS BY DELTA")
    report_lines.append("=" * 80)
    
    # Group results by delta buckets
    delta_buckets = {
        '0.05-0.08': (0.05, 0.08),
        '0.08-0.10': (0.08, 0.10),
        '0.10-0.12': (0.10, 0.12),
        '0.12-0.15': (0.12, 0.15),
        '0.15-0.18': (0.15, 0.18),
        '0.18-0.20': (0.18, 0.20)
    }
    
    delta_stats = {}
    
    for bucket_name, (min_delta, max_delta) in delta_buckets.items():
        bucket_results = []
        for result in valid_results:
            avg_delta = result.get('avg_delta', np.nan)
            if pd.notna(avg_delta) and min_delta <= avg_delta < max_delta:
                bt = result['backtest_results']
                if bt['total_trades'] > 0:
                    bucket_results.append({
                        'total_return': bt['total_return'],
                        'win_rate': bt['win_rate'],
                        'sharpe_ratio': bt['sharpe_ratio'] if pd.notna(bt['sharpe_ratio']) else 0,
                        'total_trades': bt['total_trades'],
                        'avg_return': bt.get('avg_return', 0),
                        'option_id': result['option_id']
                    })
        
        if len(bucket_results) > 0:
            delta_stats[bucket_name] = {
                'count': len(bucket_results),
                'avg_sharpe': np.mean([r['sharpe_ratio'] for r in bucket_results]),
                'median_sharpe': np.median([r['sharpe_ratio'] for r in bucket_results]),
                'avg_return': np.mean([r['total_return'] for r in bucket_results]),
                'avg_win_rate': np.mean([r['win_rate'] for r in bucket_results]),
                'winning_strategies': sum(1 for r in bucket_results if r['total_return'] > 0),
                'losing_strategies': sum(1 for r in bucket_results if r['total_return'] <= 0),
                'total_trades': sum(r['total_trades'] for r in bucket_results),
                'strategies': bucket_results
            }
    
    if len(delta_stats) > 0:
        report_lines.append("")
        report_lines.append("Performance by Delta Range:")
        report_lines.append("-" * 80)
        report_lines.append(f"{'Delta Range':<15} {'Count':<8} {'Avg Sharpe':<12} {'Avg Return':<12} {'Win Rate':<10} {'Winners':<10} {'Losers':<10}")
        report_lines.append("-" * 80)
        
        for bucket_name in sorted(delta_stats.keys()):
            stats = delta_stats[bucket_name]
            report_lines.append(f"{bucket_name:<15} {stats['count']:<8} {stats['avg_sharpe']:>11.2f} "
                              f"{stats['avg_return']:>11.2%} {stats['avg_win_rate']:>9.2%} "
                              f"{stats['winning_strategies']:<10} {stats['losing_strategies']:<10}")
        
        report_lines.append("")
        
        # Find top 5 best performing strategies by Sharpe ratio across all deltas
        all_strategies = []
        for bucket_name, stats in delta_stats.items():
            for strategy in stats['strategies']:
                all_strategies.append({
                    'delta_bucket': bucket_name,
                    'option_id': strategy['option_id'],
                    'sharpe_ratio': strategy['sharpe_ratio'],
                    'total_return': strategy['total_return'],
                    'win_rate': strategy['win_rate'],
                    'total_trades': strategy['total_trades']
                })
        
        if len(all_strategies) > 0:
            # Sort by Sharpe ratio
            all_strategies_sorted = sorted(all_strategies, key=lambda x: x['sharpe_ratio'], reverse=True)
            top_5_by_sharpe = all_strategies_sorted[:5]
            
            report_lines.append("Top 5 Best Performing Strategies by Sharpe Ratio:")
            report_lines.append("-" * 80)
            for i, strategy in enumerate(top_5_by_sharpe, 1):
                report_lines.append(f"{i}. Delta: {strategy['delta_bucket']} | Option: {strategy['option_id']} | "
                                  f"Sharpe: {strategy['sharpe_ratio']:.2f} | Return: {strategy['total_return']:.2%} | "
                                  f"Win Rate: {strategy['win_rate']:.2%} | Trades: {strategy['total_trades']}")
            
            report_lines.append("")
            
            # Sort by total return
            all_strategies_sorted_return = sorted(all_strategies, key=lambda x: x['total_return'], reverse=True)
            top_5_by_return = all_strategies_sorted_return[:5]
            
            report_lines.append("Top 5 Best Performing Strategies by Total Return:")
            report_lines.append("-" * 80)
            for i, strategy in enumerate(top_5_by_return, 1):
                report_lines.append(f"{i}. Delta: {strategy['delta_bucket']} | Option: {strategy['option_id']} | "
                                  f"Return: {strategy['total_return']:.2%} | Sharpe: {strategy['sharpe_ratio']:.2f} | "
                                  f"Win Rate: {strategy['win_rate']:.2%} | Trades: {strategy['total_trades']}")
            
            report_lines.append("")
            
            # Identify best delta buckets
            if len(delta_stats) > 0:
                best_sharpe_delta = max(delta_stats.items(), key=lambda x: x[1]['avg_sharpe'])
                best_return_delta = max(delta_stats.items(), key=lambda x: x[1]['avg_return'])
                
                report_lines.append("Best Delta Ranges:")
                report_lines.append("-" * 80)
                report_lines.append(f"✓ Best Sharpe Ratio: {best_sharpe_delta[0]} (Sharpe: {best_sharpe_delta[1]['avg_sharpe']:.2f}, "
                                  f"Return: {best_sharpe_delta[1]['avg_return']:.2%}, Win Rate: {best_sharpe_delta[1]['avg_win_rate']:.2%})")
                report_lines.append(f"✓ Best Average Return: {best_return_delta[0]} (Return: {best_return_delta[1]['avg_return']:.2%}, "
                                  f"Sharpe: {best_return_delta[1]['avg_sharpe']:.2f}, Win Rate: {best_return_delta[1]['avg_win_rate']:.2%})")
    
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
                    'MeanReversionSignals': result['mean_reversion_signals'],
                    'MeanReversionComplete': result['mean_reversion_complete'],
                    'MeanReversionRate': result['mean_reversion_rate'],
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

