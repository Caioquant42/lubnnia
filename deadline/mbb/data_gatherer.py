"""
Data Gathering Module for Moving Block Bootstrap

Handles Brazilian stock data download, preprocessing, and Monte Carlo asset selection.
Automatically appends .SA suffix for Brazilian tickers.
"""

import yfinance as yf
import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from collections import Counter
import warnings
import logging

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class DataGatherer:
    """Brazilian stock data gathering and asset selection"""
    
    # IBOVESPA asset universe
    IBOVESPA_ASSETS = [
        'ALOS3', 'ALPA4', 'ABEV3', 'ASAI3', 'AURE3', 'AZUL4', 'AZZA3', 'B3SA3',
        'BBSE3', 'BBDC3', 'BBDC4', 'BRAP4', 'BBAS3', 'BRKM5', 'BRAV3', 'BRFS3',
        'BPAC11', 'CXSE3', 'CRFB3', 'CCRO3', 'CMIG4', 'COGN3', 'CPLE6', 'CSAN3',
        'CPFE3', 'CMIN3', 'CVCB3', 'CYRE3', 'ELET3', 'ELET6', 'EMBR3', 'ENGI11',
        'ENEV3', 'EGIE3', 'EQTL3', 'EZTC3', 'FLRY3', 'GGBR4', 'GOAU4', 'NTCO3',
        'HAPV3', 'HYPE3', 'IGTI11', 'IRBR3', 'ITSA4', 'ITUB4', 'JBSS3', 'KLBN11',
        'RENT3', 'LREN3', 'LWSA3', 'MGLU3', 'MRFG3', 'BEEF3', 'MRVE3', 'MULT3',
        'PCAR3', 'PETR3', 'PETR4', 'RECV3', 'PRIO3', 'PETZ3', 'RADL3', 'RAIZ4',
        'RDOR3', 'RAIL3', 'SBSP3', 'SANB11', 'STBP3', 'SMTO3', 'CSNA3', 'SLCE3',
        'SUZB3', 'TAEE11', 'VIVT3', 'TIMS3', 'TOTS3', 'TRPL4', 'UGPA3', 'USIM5',
        'VALE3', 'VAMO3', 'VBBR3', 'VIVA3', 'WEGE3', 'YDUQ3'
    ]
    
    def __init__(self, use_monte_carlo_selection=True, top_n_assets=15, seed=1987):
        """
        Initialize Data Gatherer
        
        Parameters:
        -----------
        use_monte_carlo_selection : bool
            Use Monte Carlo to select top assets
        top_n_assets : int
            Number of top assets to select
        seed : int
            Random seed for reproducibility
        """
        self.use_monte_carlo_selection = use_monte_carlo_selection
        self.top_n_assets = top_n_assets
        self.seed = seed
        
        # Set random seeds
        np.random.seed(seed)
        random.seed(seed)
        
        if use_monte_carlo_selection:
            logger.info(f"Monte Carlo Asset Selection (Top {top_n_assets})")
            self.asset_list = self._select_assets_with_monte_carlo()
        else:
            self.asset_list = self._add_sa_suffix(self.IBOVESPA_ASSETS)
    
    def _add_sa_suffix(self, tickers):
        """Add .SA suffix to Brazilian tickers if not present"""
        return [ticker if ticker.endswith('.SA') else f"{ticker}.SA" for ticker in tickers]
    
    def _remove_sa_suffix(self, tickers):
        """Remove .SA suffix from tickers"""
        return [ticker.replace('.SA', '') for ticker in tickers]
    
    def _select_assets_with_monte_carlo(self):
        """Select top assets using Monte Carlo simulation"""
        logger.info("Running Monte Carlo asset selection...")
        
        # Get data for Monte Carlo analysis (1 year)
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
        tickers_with_suffix = self._add_sa_suffix(self.IBOVESPA_ASSETS)
        data = self.get_data(
            asset_list=tickers_with_suffix,
            start_date=start_date
        )
        
        if data.empty:
            logger.warning("No data available for Monte Carlo analysis, using default list")
            return self._add_sa_suffix(self.IBOVESPA_ASSETS[:self.top_n_assets])
        
        # Run Monte Carlo simulation
        asset_frequency = self._run_monte_carlo_simulation(data)
        
        # Select top assets (already have .SA suffix)
        top_assets = list(asset_frequency.keys())[:self.top_n_assets]
        logger.info(f"Selected top {len(top_assets)} assets: {top_assets}")
        
        return top_assets
    
    def _run_monte_carlo_simulation(self, data, n_simulations=2000, 
                                   portfolio_size=5, return_period=5):
        """
        Run Monte Carlo simulation to rank assets
        
        Parameters:
        -----------
        data : pd.DataFrame
            Price data for assets
        n_simulations : int
            Number of portfolios to simulate
        portfolio_size : int
            Number of assets per portfolio
        return_period : int
            Period for return calculation
            
        Returns:
        --------
        dict
            Asset frequency ranking (ticker: count)
        """
        df = data.copy()
        
        # Create synthetic benchmark if needed
        benchmark_cols = [col for col in df.columns if any(x in col for x in ['BOVA', 'WIN', 'IND'])]
        if not benchmark_cols:
            df['BOVA11.SA'] = df.mean(axis=1)
            benchmark_cols = ['BOVA11.SA']
        
        benchmark = df[benchmark_cols[0]].copy()
        benchmark = benchmark / benchmark.iloc[0]
        
        # Remove benchmark from asset universe
        df = df.drop(columns=benchmark_cols)
        
        logger.info(f"Monte Carlo: {len(df.columns)} assets, {n_simulations} simulations")
        
        # Calculate returns
        returns = df.pct_change(return_period)
        cumulative_returns = (1 + returns).cumprod()
        cumulative_returns.iloc[0] = 1
        
        # Monte Carlo simulation
        outperforming_portfolios = []
        
        for i in range(n_simulations):
            if (i + 1) % 500 == 0:
                logger.info(f"Progress: {(i+1)/n_simulations*100:.0f}%")
            
            try:
                # Random portfolio
                portfolio = random.sample(list(df.columns), k=min(portfolio_size, len(df.columns)))
                portfolio_returns = 10000 * cumulative_returns.loc[:, portfolio]
                final_value = portfolio_returns.sum(axis=1).iloc[-1]
                
                # Check if outperforms benchmark
                benchmark_return = benchmark.iloc[-1] * 10000 * len(portfolio)
                if final_value > benchmark_return:
                    outperforming_portfolios.append(portfolio)
            except (ValueError, IndexError) as e:
                logger.debug(f"Simulation {i} failed: {e}")
                continue
        
        # Calculate asset frequency
        all_assets = [asset for portfolio in outperforming_portfolios for asset in portfolio]
        asset_frequency = dict(sorted(
            Counter(all_assets).items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
        logger.info(
            f"Results: {len(outperforming_portfolios)} portfolios outperformed benchmark "
            f"({len(outperforming_portfolios)/n_simulations*100:.1f}%)"
        )
        
        return asset_frequency
    
    def get_data(self, asset_list=None, period='64d', interval='1d',
                data_type='Close', start_date=None, end_date=None):
        """
        Download and process stock data
        
        Parameters:
        -----------
        asset_list : list, optional
            List of tickers (will auto-add .SA suffix)
        period : str
            Period for data download
        interval : str
            Data interval
        data_type : str
            Type of data to retrieve (Close, Open, etc.)
        start_date : str, optional
            Start date in YYYY-MM-DD format
        end_date : str, optional
            End date in YYYY-MM-DD format
            
        Returns:
        --------
        pd.DataFrame
            Stock price data
        """
        if asset_list is None:
            asset_list = self.asset_list
        else:
            asset_list = self._add_sa_suffix(asset_list)
        
        logger.info(f"Downloading data for {len(asset_list)} assets...")
        
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
                
                if not hist.empty and data_type in hist.columns:
                    data[asset] = hist[data_type]
                else:
                    failed_assets.append(asset)
            except Exception as e:
                logger.debug(f"Failed to download {asset}: {e}")
                failed_assets.append(asset)
                continue
        
        if failed_assets:
            logger.warning(f"Failed to download {len(failed_assets)} assets")
        
        if not data:
            logger.error("No data downloaded")
            return pd.DataFrame()
        
        # Create DataFrame and clean
        df = pd.DataFrame(data)
        df = df.dropna()
        
        logger.info(
            f"Successfully downloaded data for {len(df.columns)} assets "
            f"({df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}, "
            f"{len(df)} observations)"
        )
        
        return df
    
    def get_current_prices(self, asset_list=None):
        """
        Get current prices for assets
        
        Parameters:
        -----------
        asset_list : list, optional
            List of tickers (will auto-add .SA suffix)
            
        Returns:
        --------
        dict
            Current prices {ticker: price}
        """
        if asset_list is None:
            asset_list = self.asset_list
        else:
            asset_list = self._add_sa_suffix(asset_list)
        
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
                logger.debug(f"Failed to get price for {asset}: {e}")
                failed_assets.append(asset)
                continue
        
        if failed_assets:
            logger.warning(f"Failed to get current prices for {len(failed_assets)} assets")
        
        logger.info(f"Got current prices for {len(current_prices)} assets")
        return current_prices
    
    def get_options_chain(self, ticker):
        """
        Get options chain for a ticker
        
        Parameters:
        -----------
        ticker : str
            Stock ticker (will auto-add .SA suffix)
            
        Returns:
        --------
        dict
            Options chain data {expiration: {calls: df, puts: df}}
        """
        ticker = ticker if ticker.endswith('.SA') else f"{ticker}.SA"
        
        try:
            stock = yf.Ticker(ticker)
            expirations = stock.options
            
            if not expirations:
                logger.warning(f"No options available for {ticker}")
                return {}
            
            options_chain = {}
            for expiration in expirations:
                opt = stock.option_chain(expiration)
                options_chain[expiration] = {
                    'calls': opt.calls,
                    'puts': opt.puts
                }
            
            logger.info(f"Retrieved options chain for {ticker}: {len(expirations)} expirations")
            return options_chain
            
        except Exception as e:
            logger.error(f"Failed to get options chain for {ticker}: {e}")
            return {}

