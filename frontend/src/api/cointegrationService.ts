import { apiBaseUrl, defaultHeaders, requestTimeout } from './config';
import axios from 'axios';

export interface CointegrationItem {
  asset1: string;
  asset2: string;
  cointegrated: boolean;
  p_value?: number;
  t_stat?: number;
  critical_value?: number;
  beta?: number;
  half_life?: number;
}

export interface PeriodData {
  pairs: CointegrationItem[];
  summary: {
    total_pairs: number;
    cointegrated_pairs: number;
    cointegrated_percentage: number;
    beta?: {
      min: number;
      max: number;
      avg: number;
    };
    half_life?: {
      min: number;
      max: number;
      avg: number;
    };
    [key: string]: any;
  };
}

export interface CointegrationData {
  last_6_months?: PeriodData;
  last_12_months?: PeriodData;
  [key: string]: PeriodData | undefined;
}

/**
 * Fetches cointegration data for stocks
 * @param period Data period (e.g., 'last_6_months', 'last_12_months')
 * @returns Promise with cointegration data
 */
export async function fetchStockCointegration(
  period: 'last_6_months' | 'last_12_months' = 'last_6_months'
): Promise<CointegrationData> {
  try {
    const response = await axios.get(`${apiBaseUrl}/pairstrading/cointegration/stocks`, {
      params: { period },
      headers: defaultHeaders,
      timeout: requestTimeout
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching stock cointegration data:', error);
    throw error;
  }
}

/**
 * Fetches cointegration data for currencies
 * @param period Data period (e.g., 'last_6_months', 'last_12_months')
 * @returns Promise with cointegration data
 */
export async function fetchCurrencyCointegration(
  period: 'last_6_months' | 'last_12_months' = 'last_6_months'
): Promise<CointegrationData> {
  try {
    const response = await axios.get(`${apiBaseUrl}/pairstrading/cointegration/currencies`, {
      params: { period },
      headers: defaultHeaders,
      timeout: requestTimeout
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching currency cointegration data:', error);
    throw error;
  }
}
