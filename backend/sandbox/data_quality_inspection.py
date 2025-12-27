#!/usr/bin/env python3
"""
Data Quality Inspection for BOVA Monthly Options Database

Identifies invalid data, outliers, and potential data collection errors.
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import sys
from scipy import stats


def check_missing_values(df, option_type):
    """Check for missing values in critical columns."""
    print(f"\n{'='*80}")
    print(f"MISSING VALUES CHECK - {option_type}")
    print(f"{'='*80}")
    
    critical_columns = ['Delta', 'BS_Price', 'Bid', 'Ask', 'K', 'Dias4Vencimento', 
                       'Vol_imp', 'Gama', 'Theta', 'Vega', 'Rho']
    
    issues = []
    for col in critical_columns:
        if col in df.columns:
            missing_count = df[col].isna().sum()
            missing_pct = (missing_count / len(df)) * 100 if len(df) > 0 else 0
            if missing_count > 0:
                issues.append({
                    'Column': col,
                    'Missing': missing_count,
                    'Percentage': missing_pct
                })
                print(f"  ⚠️  {col:20} | Missing: {missing_count:>8,} ({missing_pct:>5.2f}%)")
            else:
                print(f"  ✓  {col:20} | No missing values")
    
    return issues


def check_invalid_ranges(df, option_type):
    """Check for values outside valid ranges."""
    print(f"\n{'='*80}")
    print(f"INVALID RANGES CHECK - {option_type}")
    print(f"{'='*80}")
    
    issues = []
    
    # Delta checks
    if 'Delta' in df.columns:
        if option_type == 'CALL':
            invalid_delta = df[(df['Delta'] < 0) | (df['Delta'] > 1)]
            if len(invalid_delta) > 0:
                issues.append({
                    'Issue': 'Invalid Delta (CALL should be 0-1)',
                    'Count': len(invalid_delta),
                    'Min': invalid_delta['Delta'].min() if len(invalid_delta) > 0 else None,
                    'Max': invalid_delta['Delta'].max() if len(invalid_delta) > 0 else None
                })
                print(f"  ⚠️  Invalid Delta (CALL should be 0-1): {len(invalid_delta):,} records")
                print(f"      Range: {invalid_delta['Delta'].min():.4f} to {invalid_delta['Delta'].max():.4f}")
        else:  # PUT
            invalid_delta = df[(df['Delta'] > 0) | (df['Delta'] < -1)]
            if len(invalid_delta) > 0:
                issues.append({
                    'Issue': 'Invalid Delta (PUT should be -1 to 0)',
                    'Count': len(invalid_delta),
                    'Min': invalid_delta['Delta'].min() if len(invalid_delta) > 0 else None,
                    'Max': invalid_delta['Delta'].max() if len(invalid_delta) > 0 else None
                })
                print(f"  ⚠️  Invalid Delta (PUT should be -1 to 0): {len(invalid_delta):,} records")
                print(f"      Range: {invalid_delta['Delta'].min():.4f} to {invalid_delta['Delta'].max():.4f}")
    
    # Price checks
    if 'BS_Price' in df.columns:
        negative_prices = df[df['BS_Price'] < 0]
        if len(negative_prices) > 0:
            issues.append({'Issue': 'Negative BS_Price', 'Count': len(negative_prices)})
            print(f"  ⚠️  Negative BS_Price: {len(negative_prices):,} records")
    
    if 'Bid' in df.columns and 'Ask' in df.columns:
        # Bid should be <= Ask
        invalid_spread = df[(df['Bid'] > df['Ask']) & df['Bid'].notna() & df['Ask'].notna()]
        if len(invalid_spread) > 0:
            issues.append({'Issue': 'Bid > Ask', 'Count': len(invalid_spread)})
            print(f"  ⚠️  Bid > Ask: {len(invalid_spread):,} records")
        
        # Negative bid/ask
        negative_bid = df[df['Bid'] < 0]
        negative_ask = df[df['Ask'] < 0]
        if len(negative_bid) > 0:
            issues.append({'Issue': 'Negative Bid', 'Count': len(negative_bid)})
            print(f"  ⚠️  Negative Bid: {len(negative_bid):,} records")
        if len(negative_ask) > 0:
            issues.append({'Issue': 'Negative Ask', 'Count': len(negative_ask)})
            print(f"  ⚠️  Negative Ask: {len(negative_ask):,} records")
    
    # Strike price checks
    if 'K' in df.columns:
        negative_strike = df[df['K'] < 0]
        zero_strike = df[df['K'] == 0]
        if len(negative_strike) > 0:
            issues.append({'Issue': 'Negative Strike (K)', 'Count': len(negative_strike)})
            print(f"  ⚠️  Negative Strike: {len(negative_strike):,} records")
        if len(zero_strike) > 0:
            issues.append({'Issue': 'Zero Strike (K)', 'Count': len(zero_strike)})
            print(f"  ⚠️  Zero Strike: {len(zero_strike):,} records")
    
    # Time to expiration checks
    if 'Dias4Vencimento' in df.columns:
        negative_days = df[df['Dias4Vencimento'] < 0]
        if len(negative_days) > 0:
            issues.append({'Issue': 'Negative Days to Expiration', 'Count': len(negative_days)})
            print(f"  ⚠️  Negative Days to Expiration: {len(negative_days):,} records")
    
    # Volatility checks
    if 'Vol_imp' in df.columns:
        negative_vol = df[df['Vol_imp'] < 0]
        extreme_vol = df[df['Vol_imp'] > 5.0]  # > 500% volatility seems extreme
        if len(negative_vol) > 0:
            issues.append({'Issue': 'Negative Implied Volatility', 'Count': len(negative_vol)})
            print(f"  ⚠️  Negative Implied Volatility: {len(negative_vol):,} records")
        if len(extreme_vol) > 0:
            issues.append({'Issue': 'Extreme Implied Volatility (>500%)', 'Count': len(extreme_vol)})
            print(f"  ⚠️  Extreme Implied Volatility (>500%): {len(extreme_vol):,} records")
    
    # Greeks checks
    if 'Gama' in df.columns:
        negative_gamma = df[df['Gama'] < 0]
        if len(negative_gamma) > 0:
            issues.append({'Issue': 'Negative Gamma', 'Count': len(negative_gamma)})
            print(f"  ⚠️  Negative Gamma: {len(negative_gamma):,} records")
    
    if 'Vega' in df.columns:
        negative_vega = df[df['Vega'] < 0]
        if len(negative_vega) > 0:
            issues.append({'Issue': 'Negative Vega', 'Count': len(negative_vega)})
            print(f"  ⚠️  Negative Vega: {len(negative_vega):,} records")
    
    if len(issues) == 0:
        print("  ✓  No invalid ranges found")
    
    return issues


def detect_outliers_iqr(df, column, option_type, factor=3.0):
    """Detect outliers using IQR method."""
    if column not in df.columns:
        return []
    
    data = df[column].dropna()
    if len(data) == 0:
        return []
    
    Q1 = data.quantile(0.25)
    Q3 = data.quantile(0.75)
    IQR = Q3 - Q1
    
    if IQR == 0:
        return []
    
    lower_bound = Q1 - factor * IQR
    upper_bound = Q3 + factor * IQR
    
    outliers = df[(df[column] < lower_bound) | (df[column] > upper_bound)]
    
    return outliers


def detect_outliers_zscore(df, column, threshold=4.0):
    """Detect outliers using Z-score method."""
    if column not in df.columns:
        return []
    
    data = df[column].dropna()
    if len(data) == 0:
        return []
    
    z_scores = np.abs(stats.zscore(data))
    outlier_indices = np.where(z_scores > threshold)[0]
    
    if len(outlier_indices) == 0:
        return pd.DataFrame()
    
    return df.iloc[outlier_indices]


def check_outliers(df, option_type):
    """Check for statistical outliers."""
    print(f"\n{'='*80}")
    print(f"OUTLIERS DETECTION - {option_type}")
    print(f"{'='*80}")
    
    numeric_columns = ['Delta', 'BS_Price', 'Bid', 'Ask', 'K', 'Vol_imp', 
                       'Gama', 'Theta', 'Vega', 'Rho', 'Dias4Vencimento']
    
    available_columns = [col for col in numeric_columns if col in df.columns]
    
    outlier_summary = []
    
    for col in available_columns:
        data = df[col].dropna()
        if len(data) < 10:  # Need minimum data points
            continue
        
        # IQR method
        iqr_outliers = detect_outliers_iqr(df, col, option_type, factor=3.0)
        
        # Z-score method
        zscore_outliers = detect_outliers_zscore(df, col, threshold=4.0)
        
        if len(iqr_outliers) > 0 or len(zscore_outliers) > 0:
            iqr_count = len(iqr_outliers)
            zscore_count = len(zscore_outliers)
            
            # Get statistics
            stats_info = {
                'Column': col,
                'IQR_Outliers': iqr_count,
                'ZScore_Outliers': zscore_count,
                'Mean': data.mean(),
                'Median': data.median(),
                'Std': data.std(),
                'Min': data.min(),
                'Max': data.max(),
                'Q1': data.quantile(0.25),
                'Q3': data.quantile(0.75)
            }
            
            outlier_summary.append(stats_info)
            
            print(f"\n  📊 {col}:")
            print(f"     IQR Outliers (3σ): {iqr_count:>8,} ({iqr_count/len(df)*100:.2f}%)")
            print(f"     Z-Score Outliers (4σ): {zscore_count:>8,} ({zscore_count/len(df)*100:.2f}%)")
            print(f"     Mean: {stats_info['Mean']:>12.4f} | Median: {stats_info['Median']:>12.4f}")
            print(f"     Range: [{stats_info['Min']:>12.4f}, {stats_info['Max']:>12.4f}]")
            
            # Show extreme outliers
            if len(iqr_outliers) > 0:
                extreme_low = iqr_outliers[col].nsmallest(5)
                extreme_high = iqr_outliers[col].nlargest(5)
                if len(extreme_low) > 0:
                    print(f"     Extreme Low Values: {extreme_low.values}")
                if len(extreme_high) > 0:
                    print(f"     Extreme High Values: {extreme_high.values}")
    
    return outlier_summary


def check_logical_consistency(df, option_type):
    """Check for logical inconsistencies in the data."""
    print(f"\n{'='*80}")
    print(f"LOGICAL CONSISTENCY CHECK - {option_type}")
    print(f"{'='*80}")
    
    issues = []
    
    # Check if option price makes sense relative to intrinsic value
    if all(col in df.columns for col in ['BS_Price', 'K', 'S']):
        # For calls: intrinsic value = max(0, S - K)
        # For puts: intrinsic value = max(0, K - S)
        # Option price should be >= intrinsic value
        
        # We need underlying price S - this might not be in the dataframe
        # Skip this check if S is not available
        pass
    
    # Check if delta and option type are consistent
    if 'Delta' in df.columns:
        if option_type == 'CALL':
            # Deep ITM calls should have delta close to 1
            # Deep OTM calls should have delta close to 0
            deep_itm = df[(df['Delta'] > 0.95) & (df['BS_Price'].notna())]
            deep_otm = df[(df['Delta'] < 0.05) & (df['BS_Price'].notna())]
            
            # Deep ITM calls should have high prices
            if len(deep_itm) > 0 and 'BS_Price' in deep_itm.columns:
                low_price_itm = deep_itm[deep_itm['BS_Price'] < 0.01]
                if len(low_price_itm) > 0:
                    issues.append({
                        'Issue': 'Deep ITM calls with very low prices',
                        'Count': len(low_price_itm)
                    })
                    print(f"  ⚠️  Deep ITM calls (Delta > 0.95) with very low prices: {len(low_price_itm):,}")
            
            # Deep OTM calls should have low prices
            if len(deep_otm) > 0 and 'BS_Price' in deep_otm.columns:
                high_price_otm = deep_otm[deep_otm['BS_Price'] > 10.0]  # Arbitrary threshold
                if len(high_price_otm) > 0:
                    issues.append({
                        'Issue': 'Deep OTM calls with high prices',
                        'Count': len(high_price_otm)
                    })
                    print(f"  ⚠️  Deep OTM calls (Delta < 0.05) with high prices: {len(high_price_otm):,}")
        
        else:  # PUT
            # Deep ITM puts should have delta close to -1
            # Deep OTM puts should have delta close to 0
            deep_itm = df[(df['Delta'] < -0.95) & (df['BS_Price'].notna())]
            deep_otm = df[(df['Delta'] > -0.05) & (df['BS_Price'].notna())]
            
            if len(deep_itm) > 0 and 'BS_Price' in deep_itm.columns:
                low_price_itm = deep_itm[deep_itm['BS_Price'] < 0.01]
                if len(low_price_itm) > 0:
                    issues.append({
                        'Issue': 'Deep ITM puts with very low prices',
                        'Count': len(low_price_itm)
                    })
                    print(f"  ⚠️  Deep ITM puts (Delta < -0.95) with very low prices: {len(low_price_itm):,}")
            
            if len(deep_otm) > 0 and 'BS_Price' in deep_otm.columns:
                high_price_otm = deep_otm[deep_otm['BS_Price'] > 10.0]
                if len(high_price_otm) > 0:
                    issues.append({
                        'Issue': 'Deep OTM puts with high prices',
                        'Count': len(high_price_otm)
                    })
                    print(f"  ⚠️  Deep OTM puts (Delta > -0.05) with high prices: {len(high_price_otm):,}")
    
    # Check if bid-ask spread is reasonable
    if all(col in df.columns for col in ['Bid', 'Ask', 'BS_Price']):
        df_with_prices = df[df['Bid'].notna() & df['Ask'].notna() & df['BS_Price'].notna()]
        if len(df_with_prices) > 0:
            df_with_prices = df_with_prices.copy()
            df_with_prices['Spread'] = df_with_prices['Ask'] - df_with_prices['Bid']
            df_with_prices['SpreadPct'] = (df_with_prices['Spread'] / df_with_prices['BS_Price']) * 100
            
            # Very wide spreads (>50% of price) might indicate data issues
            wide_spreads = df_with_prices[df_with_prices['SpreadPct'] > 50]
            if len(wide_spreads) > 0:
                issues.append({
                    'Issue': 'Very wide bid-ask spreads (>50% of price)',
                    'Count': len(wide_spreads)
                })
                print(f"  ⚠️  Very wide bid-ask spreads (>50% of price): {len(wide_spreads):,}")
    
    if len(issues) == 0:
        print("  ✓  No logical inconsistencies found")
    
    return issues


def check_duplicates(df, option_type):
    """Check for duplicate records."""
    print(f"\n{'='*80}")
    print(f"DUPLICATE RECORDS CHECK - {option_type}")
    print(f"{'='*80}")
    
    # Check for exact duplicates
    exact_duplicates = df.duplicated()
    exact_dup_count = exact_duplicates.sum()
    
    # Check for duplicates on key fields
    key_fields = ['Ativo', 'Data', 'Tipo', 'K', 'Vencimento']
    available_key_fields = [f for f in key_fields if f in df.columns]
    
    if len(available_key_fields) > 0:
        key_duplicates = df.duplicated(subset=available_key_fields)
        key_dup_count = key_duplicates.sum()
        
        print(f"  Exact duplicates: {exact_dup_count:,}")
        print(f"  Duplicates on key fields {available_key_fields}: {key_dup_count:,}")
        
        return {
            'ExactDuplicates': exact_dup_count,
            'KeyFieldDuplicates': key_dup_count
        }
    
    return {'ExactDuplicates': exact_dup_count}


def generate_summary_report(all_issues, output_path):
    """Generate a summary report of all issues found."""
    report_lines = []
    report_lines.append("=" * 80)
    report_lines.append("DATA QUALITY INSPECTION REPORT - BOVA MONTHLY OPTIONS")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    report_lines.append(f"SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"Total issue categories found: {total_issues}")
    report_lines.append("")
    
    for option_type, issues in all_issues.items():
        if len(issues) > 0:
            report_lines.append(f"\n{option_type} OPTIONS:")
            report_lines.append("-" * 80)
            for issue in issues:
                if isinstance(issue, dict):
                    report_lines.append(f"  - {issue.get('Issue', 'Unknown')}: {issue.get('Count', 0):,} records")
    
    report_text = "\n".join(report_lines)
    Path(output_path).write_text(report_text, encoding='utf-8')
    print(f"\nSummary report saved to: {output_path}")


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Quality Inspection for BOVA Monthly Options')
    parser.add_argument('--db', type=str, default='BOVA_monthly.db', help='Path to database file')
    parser.add_argument('--output-dir', type=str, default='data_quality_output', help='Output directory')
    
    args = parser.parse_args()
    
    db_path = Path(__file__).parent / args.db
    output_dir = Path(__file__).parent / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 80)
    print("DATA QUALITY INSPECTION - BOVA MONTHLY OPTIONS")
    print("=" * 80)
    print(f"Database: {db_path}")
    print(f"Output directory: {output_dir}")
    print("=" * 80)
    
    if not db_path.exists():
        print(f"Error: Database file '{db_path}' not found!")
        sys.exit(1)
    
    conn = sqlite3.connect(db_path)
    
    try:
        all_issues = {}
        
        # Check underlying asset data
        print(f"\n{'#'*80}")
        print(f"ANALYZING UNDERLYING ASSET DATA (BOVA11)")
        print(f"{'#'*80}")
        
        underlying_query = """
            SELECT * FROM options_data
            WHERE Tipo = 'AtivoSubjacente'
            AND Ativo = 'BOVA11'
        """
        underlying_df = pd.read_sql_query(underlying_query, conn)
        print(f"\nLoaded {len(underlying_df):,} underlying asset records")
        
        if len(underlying_df) > 0:
            underlying_issues = check_missing_values(underlying_df, 'Underlying Asset')
            underlying_invalid = check_invalid_ranges(underlying_df, 'Underlying Asset')
            all_issues['Underlying Asset'] = underlying_issues + underlying_invalid
        
        # Check options data
        for option_type in ['CALL', 'PUT']:
            print(f"\n{'#'*80}")
            print(f"ANALYZING {option_type} OPTIONS")
            print(f"{'#'*80}")
            
            # Load data
            query = f"""
                SELECT * FROM options_data
                WHERE Tipo = '{option_type}'
            """
            df = pd.read_sql_query(query, conn)
            print(f"\nLoaded {len(df):,} {option_type} option records")
            
            if len(df) == 0:
                print(f"No {option_type} options found!")
                continue
            
            # Perform checks
            missing_issues = check_missing_values(df, option_type)
            invalid_issues = check_invalid_ranges(df, option_type)
            outlier_summary = check_outliers(df, option_type)
            logical_issues = check_logical_consistency(df, option_type)
            duplicate_info = check_duplicates(df, option_type)
            
            # Save outlier details to CSV
            if outlier_summary:
                outlier_df = pd.DataFrame(outlier_summary)
                outlier_path = output_dir / f'outliers_{option_type.lower()}.csv'
                outlier_df.to_csv(outlier_path, index=False)
                print(f"\nOutlier summary saved to: {outlier_path}")
            
            # Collect all issues
            all_issues[option_type] = missing_issues + invalid_issues + logical_issues
        
        # Generate summary report
        report_path = output_dir / 'data_quality_report.txt'
        generate_summary_report(all_issues, report_path)
        
        print("\n" + "=" * 80)
        print("INSPECTION COMPLETE!")
        print("=" * 80)
        print(f"Results saved to: {output_dir}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

