import { apiBaseUrl } from './config';

// Types
export interface TradingSignal {
  asset1: string;
  asset2: string;
  beta: number;
  current_zscore: number;
  p_value: number;
  signal_date: string;
  signal_type: 'buy' | 'sell';
}

export interface PairData {
  asset1: string;
  asset2: string;
  beta: number;
  p_value: number;
  dates: string[];
  spread: number[];
  zscore: number[];
  signals: {
    buy_signals: { dates: string[]; indices: number[]; zscores: number[] };
    sell_signals: { dates: string[]; indices: number[]; zscores: number[] };
    close_signals: { dates: string[]; indices: number[]; zscores: number[] };
  };
}

export interface SignalsSummary {
  total_signals: number;
  buy_signals: number;
  sell_signals: number;
  data_period: string;
  signal_period: string;
  generated_at: string;
}

export interface RecentSignalsResponse {
  last_5_days_signals: TradingSignal[];
  pairs_data: {
    [key: string]: PairData;
  };
  summary: SignalsSummary;
}

// Use apiBaseUrl from config
const API_BASE_URL = apiBaseUrl;

// Common options for fetch calls
const defaultOptions = {
  headers: {
    'Content-Type': 'application/json',
  },
};

/**
 * Fetch recent trading signals from the API
 */
export async function fetchRecentTradingSignals(): Promise<RecentSignalsResponse> {
  const response = await fetch(
    `${apiBaseUrl}/api/pairs-trading/recent-signals`,
    {
      ...defaultOptions,
      method: 'GET',
    }
  );

  if (!response.ok) {
    throw new Error(
      `Failed to fetch recent trading signals: ${response.statusText}`
    );
  }

  return response.json();
}
