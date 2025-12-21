#!/usr/bin/env python3
"""
Data Gathering and Asset Selection - Optimized Version

Handles stock data download, preprocessing, and Monte Carlo asset selection.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from collections import Counter
import warnings

warnings.filterwarnings('ignore')

# Set random seeds for reproducibility
np.random.seed(1987)
random.seed(1987)

class DataGatherer:
    """Optimized data gathering and asset selection"""
    
    # IBOVESPA asset universe
    IBOVESPA_ASSETS = [
        'ALOS3.SA', 'ALPA4.SA', 'ABEV3.SA', 'ASAI3.SA', 'AURE3.SA', 'AZUL4.SA', 'AZZA3.SA', 'B3SA3.SA',
        'BBSE3.SA', 'BBDC3.SA', 'BBDC4.SA', 'BRAP4.SA', 'BBAS3.SA', 'BRKM5.SA', 'BRAV3.SA', 'BRFS3.SA',
        'BPAC11.SA', 'CXSE3.SA', 'CRFB3.SA', 'CCRO3.SA', 'CMIG4.SA', 'COGN3.SA', 'CPLE6.SA', 'CSAN3.SA',
        'CPFE3.SA', 'CMIN3.SA', 'CVCB3.SA', 'CYRE3.SA', 'ELET3.SA', 'ELET6.SA', 'EMBR3.SA', 'ENGI11.SA',
        'ENEV3.SA', 'EGIE3.SA', 'EQTL3.SA', 'EZTC3.SA', 'FLRY3.SA', 'GGBR4.SA', 'GOAU4.SA', 'NTCO3.SA',
        'HAPV3.SA', 'HYPE3.SA', 'IGTI11.SA', 'IRBR3.SA', 'ITSA4.SA', 'ITUB4.SA', 'JBSS3.SA', 'KLBN11.SA',
        'RENT3.SA', 'LREN3.SA', 'LWSA3.SA', 'MGLU3.SA', 'MRFG3.SA', 'BEEF3.SA', 'MRVE3.SA', 'MULT3.SA',
        'PCAR3.SA', 'PETR3.SA', 'PETR4.SA', 'RECV3.SA', 'PRIO3.SA', 'PETZ3.SA', 'RADL3.SA', 'RAIZ4.SA',
        'RDOR3.SA', 'RAIL3.SA', 'SBSP3.SA', 'SANB11.SA', 'STBP3.SA', 'SMTO3.SA', 'CSNA3.SA', 'SLCE3.SA',
        'SUZB3.SA', 'TAEE11.SA', 'VIVT3.SA', 'TIMS3.SA', 'TOTS3.SA', 'TRPL4.SA', 'UGPA3.SA', 'USIM5.SA',
        'VALE3.SA', 'VAMO3.SA', 'VBBR3.SA', 'VIVA3.SA', 'WEGE3.SA', 'YDUQ3.SA'
    ]
    
    def __init__(self, use_monte_carlo_selection=True, top_n_assets=15):
        self.use_monte_carlo_selection = use_monte_carlo_selection
        self.top_n_assets = top_n_assets
        
        if use_monte_carlo_selection:
            print(f"🎯 Monte Carlo Asset Selection (Top {top_n_assets})")
            self.asset_list = self._select_assets_with_monte_carlo()
        else:
            self.asset_list = self.IBOVESPA_ASSETS
    
    def _select_assets_with_monte_carlo(self):
        """Select top assets using Monte Carlo simulation"""
        print("📊 Running Monte Carlo asset selection...")
        
        # Get data for Monte Carlo analysis
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        data = self.get_data(asset_list=self.IBOVESPA_ASSETS, start_date=start_date)
        
        if data.empty:
            print("❌ No data available for Monte Carlo analysis")
            return self.IBOVESPA_ASSETS[:self.top_n_assets]
        
        # Run Monte Carlo simulation
        asset_frequency = self._run_monte_carlo_simulation(data)
        
        # Select top assets
        top_assets = list(asset_frequency.keys())[:self.top_n_assets]
        print(f"✅ Selected top {len(top_assets)} assets")
        
        return top_assets
    
    def _run_monte_carlo_simulation(self, data, n_simulations=2000, portfolio_size=5, return_period=5):
        """Run Monte Carlo simulation to rank assets"""
        df = data.copy()
        
        # Create synthetic benchmark if needed
        benchmark_cols = [col for col in df.columns if any(x in col for x in ['BOVA', 'WIN', 'IND'])]
        if not benchmark_cols:
            df['BOVA11'] = df.mean(axis=1)
            benchmark_cols = ['BOVA11']
        
        benchmark = df[benchmark_cols[0]].copy()
        benchmark = benchmark / benchmark.iloc[0]
        
        # Remove benchmark from asset universe
        df = df.drop(columns=benchmark_cols)
        
        print(f"🎲 Monte Carlo: {len(df.columns)} assets, {n_simulations} simulations")
        
        # Calculate returns
        returns = df.pct_change(return_period)
        cumulative_returns = (1 + returns).cumprod()
        cumulative_returns.iloc[0] = 1
        
        # Monte Carlo simulation
        outperforming_portfolios = []
        progress_step = max(1, n_simulations // 10)
        
        for i in range(n_simulations):
            if (i + 1) % progress_step == 0:
                print(f"   Progress: {(i+1)/n_simulations*100:.0f}%")
            
            try:
                # Random portfolio
                portfolio = random.sample(list(df.columns), k=portfolio_size)
                portfolio_returns = 10000 * cumulative_returns.loc[:, portfolio]
                final_value = portfolio_returns.sum(axis=1).iloc[-1]
                
                # Check if outperforms benchmark
                benchmark_return = benchmark.iloc[-1] * 10000 * portfolio_size
                if final_value > benchmark_return:
                    outperforming_portfolios.append(portfolio)
            except (ValueError, IndexError):
                continue
        
        # Calculate asset frequency
        all_assets = [asset for portfolio in outperforming_portfolios for asset in portfolio]
        asset_frequency = dict(sorted(Counter(all_assets).items(), key=lambda x: x[1], reverse=True))
        
        print(f"📈 Results: {len(outperforming_portfolios)} portfolios outperformed benchmark")
        print(f"   Outperformance rate: {len(outperforming_portfolios)/n_simulations*100:.1f}%")
        
        return asset_frequency
    
    def get_data(self, asset_list=None, period='64d', interval='1d', 
                 data_type='Close', start_date=None, end_date=None):
        """Download and process stock data"""
        if asset_list is None:
            asset_list = self.asset_list
        
        print(f"📥 Downloading data for {len(asset_list)} assets...")
        
        # Prepare date range
        if start_date and end_date:
            period = None
        elif start_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
            period = None
        elif end_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
            period = None
        
        # Download data
        data = {}
        failed_assets = []
        
        for asset in asset_list:
            try:
                ticker = yf.Ticker(asset)
                if period:
                    hist = ticker.history(period=period, interval=interval)
                else:
                    hist = ticker.history(start=start_date, end=end_date, interval=interval)
                
                if not hist.empty:
                    data[asset] = hist[data_type]
                else:
                    failed_assets.append(asset)
            except Exception as e:
                failed_assets.append(asset)
                continue
        
        if failed_assets:
            print(f"⚠️  Failed to download {len(failed_assets)} assets: {failed_assets[:5]}...")
        
        if not data:
            print("❌ No data downloaded")
            return pd.DataFrame()
        
        # Create DataFrame and clean
        df = pd.DataFrame(data)
        df = df.dropna()
        
        print(f"✅ Successfully downloaded data for {len(df.columns)} assets")
        print(f"   Date range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
        print(f"   Observations: {len(df)}")
        
        return df
    
    def get_current_prices(self, asset_list=None):
        """Get current prices for assets"""
        if asset_list is None:
            asset_list = self.asset_list
        
        current_prices = {}
        failed_assets = []
        
        for asset in asset_list:
            try:
                ticker = yf.Ticker(asset)
                hist = ticker.history(period='1d')
                if not hist.empty:
                    current_prices[asset] = hist['Close'].iloc[-1]
                else:
                    failed_assets.append(asset)
            except Exception as e:
                failed_assets.append(asset)
                continue
        
        if failed_assets:
            print(f"⚠️  Failed to get current prices for {len(failed_assets)} assets: {failed_assets[:5]}...")
        
        print(f"✅ Got current prices for {len(current_prices)} assets")
        return current_prices
    
    def save_data(self, asset_list=None, period='64d', output_dir='.'):
        """Save data to CSV files"""
        if asset_list is None:
            asset_list = self.asset_list
        
        # Get data
        closing_prices = self.get_data(asset_list=asset_list, period=period)
        if closing_prices.empty:
            print("❌ No data to save")
            return
        
        # Calculate log returns
        log_returns = closing_prices.pct_change().dropna()
        
        # Save files
        closing_prices.to_csv(f'{output_dir}/closing_prices.csv')
        log_returns.to_csv(f'{output_dir}/log_returns.csv')
        
        print(f"💾 Data saved to {output_dir}/")
        print(f"   closing_prices.csv: {closing_prices.shape}")
        print(f"   log_returns.csv: {log_returns.shape}")

def main():
    """Test data gathering functionality"""
    gatherer = DataGatherer(use_monte_carlo_selection=True, top_n_assets=10)
    
    print("\n📊 Testing data download...")
    data = gatherer.get_data()
    
    if not data.empty:
        print(f"✅ Data download successful: {data.shape}")
        gatherer.save_data()
    else:
        print("❌ Data download failed")

if __name__ == "__main__":
    main() 