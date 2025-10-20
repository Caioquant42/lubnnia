/**
 * Collar Strategy API Service
 * Handles API calls for options collar strategy analysis
 * Fetches available strikes, calculates collar combinations, and manages strategy data
 */
import axios from 'axios';
import { apiBaseUrl, defaultHeaders, requestTimeout } from './config';

// Define interfaces for collar data
export interface OptionData {
  symbol: string;
  name?: string;
  open?: number;
  high?: number;
  low?: number;
  close: number;
  volume?: number;
  financial_volume?: number;
  bid?: number;
  ask?: number;
  category?: string;
  due_date: string;
  maturity_type?: 'AMERICAN' | 'EUROPEAN';
  strike: number;
  variation?: number;
  spot_price: number;
  market_maker?: boolean;
  block_date?: string;
  days_to_maturity: number;
  bid_volume?: number;
  ask_volume?: number;
  time?: number;
  type: 'CALL' | 'PUT';
  moneyness: 'ITM' | 'OTM' | 'ATM';
  intrinsic_value?: number;
  extrinsic_value?: number;
}

export interface StrategyData {
  parent_symbol: string;
  days_to_maturity: number;
  maturity_type?: 'AMERICAN' | 'EUROPEAN';
  gain_to_risk_ratio?: number;
  combined_score?: number;
  intrinsic_protection?: boolean;
  zero_risk?: boolean;
  pm_result?: number;
  cdi_relative_return?: number;
  call_symbol: string;
  put_symbol: string;
  call_strike: number;
  put_strike: number;
  total_gain: number;
  total_risk: number;
}

export interface CollarStrategy {
  call: OptionData;
  put: OptionData;
  strategy: StrategyData;
}

export interface CollarApiResponse {
  metadata: {
    total_count: number;
    symbol_count: number;
    unique_symbols: string[];
    category_counts: Record<string, number>;
    maturity_range_counts: Record<string, number>;
  };
  results: {
    intrinsic?: {
      less_than_14_days?: CollarStrategy[]; 
      between_15_and_30_days?: CollarStrategy[];
      between_30_and_60_days?: CollarStrategy[];
      more_than_60_days?: CollarStrategy[];
    };
    otm?: {
      less_than_14_days?: CollarStrategy[];
      between_15_and_30_days?: CollarStrategy[];
      between_30_and_60_days?: CollarStrategy[];
      more_than_60_days?: CollarStrategy[];
    };
  };
}

interface CollarStrategyData {
  call: any;
  put: any;
  strategy: {
    parent_symbol: string;
    days_to_maturity: number;
    maturity_type: string;
    gain_to_risk_ratio: number;
    combined_score: number;
    intrinsic_protection: boolean;
    zero_risk: boolean;
    pm_result: number;
    cdi_relative_return: number;
    call_symbol: string;
    put_symbol: string;
    call_strike: number;
    put_strike: number;
    total_gain: number;
    total_risk: number;
  };
}

/**
 * Fetches collar strategy data from the API
 */
export async function getCollarData(
  params?: {
    category?: string;
    maturity_range?: string;
    symbol?: string;
    min_gain_to_risk?: number;
    sort_by?: string;
    sort_order?: 'asc' | 'desc';
    limit?: number;
  }
) {
  try {
    // Changed from ${apiBaseUrl}/collar to ${apiBaseUrl}/api/collar to match the backend route
    const response = await axios.get(`${apiBaseUrl}/api/collar`, {
      headers: defaultHeaders,
      timeout: requestTimeout,
      params
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching collar data:', error);
    throw error;
  }
}

/**
 * Generates payoff data for the collar strategy visualization
 */
export function generateCollarPayoffData(strategy: CollarStrategy | CollarStrategyData) {
  // Extract relevant data
  const callStrike = strategy.strategy.call_strike;
  const putStrike = strategy.strategy.put_strike;
  const callPrice = strategy.call.close;
  const putPrice = strategy.put.close;
  const spotPrice = strategy.call.spot_price;
  
  // Calculate the range for the chart (20% below and above the current spot price)
  const minPrice = Math.min(putStrike, spotPrice) * 0.8;
  const maxPrice = Math.max(callStrike, spotPrice) * 1.2;
  
  // Generate 50 price points within the range
  const priceStep = (maxPrice - minPrice) / 50;
  const pricePoints = [];
  
  for (let i = 0; i <= 50; i++) {
    const price = minPrice + i * priceStep;
    pricePoints.push(price);
  }
  
  // Calculate payoffs at each price point
  return pricePoints.map(price => {
    // Calculate call payoff (sold call)
    const callPayoff = price > callStrike 
      ? callStrike - price + callPrice 
      : callPrice;
    
    // Calculate put payoff (bought put)
    const putPayoff = price < putStrike 
      ? putStrike - price - putPrice 
      : -putPrice;
    
    // Collar payoff = underlying + short call + long put
    const collarPayoff = (price - spotPrice) + callPayoff + putPayoff;
    
    return {
      price,
      payoff: collarPayoff
    };
  });
}

// Export generatePayoffData as an alias for generateCollarPayoffData for backward compatibility
export const generatePayoffData = generateCollarPayoffData;

/**
 * Gets detailed collar strategy information by symbols
 */
export async function getCollarDetailBySymbols(
  callSymbol: string,
  putSymbol: string
) {
  try {
    // Changed from ${apiBaseUrl}/collar/detail to ${apiBaseUrl}/api/collar/detail to match the backend route
    const response = await axios.get(`${apiBaseUrl}/api/collar/detail`, {
      headers: defaultHeaders,
      timeout: requestTimeout,
      params: {
        call_symbol: callSymbol,
        put_symbol: putSymbol
      }
    });
    
    return response.data;
  } catch (error) {
    console.error('Error fetching collar strategy details:', error);
    throw error;
  }
}