import axios from 'axios';
import { apiBaseUrl, defaultHeaders, requestTimeout } from './config';

// Define interfaces for crypto collar data
export interface CryptoOptionData {
  symbol: string;
  underlying: string;
  strike: number;
  expiry_date: string;
  days_to_expiry: number;
  type: 'CALL' | 'PUT';
  mark_price: number;
  bid?: number;
  ask?: number;
  last_price?: number;
  volume?: number;
  delta?: number;
  gamma?: number;
  vega?: number;
  theta?: number;
  iv?: number;
}

export interface CryptoStrategyData {
  underlying: string;
  spot_price: number;
  days_to_maturity: number;
  call_symbol: string;
  put_symbol: string;
  call_strike: number;
  put_strike: number;
  call_price: number;
  put_price: number;
  net_premium: number;
  max_gain: number;
  max_risk: number;
  gain_to_risk_ratio: number;
  combined_score: number;
  intrinsic_protection: boolean;
  zero_risk: boolean;
  // Intrinsic/extrinsic values
  call_intrinsic_value?: number;
  put_intrinsic_value?: number;
  call_extrinsic_value?: number;
  put_extrinsic_value?: number;
  call_protection?: number;
  put_protection?: number;
  // Greeks
  call_delta?: number;
  put_delta?: number;
  call_gamma?: number;
  put_gamma?: number;
  call_vega?: number;
  put_vega?: number;
  call_theta?: number;
  put_theta?: number;
  // Payoff function
  payoff_function?: {
    price_points: number[];
    pnl_points: number[];
    breakeven_points: number[];
    max_profit: number;
    max_loss: number;
    profit_range: {
      start: number;
      end: number;
    };
  };
}

export interface CryptoCollarStrategy {
  call: CryptoOptionData;
  put: CryptoOptionData;
  strategy: CryptoStrategyData;
}

export interface CryptoCollarApiResponse {
  metadata: {
    total_count: number;
    underlying: string;
    exchange: string;
    spot_price: number;
    timestamp: string;
  };
  results: {
    intrinsic?: {
      less_than_14_days?: CryptoCollarStrategy[];
      between_15_and_30_days?: CryptoCollarStrategy[];
      between_30_and_60_days?: CryptoCollarStrategy[];
      more_than_60_days?: CryptoCollarStrategy[];
    };
    otm?: {
      less_than_14_days?: CryptoCollarStrategy[];
      between_15_and_30_days?: CryptoCollarStrategy[];
      between_30_and_60_days?: CryptoCollarStrategy[];
      more_than_60_days?: CryptoCollarStrategy[];
    };
  };
}

/**
 * Fetches crypto collar strategy data from the API
 */
export async function getCryptoCollarData(
  params?: {
    underlying?: string;
    exchange?: 'bybit';
    min_days?: number;
    max_days?: number;
    min_gain_to_risk?: number;
  }
) {
  try {
    const response = await axios.get<CryptoCollarApiResponse>(
      `${apiBaseUrl}/api/crypto-collar`,
      {
        headers: defaultHeaders,
        timeout: requestTimeout,
        params
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Error fetching crypto collar data:', error);
    throw error;
  }
}

/**
 * Generates optimized payoff data for crypto collar strategy visualization
 * with adaptive step sizing based on price range
 */
export function generateCryptoCollarPayoffData(strategy: CryptoCollarStrategy) {
  const { call, put, strategy: strategyData } = strategy;
  const callStrike = call.strike;
  const putStrike = put.strike;
  const callPrice = call.mark_price;
  const putPrice = put.mark_price;
  const spotPrice = strategyData.spot_price;
  
  // Calculate adaptive step size based on price range for better performance
  const priceRange = Math.max(callStrike, spotPrice) - Math.min(putStrike, spotPrice);
  let step = 1; // Default $1 step for crypto (larger values)
  
  if (priceRange > 20000) {
    step = 100; // $100 steps for very large ranges (BTC)
  } else if (priceRange > 10000) {
    step = 50; // $50 steps for large ranges
  } else if (priceRange > 5000) {
    step = 25; // $25 steps for medium ranges
  } else if (priceRange > 1000) {
    step = 10; // $10 steps for smaller ranges
  } else {
    step = 5; // $5 steps for very small ranges (altcoins)
  }
  
  // Generate optimized data points with calculated step size
  const minX = Math.min(putStrike * 0.90, spotPrice * 0.80);  // Lower buffer (crypto needs more range)
  const maxX = Math.max(callStrike * 1.10, spotPrice * 1.20); // Upper buffer
  
  const detailedPoints = [];
  for (let price = minX; price <= maxX; price += step) {
    // Round to 2 decimal places to avoid floating point issues
    const roundedPrice = Math.round(price * 100) / 100;
    
    // Call payoff (sold call)
    const callPayoff = roundedPrice > callStrike 
      ? callStrike - roundedPrice + callPrice
      : callPrice;
    
    // Put payoff (bought put)
    const putPayoff = roundedPrice < putStrike 
      ? putStrike - roundedPrice - putPrice
      : -putPrice;
    
    // Total collar payoff = underlying + short call + long put
    const collarPayoff = (roundedPrice - spotPrice) + callPayoff + putPayoff;
    
    detailedPoints.push({
      price: roundedPrice,
      payoff: collarPayoff,
      negativePayoff: collarPayoff < 0 ? collarPayoff : null, // For dual-color visualization
      callPayoff,
      putPayoff,
      underlyingPayoff: roundedPrice - spotPrice
    });
  }
  
  // Sort all data points by price
  return detailedPoints.sort((a, b) => a.price - b.price);
}

