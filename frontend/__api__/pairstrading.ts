/**
 * Pairs Trading API Service
 * Handles all API calls related to pairs trading, cointegration analysis, and trading signals
 * Provides functions to fetch recent signals, cointegration data, and pair details
 */
import axios from 'axios';
import { apiBaseUrl, defaultHeaders, requestTimeout } from './config';

// Types
export interface PairSignal {
  asset1: string;
  asset2: string;
  signal_type: 'buy' | 'sell';
  signal_date: string;
  beta?: number;
  p_value?: number;
  current_zscore: number;
  half_life?: number;
}

export interface CointegrationPair {
  asset1: string;
  asset2: string;
  cointegrated: boolean;
  p_value?: number;
  t_stat?: number;
  critical_value?: number;
  beta?: number;
  half_life?: number;
}

// Beta and half-life statistics
export interface StatsObject {
  min: number;
  max: number;
  avg: number;
}

export interface SignalsSummary {
  total_signals: number;
  buy_signals: number;
  sell_signals: number;
  beta_stats?: StatsObject;
  half_life_stats?: StatsObject;
}

export interface CointegrationSummary {
  total_pairs: number;
  cointegrated_pairs: number;
  cointegrated_percentage: number;
}

export interface PairsResponse {
  metadata?: {
    filters_applied: Record<string, any>;
  };
  results?: CointegrationPair[];
  cointegration?: {
    results: CointegrationPair[];
    summary: CointegrationSummary;
  };
  signals?: {
    signals: PairSignal[];
    summary: SignalsSummary;
  };
  summary?: SignalsSummary;
}

export interface PairDetailResponse {
  price_series?: {
    dates: string[];
    asset1_prices: number[];
    asset2_prices: number[];
    spread: number[];
    zscore: number[];
  };
  cointegration_analysis?: {
    cointegrated: boolean;
    p_value: number;
    t_stat: number;
    critical_value: number;
    beta: number;
    half_life: number;
  };
  recent_signals?: PairSignal[];
  performance_metrics?: {
    sharpe_ratio: number;
    profit_factor: number;
    win_rate: number;
    max_drawdown: number;
  };
}

// Parameters for pairs trading API calls
export interface PairsTradingParams {
  data_type?: 'signals' | 'cointegration' | 'all' | 'pair_details';
  period?: 'last_6_months' | 'last_12_months';
  asset1?: string;
  asset2?: string;
  signal_type?: 'buy' | 'sell';
  cointegrated_only?: boolean;
  min_zscore?: number;
  max_zscore?: number;
  min_beta?: number;
  max_beta?: number;
  min_half_life?: number;
  max_half_life?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  limit?: number;
}

// API endpoint base URL (from environment variable or default)
const API_BASE_URL = apiBaseUrl;

// Common options for fetch calls
const defaultOptions = {
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Get pairs trading data from the API
 */
export async function getPairsTrading(params: PairsTradingParams): Promise<PairsResponse> {
  // Build query string from params
  const queryParams = new URLSearchParams();
  
  // Add each parameter to the query string if defined
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined) {
      // Handle boolean values specifically
      if (typeof value === 'boolean') {
        queryParams.append(key, value ? 'true' : 'false');
      } else {
        queryParams.append(key, String(value));
      }
    }
  });
  
  const response = await fetch(`${apiBaseUrl}/api/pairs-trading?${queryParams.toString()}`, {
    ...defaultOptions,
    method: 'GET',
  });
  
  if (!response.ok) {
    throw new Error(`Failed to fetch pairs trading data: ${response.statusText}`);
  }
  
  return response.json();
}

/**
 * Get recent trading signals
 */
export async function getRecentSignals(params: Omit<PairsTradingParams, 'data_type' | 'period'>): Promise<PairsResponse> {
  return getPairsTrading({
    data_type: 'signals',
    ...params
  });
}

/**
 * Get cointegration data for pairs
 */
export async function getCointegrationData(params: Omit<PairsTradingParams, 'data_type' | 'signal_type' | 'min_zscore' | 'max_zscore'>): Promise<PairsResponse> {
  return getPairsTrading({
    data_type: 'cointegration',
    cointegrated_only: true, // Default to cointegrated pairs only
    ...params
  });
}

/**
 * Get detailed analysis for a specific pair
 */
export async function getPairDetails(asset1: string, asset2: string, period: string = 'last_6_months'): Promise<PairDetailResponse> {
  const response = await getPairsTrading({
    data_type: 'pair_details',
    asset1,
    asset2,
    period: period as 'last_6_months' | 'last_12_months'
  });
  
  return response as unknown as PairDetailResponse;
}

/**
 * Extract unique symbols from either cointegration results or signals
 */
export function extractUniqueSymbols(data: PairsResponse): string[] {
  const symbols = new Set<string>();
  
  // Extract from cointegration results
  if (data.cointegration?.results) {
    data.cointegration.results.forEach(pair => {
      if (pair.asset1) symbols.add(pair.asset1);
      if (pair.asset2) symbols.add(pair.asset2);
    });
  }
  
  // Extract from signals
  if (data.signals?.signals) {
    data.signals.signals.forEach(signal => {
      if (signal.asset1) symbols.add(signal.asset1);
      if (signal.asset2) symbols.add(signal.asset2);
    });
  }
  
  // Return sorted array of unique symbols
  return Array.from(symbols).sort();
}