// Asset Interface - Represents a financial instrument
export interface Asset {
  id: string;
  symbol: string;
  name: string;
  type: 'stock' | 'etf' | 'future' | 'option' | 'forex' | 'crypto';
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap?: number;
  high52Week?: number;
  low52Week?: number;
  beta?: number;
  lastUpdated: Date;
}

// Portfolio Position Interface
export interface PortfolioPosition {
  id: string;
  assetId: string;
  symbol: string;
  name: string;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  value: number;
  pnl: number;
  pnlPercent: number;
  allocation: number; // Percentage of portfolio
  costBasis: number;
}

// Portfolio Interface
export interface Portfolio {
  id: string;
  name: string;
  totalValue: number;
  cashBalance: number;
  pnlToday: number;
  pnlTodayPercent: number;
  positions: PortfolioPosition[];
}

// Watchlist Interface
export interface Watchlist {
  id: string;
  name: string;
  assets: Asset[];
}

// Market Data Interface
export interface MarketData {
  id: string;
  type: 'index' | 'sector' | 'commodity' | 'forex' | 'rate';
  name: string;
  value: number;
  change: number;
  changePercent: number;
  lastUpdated: Date;
}

// User Interface
export interface User {
  id: string;
  name: string;
  email: string;
  avatar?: string;
}

// Trade Interface
export interface Trade {
  id: string;
  assetId: string;
  symbol: string;
  type: 'buy' | 'sell';
  quantity: number;
  price: number;
  timestamp: Date;
  value: number;
  fees?: number;
}

// Chart Data Point Interface
export interface ChartDataPoint {
  timestamp: number; // Unix timestamp
  value: number;
}

// Chart Data Series Interface
export interface ChartDataSeries {
  name: string;
  data: ChartDataPoint[];
  color?: string;
}

// Chart Time Period Type
export type ChartTimePeriod = '1D' | '1W' | '1M' | '3M' | '6M' | 'YTD' | '1Y' | '5Y' | 'MAX';

// Notification Interface
export interface Notification {
  id: string;
  type: 'alert' | 'info' | 'warning' | 'success' | 'error';
  title: string;
  message: string;
  read: boolean;
  timestamp: Date;
}

// Market Sector Interface
export interface MarketSector {
  id: string;
  name: string;
  change: number;
  changePercent: number;
}