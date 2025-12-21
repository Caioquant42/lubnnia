import axios from 'axios';
import { apiBaseUrl, defaultHeaders, requestTimeout } from './config';

// Define interfaces for tail hedge data
export interface TailHedgePut {
  symbol: string;
  underlying: string;
  strike: number;
  delta: number;
  price: number;
  expiry_date: string;
  days_to_expiry: number;
  gamma?: number;
  vega?: number;
  theta?: number;
  iv?: number;
}

export interface TailHedgeCall {
  symbol: string;
  underlying: string;
  strike: number;
  delta: number;
  price: number;
  expiry_date: string;
  days_to_expiry: number;
  gamma?: number;
  vega?: number;
  theta?: number;
  iv?: number;
}

export interface TailHedgeStrategyMetrics {
  put_quantity: number;
  call_quantity: number;
  total_put_cost: number;
  total_call_premium: number;
  net_cost: number;
  financing_ratio: number;
  financing_percentage: number;
  protection_coverage: number;
  protection_percentage: number;
  max_loss_protected: number;
  breakeven_price: number;
  put_strike: number;
  call_strike: number;
}

export interface TailHedgePayoffFunction {
  price_points: number[];
  pnl_points: number[];
  breakeven_points: number[];
  max_profit: number;
  max_loss: number;
}

export interface TailHedgeStrategy {
  put: TailHedgePut;
  call: TailHedgeCall;
  strategy_metrics: TailHedgeStrategyMetrics;
  payoff_function: TailHedgePayoffFunction;
}

export interface TailHedgeApiResponse {
  metadata: {
    total_count: number;
    underlying: string;
    exchange: string;
    spot_price: number;
    portfolio_size: number;
    portfolio_type: 'units' | 'usd';
    portfolio_value_usd: number;
    portfolio_hedge_percentage: number;
    financing_percentage: number;
    protection_target: number;
    timestamp: string;
  };
  strategies: TailHedgeStrategy[];
}

/**
 * Fetches tail hedge strategy data from the API
 */
export async function getTailHedgeStrategies(
  params?: {
    underlying?: string;
    exchange?: 'bybit';
    portfolio_size?: number;
    portfolio_type?: 'units' | 'usd';
    portfolio_hedge_percentage?: 0.50 | 0.75 | 1.0;
    financing_percentage?: 0.50 | 0.75 | 1.0;
    put_delta_min?: number;
    put_delta_max?: number;
    call_delta?: number;
    put_min_days?: number;
    put_max_days?: number;
    call_min_days?: number;
    call_max_days?: number;
    min_maturity_diff?: number;
  }
) {
  try {
    const response = await axios.get<TailHedgeApiResponse>(
      `${apiBaseUrl}/api/tail-hedge`,
      {
        headers: defaultHeaders,
        timeout: requestTimeout,
        params
      }
    );
    
    return response.data;
  } catch (error) {
    console.error('Error fetching tail hedge data:', error);
    throw error;
  }
}

/**
 * Generates optimized payoff data for tail hedge strategy visualization
 * with adaptive step sizing based on price range
 */
export function generateTailHedgePayoffData(strategy: TailHedgeStrategy) {
  const { put, call, strategy_metrics, payoff_function } = strategy;
  const putStrike = put.strike;
  const callStrike = call.strike;
  const putPrice = put.price;
  const callPrice = call.price;
  // Note: spot_price should come from metadata, but for now use put_strike as fallback
  // This will be corrected when metadata is passed to this function
  const spotPrice = strategy_metrics.put_strike; // Fallback - should use actual spot price
  const putQuantity = strategy_metrics.put_quantity;
  const callQuantity = strategy_metrics.call_quantity;
  
  // Use payoff function from API if available
  if (payoff_function && payoff_function.price_points && payoff_function.pnl_points) {
    return payoff_function.price_points.map((price, index) => ({
      price: price,
      payoff: payoff_function.pnl_points[index],
      negativePayoff: payoff_function.pnl_points[index] < 0 ? payoff_function.pnl_points[index] : null,
      callPayoff: (callPrice - Math.max(price - callStrike, 0)) * callQuantity,
      putPayoff: (Math.max(putStrike - price, 0) - putPrice) * putQuantity
    }));
  }
  
  // Fallback: Calculate adaptive step size based on price range
  const priceRange = Math.max(callStrike, spotPrice) - Math.min(putStrike, spotPrice);
  let step = 1;
  
  if (priceRange > 20000) {
    step = 100;
  } else if (priceRange > 10000) {
    step = 50;
  } else if (priceRange > 5000) {
    step = 25;
  } else if (priceRange > 1000) {
    step = 10;
  } else {
    step = 5;
  }
  
  // Generate optimized data points
  const minX = Math.min(putStrike * 0.90, spotPrice * 0.80);
  const maxX = Math.max(callStrike * 1.10, spotPrice * 1.20);
  
  const detailedPoints = [];
  for (let price = minX; price <= maxX; price += step) {
    const roundedPrice = Math.round(price * 100) / 100;
    
    // Long put payoff: max(put_strike - price, 0) - put_price
    const putPayoff = (Math.max(putStrike - roundedPrice, 0) - putPrice) * putQuantity;
    
    // Short call payoff: call_price - max(price - call_strike, 0)
    const callPayoff = (callPrice - Math.max(roundedPrice - callStrike, 0)) * callQuantity;
    
    // Total payoff
    const totalPayoff = putPayoff + callPayoff;
    
    detailedPoints.push({
      price: roundedPrice,
      payoff: totalPayoff,
      negativePayoff: totalPayoff < 0 ? totalPayoff : null,
      callPayoff,
      putPayoff
    });
  }
  
  // Sort all data points by price
  return detailedPoints.sort((a, b) => a.price - b.price);
}

