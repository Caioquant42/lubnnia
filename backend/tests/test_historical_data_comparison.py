"""
Test suite to compare historical data from yfinance vs OPLAB API.

Verifies that historical stock price data from yfinance matches
data from OPLAB API for the same tickers and date ranges.
"""
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pytest
import pandas as pd
import numpy as np

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yfinance as yf
from oplab import create_client


class TestHistoricalDataComparison:
    """Test historical data comparison between yfinance and OPLAB API."""
    
    @pytest.fixture(scope="class")
    def oplab_client(self):
        """Create OPLAB client instance."""
        import os
        token = os.getenv('OPLAB_ACCESS_TOKEN')
        if not token:
            pytest.skip(
                "OPLAB_ACCESS_TOKEN environment variable not set. "
                "Set it to run these integration tests."
            )
        try:
            return create_client()
        except ValueError as e:
            pytest.skip(f"Failed to create OPLAB client: {e}")
    
    @pytest.fixture(scope="class")
    def test_tickers(self):
        """List of tickers to test."""
        return ['PETR4', 'VALE3', 'BOVA11']
    
    @pytest.fixture(scope="class")
    def date_range(self):
        """Define date range for historical data (last 90 days)."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        return start_date, end_date
    
    def fetch_yfinance_data(
        self, 
        ticker: str, 
        start_date: datetime, 
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch historical data from yfinance.
        
        Args:
            ticker: Stock ticker (e.g., 'PETR4')
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with historical prices
        """
        # yfinance requires .SA suffix for Brazilian stocks
        ticker_with_suffix = f"{ticker}.SA" if not ticker.endswith('.SA') else ticker
        
        ticker_obj = yf.Ticker(ticker_with_suffix)
        hist = ticker_obj.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval='1d'
        )
        
        if hist.empty:
            return pd.DataFrame()
        
        # Return DataFrame with date index and Close column
        df = pd.DataFrame({
            'date': hist.index,
            'close': hist['Close'].values
        })
        df['date'] = pd.to_datetime(df['date']).dt.date
        return df
    
    def fetch_oplab_data(
        self,
        client,
        ticker: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        Fetch historical data from OPLAB API.
        
        Args:
            client: OPLAB client instance
            ticker: Stock ticker (e.g., 'PETR4')
            start_date: Start date
            end_date: End date
            
        Returns:
            DataFrame with historical prices
        """
        from_date_str = start_date.strftime('%Y-%m-%dT00:00:00Z')
        to_date_str = end_date.strftime('%Y-%m-%dT23:59:59Z')
        
        hist_data = client.market.historical.get_historical_data(
            symbol=ticker,
            resolution='1d',
            from_date=from_date_str,
            to_date=to_date_str,
            smooth=True,
            df='timestamp'
        )
        
        if not hist_data or 'data' not in hist_data or not hist_data['data']:
            return pd.DataFrame()
        
        # Extract data and convert to DataFrame
        data_array = hist_data['data']
        records = []
        
        for item in data_array:
            time_val = item.get('time')
            close_val = item.get('close')
            
            if time_val is not None and close_val is not None and close_val > 0:
                # Convert timestamp to date
                if isinstance(time_val, (int, float)):
                    # Unix timestamp in milliseconds or seconds
                    if time_val > 1e10:  # Likely milliseconds
                        dt = datetime.fromtimestamp(time_val / 1000)
                    else:  # Likely seconds
                        dt = datetime.fromtimestamp(time_val)
                else:
                    # Try parsing as string
                    dt = pd.to_datetime(time_val)
                
                records.append({
                    'date': dt.date(),
                    'close': float(close_val)
                })
        
        if not records:
            return pd.DataFrame()
        
        df = pd.DataFrame(records)
        df = df.sort_values('date').reset_index(drop=True)
        return df
    
    def compare_data(
        self,
        df_yfinance: pd.DataFrame,
        df_oplab: pd.DataFrame,
        ticker: str
    ) -> Dict:
        """
        Compare data from yfinance and OPLAB.
        
        Args:
            df_yfinance: DataFrame from yfinance
            df_oplab: DataFrame from OPLAB
            ticker: Stock ticker for reporting
            
        Returns:
            Dictionary with comparison statistics
        """
        if df_yfinance.empty:
            return {
                'ticker': ticker,
                'error': 'No yfinance data',
                'success': False
            }
        
        if df_oplab.empty:
            return {
                'ticker': ticker,
                'error': 'No OPLAB data',
                'success': False
            }
        
        # Merge on date
        merged = pd.merge(
            df_yfinance[['date', 'close']].rename(columns={'close': 'close_yf'}),
            df_oplab[['date', 'close']].rename(columns={'close': 'close_oplab'}),
            on='date',
            how='inner'
        )
        
        if merged.empty:
            return {
                'ticker': ticker,
                'error': 'No overlapping dates',
                'yfinance_dates': len(df_yfinance),
                'oplab_dates': len(df_oplab),
                'success': False
            }
        
        # Calculate differences
        merged['diff'] = merged['close_yf'] - merged['close_oplab']
        merged['diff_pct'] = (merged['diff'] / merged['close_yf']) * 100
        
        # Statistics
        abs_diff = merged['diff'].abs()
        abs_diff_pct = merged['diff_pct'].abs()
        
        stats = {
            'ticker': ticker,
            'total_dates': len(merged),
            'yfinance_dates': len(df_yfinance),
            'oplab_dates': len(df_oplab),
            'mean_close_yf': float(merged['close_yf'].mean()),
            'mean_close_oplab': float(merged['close_oplab'].mean()),
            'mean_diff': float(merged['diff'].mean()),
            'mean_abs_diff': float(abs_diff.mean()),
            'max_abs_diff': float(abs_diff.max()),
            'mean_abs_diff_pct': float(abs_diff_pct.mean()),
            'max_abs_diff_pct': float(abs_diff_pct.max()),
            'std_diff': float(merged['diff'].std()),
            'min_date': merged['date'].min().strftime('%Y-%m-%d'),
            'max_date': merged['date'].max().strftime('%Y-%m-%d'),
            'success': True
        }
        
        return stats
    
    @pytest.mark.slow
    def test_historical_data_petr4(self, oplab_client, test_tickers, date_range):
        """Test historical data comparison for PETR4."""
        ticker = 'PETR4'
        start_date, end_date = date_range
        
        # Fetch data from both sources
        df_yf = self.fetch_yfinance_data(ticker, start_date, end_date)
        df_oplab = self.fetch_oplab_data(oplab_client, ticker, start_date, end_date)
        
        # Compare
        stats = self.compare_data(df_yf, df_oplab, ticker)
        
        # Assertions
        assert stats['success'], f"Failed to compare data: {stats.get('error', 'Unknown error')}"
        assert stats['total_dates'] > 0, f"No overlapping dates found for {ticker}"
        
        # Prices should be within reasonable range (within 5% difference)
        assert stats['mean_abs_diff_pct'] < 5.0, (
            f"Mean absolute difference ({stats['mean_abs_diff_pct']:.2f}%) "
            f"exceeds 5% for {ticker}"
        )
        
        # Maximum difference should not be too large (10% tolerance)
        assert stats['max_abs_diff_pct'] < 10.0, (
            f"Max absolute difference ({stats['max_abs_diff_pct']:.2f}%) "
            f"exceeds 10% for {ticker}"
        )
        
        print(f"\n✓ {ticker} comparison:")
        print(f"  - Overlapping dates: {stats['total_dates']}")
        print(f"  - Mean absolute diff: {stats['mean_abs_diff']:.4f} ({stats['mean_abs_diff_pct']:.2f}%)")
        print(f"  - Max absolute diff: {stats['max_abs_diff']:.4f} ({stats['max_abs_diff_pct']:.2f}%)")
    
    @pytest.mark.slow
    def test_historical_data_vale3(self, oplab_client, test_tickers, date_range):
        """Test historical data comparison for VALE3."""
        ticker = 'VALE3'
        start_date, end_date = date_range
        
        # Fetch data from both sources
        df_yf = self.fetch_yfinance_data(ticker, start_date, end_date)
        df_oplab = self.fetch_oplab_data(oplab_client, ticker, start_date, end_date)
        
        # Compare
        stats = self.compare_data(df_yf, df_oplab, ticker)
        
        # Assertions
        assert stats['success'], f"Failed to compare data: {stats.get('error', 'Unknown error')}"
        assert stats['total_dates'] > 0, f"No overlapping dates found for {ticker}"
        assert stats['mean_abs_diff_pct'] < 5.0, (
            f"Mean absolute difference ({stats['mean_abs_diff_pct']:.2f}%) "
            f"exceeds 5% for {ticker}"
        )
        assert stats['max_abs_diff_pct'] < 10.0, (
            f"Max absolute difference ({stats['max_abs_diff_pct']:.2f}%) "
            f"exceeds 10% for {ticker}"
        )
        
        print(f"\n✓ {ticker} comparison:")
        print(f"  - Overlapping dates: {stats['total_dates']}")
        print(f"  - Mean absolute diff: {stats['mean_abs_diff']:.4f} ({stats['mean_abs_diff_pct']:.2f}%)")
        print(f"  - Max absolute diff: {stats['max_abs_diff']:.4f} ({stats['max_abs_diff_pct']:.2f}%)")
    
    @pytest.mark.slow
    def test_historical_data_bova11(self, oplab_client, test_tickers, date_range):
        """Test historical data comparison for BOVA11."""
        ticker = 'BOVA11'
        start_date, end_date = date_range
        
        # Fetch data from both sources
        df_yf = self.fetch_yfinance_data(ticker, start_date, end_date)
        df_oplab = self.fetch_oplab_data(oplab_client, ticker, start_date, end_date)
        
        # Compare
        stats = self.compare_data(df_yf, df_oplab, ticker)
        
        # Assertions
        assert stats['success'], f"Failed to compare data: {stats.get('error', 'Unknown error')}"
        assert stats['total_dates'] > 0, f"No overlapping dates found for {ticker}"
        assert stats['mean_abs_diff_pct'] < 5.0, (
            f"Mean absolute difference ({stats['mean_abs_diff_pct']:.2f}%) "
            f"exceeds 5% for {ticker}"
        )
        assert stats['max_abs_diff_pct'] < 10.0, (
            f"Max absolute difference ({stats['max_abs_diff_pct']:.2f}%) "
            f"exceeds 10% for {ticker}"
        )
        
        print(f"\n✓ {ticker} comparison:")
        print(f"  - Overlapping dates: {stats['total_dates']}")
        print(f"  - Mean absolute diff: {stats['mean_abs_diff']:.4f} ({stats['mean_abs_diff_pct']:.2f}%)")
        print(f"  - Max absolute diff: {stats['max_abs_diff']:.4f} ({stats['max_abs_diff_pct']:.2f}%)")
    
    @pytest.mark.slow
    def test_all_tickers_comparison(self, oplab_client, test_tickers, date_range):
        """Test and compare all tickers in a single test."""
        start_date, end_date = date_range
        all_stats = []
        
        for ticker in test_tickers:
            try:
                # Fetch data from both sources
                df_yf = self.fetch_yfinance_data(ticker, start_date, end_date)
                df_oplab = self.fetch_oplab_data(oplab_client, ticker, start_date, end_date)
                
                # Compare
                stats = self.compare_data(df_yf, df_oplab, ticker)
                all_stats.append(stats)
                
            except Exception as e:
                pytest.fail(f"Error comparing {ticker}: {str(e)}")
        
        # Summary report
        print("\n" + "="*80)
        print("HISTORICAL DATA COMPARISON SUMMARY")
        print("="*80)
        
        successful = [s for s in all_stats if s.get('success', False)]
        failed = [s for s in all_stats if not s.get('success', False)]
        
        if failed:
            print(f"\n⚠ Failed comparisons: {len(failed)}")
            for stat in failed:
                print(f"  - {stat['ticker']}: {stat.get('error', 'Unknown error')}")
        
        if successful:
            print(f"\n✓ Successful comparisons: {len(successful)}")
            print("\nDetailed Statistics:")
            print("-"*80)
            
            summary_df = pd.DataFrame(successful)
            summary_df = summary_df[[
                'ticker', 'total_dates', 'mean_abs_diff_pct', 
                'max_abs_diff_pct', 'mean_close_yf', 'mean_close_oplab'
            ]]
            
            print(summary_df.to_string(index=False))
            
            # Overall assertions
            assert len(successful) == len(test_tickers), (
                f"Not all tickers were successfully compared. "
                f"Expected {len(test_tickers)}, got {len(successful)}"
            )
            
            # Check that all mean differences are within tolerance
            for stat in successful:
                assert stat['mean_abs_diff_pct'] < 5.0, (
                    f"Mean difference for {stat['ticker']} exceeds 5%"
                )
                assert stat['max_abs_diff_pct'] < 10.0, (
                    f"Max difference for {stat['ticker']} exceeds 10%"
                )
        
        print("="*80)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])

