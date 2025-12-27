#!/usr/bin/env python3
"""
Elasticity Analysis for BOVA Options

Analyzes options data to find delta ranges where options exhibit high elasticity
(price sensitivity to 1% stock movements) throughout their lifetime.
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


def calculate_elasticity(delta, underlying_price, option_price, risk_free_rate=0.0, time_to_expiry=0.0):
    """
    Calculate elasticity from delta and prices.
    
    For calls: Λ = (Se^(-rT)N(d1))/c = Delta × (S/c)
    For puts: Λ = (Se^(-rT)N(-d1))/p = Delta × (S/p)
    
    Simplified version: Λ = Delta × (S / option_price)
    
    Args:
        delta: Option delta (positive for calls, negative for puts)
        underlying_price: Current underlying asset price (S)
        option_price: Option price (c for calls, p for puts)
        risk_free_rate: Risk-free rate (default 0 for simplified calculation)
        time_to_expiry: Time to expiration in years (default 0 for simplified)
    
    Returns:
        Elasticity value (float)
    """
    if option_price is None or option_price <= 0:
        return np.nan
    
    if underlying_price is None or underlying_price <= 0:
        return np.nan
    
    if delta is None or np.isnan(delta):
        return np.nan
    
    # Simplified elasticity: Λ = Delta × (S / option_price)
    # This is equivalent to the full formula when rT is small
    elasticity = delta * (underlying_price / option_price)
    
    return elasticity


def load_and_prepare_data(db_path):
    """
    Load and join options with underlying prices.
    
    Args:
        db_path: Path to the SQLite database
    
    Returns:
        DataFrame with options data joined with underlying prices
    """
    print(f"Loading data from {db_path}...")
    
    if not Path(db_path).exists():
        raise FileNotFoundError(f"Database file '{db_path}' not found!")
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Load options data
        print("Loading options data...")
        options_query = """
            SELECT 
                id, Ativo, Data, Tipo, K, Delta, BS_Price, Bid, Ask, LastPremio,
                Vol_imp, Dias4Vencimento, Vencimento, Gama, Theta, Vega, Rho
            FROM options_data
            WHERE Tipo IN ('CALL', 'PUT')
            AND Delta IS NOT NULL
        """
        options_df = pd.read_sql_query(options_query, conn)
        print(f"Loaded {len(options_df):,} option records")
        
        # Load underlying asset prices (BOVA11)
        print("Loading underlying asset prices...")
        underlying_query = """
            SELECT Data, BS_Price, Bid, Ask, LastPremio
            FROM options_data
            WHERE Tipo = 'AtivoSubjacente'
            AND Ativo = 'BOVA11'
        """
        underlying_df = pd.read_sql_query(underlying_query, conn)
        
        # Use LastPremio, or midpoint of Bid/Ask, or BS_Price as underlying price
        underlying_df['UnderlyingPrice'] = underlying_df.apply(
            lambda row: (
                row['LastPremio'] if pd.notna(row['LastPremio']) and row['LastPremio'] > 0
                else (row['Bid'] + row['Ask']) / 2 if pd.notna(row['Bid']) and pd.notna(row['Ask']) and row['Bid'] > 0 and row['Ask'] > 0
                else row['BS_Price'] if pd.notna(row['BS_Price']) and row['BS_Price'] > 0
                else np.nan
            ),
            axis=1
        )
        
        # Filter out rows without valid price
        underlying_df = underlying_df[underlying_df['UnderlyingPrice'].notna() & (underlying_df['UnderlyingPrice'] > 0)]
        print(f"Loaded {len(underlying_df):,} underlying price records")
        
        # Convert Data to datetime for proper joining
        options_df['Data'] = pd.to_datetime(options_df['Data'], format='%Y.%m.%d %H:%M:%S', errors='coerce')
        underlying_df['Data'] = pd.to_datetime(underlying_df['Data'], format='%Y.%m.%d %H:%M:%S', errors='coerce')
        
        # Round timestamps to nearest minute for joining (since options and underlying may have slightly different timestamps)
        options_df['Data_rounded'] = options_df['Data'].dt.round('1min')
        underlying_df['Data_rounded'] = underlying_df['Data'].dt.round('1min')
        
        # Merge options with underlying prices
        print("Joining options with underlying prices...")
        merged_df = options_df.merge(
            underlying_df[['Data_rounded', 'UnderlyingPrice', 'Bid', 'Ask', 'LastPremio']],
            on='Data_rounded',
            how='inner',
            suffixes=('', '_underlying')
        )
        
        # Use underlying price from the merge
        merged_df['S'] = merged_df['UnderlyingPrice']
        
        # Ensure Dias4Vencimento is preserved (it should be from options_df)
        if 'Dias4Vencimento' not in merged_df.columns:
            print("Warning: Dias4Vencimento column missing after merge!")
        
        # For market price, use midpoint of Bid/Ask or LastPremio
        merged_df['MarketPrice'] = merged_df.apply(
            lambda row: (
                row['LastPremio'] if pd.notna(row['LastPremio']) and row['LastPremio'] > 0
                else (row['Bid'] + row['Ask']) / 2 if pd.notna(row['Bid']) and pd.notna(row['Ask']) and row['Bid'] > 0 and row['Ask'] > 0
                else np.nan
            ),
            axis=1
        )
        
        print(f"After joining: {len(merged_df):,} records")
        
        # Filter out rows with missing critical data
        initial_count = len(merged_df)
        merged_df = merged_df[
            (merged_df['Delta'].notna()) &
            (merged_df['S'].notna()) &
            (merged_df['S'] > 0) &
            (merged_df['BS_Price'].notna()) &
            (merged_df['BS_Price'] > 0)
        ]
        
        print(f"After filtering: {len(merged_df):,} records (removed {initial_count - len(merged_df):,})")
        
        # Filter by valid delta ranges (focus on ATM and OTM)
        # CALLS: delta 0.60 to 0.01
        calls_df = merged_df[
            (merged_df['Tipo'] == 'CALL') &
            (merged_df['Delta'] >= 0.01) &
            (merged_df['Delta'] <= 0.60)
        ]
        
        # PUTS: delta -0.60 to -0.01
        puts_df = merged_df[
            (merged_df['Tipo'] == 'PUT') &
            (merged_df['Delta'] <= -0.01) &
            (merged_df['Delta'] >= -0.60)
        ]
        
        print(f"Valid calls: {len(calls_df):,}")
        print(f"Valid puts: {len(puts_df):,}")
        
        return pd.concat([calls_df, puts_df], ignore_index=True)
        
    finally:
        conn.close()


def classify_option_type(ticker):
    """
    Classify option as weekly or monthly based on ticker naming.
    
    Args:
        ticker: Option ticker (e.g., 'BOVAE102W1' or 'BOVAE100')
    
    Returns:
        'weekly' if ticker contains 'W', 'monthly' otherwise
    """
    if pd.isna(ticker):
        return 'unknown'
    
    ticker_str = str(ticker).upper()
    if 'W' in ticker_str:
        return 'weekly'
    else:
        return 'monthly'


def bucket_delta(delta, option_type):
    """
    Assign delta to bucket.
    Focus on ATM and OTM options:
    - CALLS: delta 0.60 to 0.01
    - PUTS: delta -0.60 to -0.01
    
    Args:
        delta: Option delta value
        option_type: 'CALL' or 'PUT'
    
    Returns:
        Delta bucket label (str) or None if outside range
    """
    if pd.isna(delta):
        return None
    
    if option_type == 'CALL':
        # Focus on delta 0.60 to 0.01 (ATM and OTM)
        if 0.50 <= delta < 0.60:
            return '0.50-0.60'
        elif 0.40 <= delta < 0.50:
            return '0.40-0.50'
        elif 0.30 <= delta < 0.40:
            return '0.30-0.40'
        elif 0.20 <= delta < 0.30:
            return '0.20-0.30'
        elif 0.10 <= delta < 0.20:
            return '0.10-0.20'
        elif 0.05 <= delta < 0.10:
            return '0.05-0.10'
        elif 0.01 <= delta < 0.05:
            return '0.01-0.05'
        else:
            # Outside range (delta > 0.60 or < 0.01)
            return None
    
    else:  # PUT
        # Focus on delta -0.60 to -0.01 (ATM and OTM)
        if -0.60 < delta <= -0.50:
            return '-0.60--0.50'
        elif -0.50 < delta <= -0.40:
            return '-0.50--0.40'
        elif -0.40 < delta <= -0.30:
            return '-0.40--0.30'
        elif -0.30 < delta <= -0.20:
            return '-0.30--0.20'
        elif -0.20 < delta <= -0.10:
            return '-0.20--0.10'
        elif -0.10 < delta <= -0.05:
            return '-0.10--0.05'
        elif -0.05 < delta <= -0.01:
            return '-0.05--0.01'
        else:
            # Outside range (delta < -0.60 or > -0.01)
            return None


def bucket_time_to_expiry(days):
    """
    Assign time to expiration to bucket.
    
    Args:
        days: Days to expiration
    
    Returns:
        Time bucket label (str)
    """
    if pd.isna(days) or days < 0:
        return 'unknown'
    
    if days <= 7:
        return '0-7 days'
    elif days <= 14:
        return '8-14 days'
    elif days <= 30:
        return '15-30 days'
    elif days <= 60:
        return '31-60 days'
    elif days <= 90:
        return '61-90 days'
    else:
        return '90+ days'


def analyze_elasticity_by_delta(df, option_type, price_type='BS_Price', risk_free_rate=0.0):
    """
    Main analysis function to calculate elasticity statistics by delta buckets.
    
    Args:
        df: DataFrame with options data
        option_type: 'CALL' or 'PUT'
        price_type: 'BS_Price' or 'MarketPrice'
        risk_free_rate: Risk-free rate for calculations
    
    Returns:
        Tuple of (statistics_df, raw_data_df) where:
        - statistics_df: DataFrame with statistics grouped by delta bucket and time-to-expiration
        - raw_data_df: DataFrame with raw data including elasticity calculations
    """
    print(f"\nAnalyzing {option_type} options using {price_type}...")
    
    # Filter by option type
    filtered_df = df[df['Tipo'] == option_type].copy()
    
    if len(filtered_df) == 0:
        print(f"No {option_type} options found!")
        return pd.DataFrame(), pd.DataFrame()
    
    # Calculate elasticity
    filtered_df['Elasticity'] = filtered_df.apply(
        lambda row: calculate_elasticity(
            row['Delta'],
            row['S'],
            row[price_type],
            risk_free_rate,
            row.get('Dias4Vencimento', 0) / 365.0 if pd.notna(row.get('Dias4Vencimento')) else 0
        ),
        axis=1
    )
    
    # Add classifications
    filtered_df['OptionFrequency'] = filtered_df['Ativo'].apply(classify_option_type)
    filtered_df['DeltaBucket'] = filtered_df.apply(
        lambda row: bucket_delta(row['Delta'], row['Tipo']),
        axis=1
    )
    
    # Check if Dias4Vencimento exists before using it
    if 'Dias4Vencimento' in filtered_df.columns:
        filtered_df['TimeBucket'] = filtered_df['Dias4Vencimento'].apply(bucket_time_to_expiry)
    else:
        print(f"  Warning: 'Dias4Vencimento' column not found, creating placeholder")
        filtered_df['TimeBucket'] = 'unknown'
    
    # Filter to only include deltas in the specified range (remove None buckets)
    filtered_df = filtered_df[filtered_df['DeltaBucket'].notna()]
    
    # Remove invalid elasticity values
    filtered_df = filtered_df[filtered_df['Elasticity'].notna()]
    filtered_df = filtered_df[np.isfinite(filtered_df['Elasticity'])]
    
    # For calls, filter out negative elasticity (should be > 0)
    if option_type == 'CALL':
        filtered_df = filtered_df[filtered_df['Elasticity'] > 0]
    # For puts, filter out positive elasticity (should be < 0)
    else:
        filtered_df = filtered_df[filtered_df['Elasticity'] < 0]
    
    print(f"Valid elasticity calculations: {len(filtered_df):,}")
    
    # Group by delta bucket, time bucket, and option frequency
    grouped = filtered_df.groupby(['DeltaBucket', 'TimeBucket', 'OptionFrequency'])
    
    # Calculate statistics
    stats_list = []
    for (delta_bucket, time_bucket, freq), group in grouped:
        if len(group) == 0:
            continue
        
        elasticity_values = group['Elasticity'].values
        
        stats_dict = {
            'OptionType': option_type,
            'DeltaBucket': delta_bucket,
            'TimeBucket': time_bucket,
            'OptionFrequency': freq,
            'Count': len(group),
            'MeanElasticity': np.mean(elasticity_values),
            'MedianElasticity': np.median(elasticity_values),
            'StdElasticity': np.std(elasticity_values),
            'MinElasticity': np.min(elasticity_values),
            'MaxElasticity': np.max(elasticity_values),
            'Q25Elasticity': np.percentile(elasticity_values, 25),
            'Q75Elasticity': np.percentile(elasticity_values, 75),
            'CoeffVariation': np.std(elasticity_values) / np.abs(np.mean(elasticity_values)) if np.mean(elasticity_values) != 0 else np.nan,
        }
        
        stats_list.append(stats_dict)
    
    result_df = pd.DataFrame(stats_list)
    
    if len(result_df) > 0:
        print(f"Generated statistics for {len(result_df)} groups")
    
    # Return both statistics and raw data
    return result_df, filtered_df


def generate_visualizations(results_dict, raw_data_dict, output_dir):
    """
    Create charts and plots.
    
    Args:
        results_dict: Dictionary with analysis statistics
        raw_data_dict: Dictionary with raw data including elasticity
        output_dir: Directory to save plots
    """
    print("\nGenerating visualizations...")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Set style
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    
    # 1. Heatmap: Elasticity vs Delta vs Time-to-Expiration
    for option_type in ['CALL', 'PUT']:
        for price_type in ['BS_Price', 'MarketPrice']:
            key = f"{option_type}_{price_type}"
            if key not in results_dict or len(results_dict[key]) == 0:
                continue
            
            df = results_dict[key]
            
            # Create pivot table for heatmap
            pivot = df.pivot_table(
                values='MeanElasticity',
                index='DeltaBucket',
                columns='TimeBucket',
                aggfunc='mean'
            )
            
            if len(pivot) > 0:
                plt.figure(figsize=(14, 10))
                sns.heatmap(
                    pivot,
                    annot=True,
                    fmt='.2f',
                    cmap='viridis',
                    cbar_kws={'label': 'Mean Elasticity'}
                )
                plt.title(f'Elasticity Heatmap: {option_type} Options ({price_type})', fontsize=16, fontweight='bold')
                plt.xlabel('Time to Expiration', fontsize=12)
                plt.ylabel('Delta Bucket', fontsize=12)
                plt.tight_layout()
                plt.savefig(output_dir / f'heatmap_{option_type.lower()}_{price_type.lower()}.png', dpi=300, bbox_inches='tight')
                plt.close()
    
    # 2. Line plots: Mean elasticity by delta range (weekly vs monthly)
    for option_type in ['CALL', 'PUT']:
        for price_type in ['BS_Price', 'MarketPrice']:
            key = f"{option_type}_{price_type}"
            if key not in results_dict or len(results_dict[key]) == 0:
                continue
            
            df = results_dict[key]
            
            # Aggregate by delta bucket and frequency
            delta_agg = df.groupby(['DeltaBucket', 'OptionFrequency'])['MeanElasticity'].mean().reset_index()
            
            if len(delta_agg) > 0:
                plt.figure(figsize=(14, 8))
                
                for freq in ['weekly', 'monthly']:
                    freq_data = delta_agg[delta_agg['OptionFrequency'] == freq]
                    if len(freq_data) > 0:
                        plt.plot(
                            freq_data['DeltaBucket'],
                            freq_data['MeanElasticity'],
                            marker='o',
                            label=f'{freq.capitalize()} Options',
                            linewidth=2,
                            markersize=8
                        )
                
                plt.title(f'Mean Elasticity by Delta Range: {option_type} Options ({price_type})', fontsize=16, fontweight='bold')
                plt.xlabel('Delta Bucket', fontsize=12)
                plt.ylabel('Mean Elasticity', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.legend()
                plt.grid(True, alpha=0.3)
                plt.tight_layout()
                plt.savefig(output_dir / f'lineplot_{option_type.lower()}_{price_type.lower()}.png', dpi=300, bbox_inches='tight')
                plt.close()
    
    # 3. Box plots: Elasticity distribution by delta buckets
    for option_type in ['CALL', 'PUT']:
        for price_type in ['BS_Price', 'MarketPrice']:
            key = f"{option_type}_{price_type}"
            if key not in raw_data_dict or len(raw_data_dict[key]) == 0:
                continue
            
            raw_df = raw_data_dict[key]
            
            # Filter to top delta buckets with sufficient data
            delta_counts = raw_df['DeltaBucket'].value_counts()
            top_deltas = delta_counts[delta_counts >= 50].index.tolist()[:10]  # Top 10 with at least 50 observations
            
            if len(top_deltas) > 0:
                filtered_raw = raw_df[raw_df['DeltaBucket'].isin(top_deltas)]
                
                plt.figure(figsize=(16, 10))
                sns.boxplot(
                    data=filtered_raw,
                    x='DeltaBucket',
                    y='Elasticity',
                    hue='OptionFrequency',
                    order=sorted(top_deltas)
                )
                plt.title(f'Elasticity Distribution by Delta Range: {option_type} Options ({price_type})', fontsize=16, fontweight='bold')
                plt.xlabel('Delta Bucket', fontsize=12)
                plt.ylabel('Elasticity', fontsize=12)
                plt.xticks(rotation=45, ha='right')
                plt.legend(title='Option Frequency')
                plt.tight_layout()
                plt.savefig(output_dir / f'boxplot_{option_type.lower()}_{price_type.lower()}.png', dpi=300, bbox_inches='tight')
                plt.close()
    
    # 4. Time evolution: Elasticity vs Days to Expiration
    for option_type in ['CALL', 'PUT']:
        for price_type in ['BS_Price', 'MarketPrice']:
            key = f"{option_type}_{price_type}"
            if key not in raw_data_dict or len(raw_data_dict[key]) == 0:
                continue
            
            raw_df = raw_data_dict[key]
            
            # Sample data for plotting (to avoid too many points)
            if len(raw_df) > 10000:
                sample_df = raw_df.sample(n=10000, random_state=42)
            else:
                sample_df = raw_df.copy()
            
            plt.figure(figsize=(14, 8))
            
            for freq in ['weekly', 'monthly']:
                freq_data = sample_df[sample_df['OptionFrequency'] == freq]
                if len(freq_data) > 0:
                    plt.scatter(
                        freq_data['Dias4Vencimento'],
                        freq_data['Elasticity'],
                        alpha=0.3,
                        s=10,
                        label=f'{freq.capitalize()} Options'
                    )
            
            plt.title(f'Elasticity vs Days to Expiration: {option_type} Options ({price_type})', fontsize=16, fontweight='bold')
            plt.xlabel('Days to Expiration', fontsize=12)
            plt.ylabel('Elasticity', fontsize=12)
            plt.legend()
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir / f'time_evolution_{option_type.lower()}_{price_type.lower()}.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    print(f"Visualizations saved to {output_dir}")


def generate_summary_report(results_dict, output_path, risk_free_rate):
    """
    Generate text report with key findings.
    
    Args:
        results_dict: Dictionary with analysis results
        output_path: Path to save report
        risk_free_rate: Risk-free rate used in calculations
    """
    print(f"\nGenerating summary report...")
    
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("ELASTICITY ANALYSIS REPORT - BOVA OPTIONS")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Risk-free rate used: {risk_free_rate:.4f}")
    report_lines.append("Note: MarketPrice uses actual market prices (LastPremio or Bid/Ask midpoint)")
    report_lines.append("")
    
    # Key findings for each option type and price type
    for option_type in ['CALL', 'PUT']:
        for price_type in ['BS_Price', 'MarketPrice']:
            key = f"{option_type}_{price_type}"
            if key not in results_dict or len(results_dict[key]) == 0:
                continue
            
            df = results_dict[key]
            report_lines.append(f"\n{'=' * 80}")
            report_lines.append(f"{option_type} OPTIONS - {price_type}")
            report_lines.append(f"{'=' * 80}")
            report_lines.append("")
            
            # Find delta ranges with highest mean elasticity
            overall_stats = df.groupby('DeltaBucket')['MeanElasticity'].agg(['mean', 'count']).reset_index()
            overall_stats = overall_stats.sort_values('mean', ascending=False if option_type == 'CALL' else True)
            
            report_lines.append("Top 5 Delta Ranges by Mean Elasticity:")
            report_lines.append("-" * 80)
            for idx, row in overall_stats.head(5).iterrows():
                report_lines.append(f"  Delta {row['DeltaBucket']:15} | Mean Elasticity: {row['mean']:8.2f} | Count: {int(row['count']):>8,}")
            
            # Weekly vs Monthly comparison
            report_lines.append("")
            report_lines.append("Weekly vs Monthly Comparison:")
            report_lines.append("-" * 80)
            
            freq_comparison = df.groupby('OptionFrequency')['MeanElasticity'].agg(['mean', 'std', 'count']).reset_index()
            for idx, row in freq_comparison.iterrows():
                report_lines.append(
                    f"  {row['OptionFrequency'].capitalize():10} | "
                    f"Mean: {row['mean']:8.2f} | "
                    f"Std: {row['std']:8.2f} | "
                    f"Count: {int(row['count']):>8,}"
                )
            
            # Time to expiration analysis
            report_lines.append("")
            report_lines.append("Elasticity by Time to Expiration:")
            report_lines.append("-" * 80)
            
            time_stats = df.groupby('TimeBucket')['MeanElasticity'].agg(['mean', 'count']).reset_index()
            time_stats = time_stats.sort_values('mean', ascending=False if option_type == 'CALL' else True)
            
            for idx, row in time_stats.iterrows():
                report_lines.append(
                    f"  {row['TimeBucket']:15} | "
                    f"Mean Elasticity: {row['mean']:8.2f} | "
                    f"Count: {int(row['count']):>8,}"
                )
    
    # Recommendations
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("=" * 80)
    report_lines.append("")
    report_lines.append("Based on the analysis, the optimal delta ranges for high elasticity are:")
    report_lines.append("")
    
    # This will be filled with actual findings
    for option_type in ['CALL', 'PUT']:
        for price_type in ['BS_Price', 'MarketPrice']:
            key = f"{option_type}_{price_type}"
            if key not in results_dict or len(results_dict[key]) == 0:
                continue
            
            df = results_dict[key]
            overall_stats = df.groupby('DeltaBucket')['MeanElasticity'].agg(['mean', 'count']).reset_index()
            overall_stats = overall_stats[overall_stats['count'] >= 100]  # Only consider buckets with sufficient data
            
            if option_type == 'CALL':
                overall_stats = overall_stats.sort_values('mean', ascending=False)
            else:
                overall_stats = overall_stats.sort_values('mean', ascending=True)
            
            top_ranges = overall_stats.head(3)
            if len(top_ranges) > 0:
                report_lines.append(f"{option_type} Options ({price_type}):")
                for idx, row in top_ranges.iterrows():
                    report_lines.append(f"  - Delta {row['DeltaBucket']}: Mean Elasticity = {row['mean']:.2f} (n={int(row['count']):,})")
                report_lines.append("")
    
    # Write report
    report_text = "\n".join(report_lines)
    Path(output_path).write_text(report_text, encoding='utf-8')
    print(f"Summary report saved to {output_path}")


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Elasticity Analysis for BOVA Options')
    parser.add_argument('--db', type=str, default='BOVA_monthly.db', help='Path to database file (default: BOVA_monthly.db)')
    parser.add_argument('--risk-free-rate', type=float, default=0.1375, help='Risk-free rate (default: 0.1375 = 13.75%%)')
    parser.add_argument('--output-dir', type=str, default='elasticity_analysis_output', help='Output directory')
    
    args = parser.parse_args()
    
    db_path = Path(__file__).parent / args.db
    output_dir = Path(__file__).parent / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    risk_free_rate = args.risk_free_rate
    
    print("=" * 80)
    print("ELASTICITY ANALYSIS FOR BOVA OPTIONS (MONTHLY)")
    print("=" * 80)
    print(f"Database: {db_path}")
    print(f"Risk-free rate: {risk_free_rate:.4f}")
    print(f"Output directory: {output_dir}")
    print("\nFocus: ATM and OTM Options")
    print("  CALLS: Delta 0.60 to 0.01")
    print("  PUTS: Delta -0.60 to -0.01")
    print("=" * 80)
    
    try:
        # Load and prepare data
        df = load_and_prepare_data(db_path)
        
        if len(df) == 0:
            print("No valid data found!")
            return
        
        # Analyze elasticity for different combinations
        results_dict = {}
        raw_data_dict = {}
        
        for option_type in ['CALL', 'PUT']:
            for price_type in ['BS_Price', 'MarketPrice']:
                key = f"{option_type}_{price_type}"
                stats_df, raw_df = analyze_elasticity_by_delta(df, option_type, price_type, risk_free_rate)
                results_dict[key] = stats_df
                raw_data_dict[key] = raw_df
                
                # Save CSV for statistics
                if len(stats_df) > 0:
                    csv_path = output_dir / f'elasticity_by_delta_{option_type.lower()}_{price_type.lower()}.csv'
                    stats_df.to_csv(csv_path, index=False)
                    print(f"Saved CSV: {csv_path}")
        
        # Generate time evolution analysis
        print("\nGenerating time evolution analysis...")
        time_evolution_list = []
        for option_type in ['CALL', 'PUT']:
            for price_type in ['BS_Price', 'MarketPrice']:
                key = f"{option_type}_{price_type}"
                if key not in raw_data_dict or len(raw_data_dict[key]) == 0:
                    continue
            
            raw_df = raw_data_dict[key].copy()  # Make a copy to avoid modifying the original
            
            # Check if Dias4Vencimento column exists
            if 'Dias4Vencimento' not in raw_df.columns:
                print(f"  Warning: 'Dias4Vencimento' column not found for {key}")
                print(f"    Available columns: {list(raw_df.columns)}")
                print(f"    Skipping time evolution analysis for {key}")
                continue
            
            # Filter out rows with missing Dias4Vencimento
            raw_df = raw_df[raw_df['Dias4Vencimento'].notna()]
            
            if len(raw_df) == 0:
                print(f"  No valid Dias4Vencimento data for {key}, skipping")
                continue
            
            # Group by days to expiration buckets
            time_buckets = [0, 7, 14, 30, 60, 90, 180, 365]
            try:
                raw_df['DaysBucket'] = pd.cut(
                    raw_df['Dias4Vencimento'],
                    bins=time_buckets + [float('inf')],
                    labels=['0-7', '8-14', '15-30', '31-60', '61-90', '91-180', '181-365', '365+'],
                    include_lowest=True
                )
            except Exception as e:
                print(f"  Error creating DaysBucket for {key}: {e}")
                continue
            
            for days_bucket in raw_df['DaysBucket'].cat.categories:
                bucket_data = raw_df[raw_df['DaysBucket'] == days_bucket]
                if len(bucket_data) > 0:
                    for freq in ['weekly', 'monthly']:
                        freq_data = bucket_data[bucket_data['OptionFrequency'] == freq]
                        if len(freq_data) > 0:
                            time_evolution_list.append({
                                'OptionType': option_type,
                                'PriceType': price_type,
                                'DaysBucket': days_bucket,
                                'OptionFrequency': freq,
                                'MeanElasticity': np.mean(freq_data['Elasticity']),
                                'MedianElasticity': np.median(freq_data['Elasticity']),
                                'StdElasticity': np.std(freq_data['Elasticity']),
                                'Count': len(freq_data)
                            })
        
        if time_evolution_list:
            time_evolution_df = pd.DataFrame(time_evolution_list)
            time_csv_path = output_dir / 'elasticity_time_evolution.csv'
            time_evolution_df.to_csv(time_csv_path, index=False)
            print(f"Saved time evolution CSV: {time_csv_path}")
        
        # Generate visualizations
        generate_visualizations(results_dict, raw_data_dict, output_dir)
        
        # Generate summary report
        report_path = output_dir / 'elasticity_analysis_report.txt'
        generate_summary_report(results_dict, report_path, risk_free_rate)
        
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

