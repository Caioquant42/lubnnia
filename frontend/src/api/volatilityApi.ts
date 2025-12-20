import axios from 'axios';
import { apiBaseUrl } from './config';

export type StockVolatilityData = {
  symbol: string;
  name: string;
  type: string;
  close: number;
  variation: number;
  iv_current: number;
  ewma_current: number;
  iv_ewma_ratio: number;
  iv_1y_rank: number;
  iv_1y_percentile: number;
  iv_6m_percentile: number;
  ewma_1y_percentile: number;
  ewma_6m_percentile: number;
  beta_ibov: number;
  correl_ibov: number;
  stdv_1y: number;
  stdv_5d: number;
  entropy: number;
  sector: string;
  short_term_trend: number;
  middle_term_trend: number;
  semi_return_1y: number;
  garch11_1y: number;
};

export type VolatilityApiResponse = {
  metadata: {
    total_count: number;
    filters_applied: {
      symbol?: string;
      min_iv_current?: number;
      max_iv_current?: number;
      min_beta_ibov?: number;
      max_beta_ibov?: number;
      min_iv_ewma_ratio?: number;
      max_iv_ewma_ratio?: number;
      sort_by?: string;
      sort_order?: string;
      limit?: number;
    };
  };
  results: StockVolatilityData[];
};

export const fetchStocksVolatilityData = async (
  params: {
    symbol?: string;
    min_iv_current?: number;
    max_iv_current?: number;
    min_beta_ibov?: number;
    max_beta_ibov?: number;
    min_iv_ewma_ratio?: number;
    max_iv_ewma_ratio?: number;
    sort_by?: string;
    sort_order?: string;
    limit?: number;
  } = {}
): Promise<VolatilityApiResponse> => {
  try {
    const response = await axios.get(`${apiBaseUrl}/api/ibov-stocks`, {
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stocks volatility data:', error);
    throw error;
  }
};

// Helper functions for volatility analysis

/**
 * Categorize IV/EWMA ratio into volatility status
 */
export const categorizeVolatility = (ratio: number): string => {
  if (ratio < 0.8) return 'Extremamente Baixa';
  if (ratio < 0.9) return 'Muito Baixa';
  if (ratio < 1.0) return 'Baixa';
  if (ratio < 1.1) return 'Neutra';
  if (ratio < 1.2) return 'Alta';
  if (ratio < 1.3) return 'Muito Alta';
  return 'Extremamente Alta';
};

/**
 * Get volatility status color
 */
export const getVolatilityStatusColor = (ratio: number): string => {
  if (ratio < 0.8) return 'blue-500'; // Extremely Low
  if (ratio < 0.9) return 'cyan-500'; // Very Low
  if (ratio < 1.0) return 'green-500'; // Low
  if (ratio < 1.1) return 'yellow-500'; // Neutral
  if (ratio < 1.2) return 'orange-500'; // High
  if (ratio < 1.3) return 'red-500'; // Very High
  return 'purple-500'; // Extremely High
};

/**
 * Get market sentiment based on aggregated volatility data
 */
export const getMarketSentiment = (
  stocks: StockVolatilityData[]
): {
  sentiment: string;
  description: string;
  ratioAvg: number;
  distribution: Record<string, number>;
} => {
  if (!stocks || stocks.length === 0) {
    return {
      sentiment: 'Desconhecido',
      description: 'Nenhum dado disponível',
      ratioAvg: 0,
      distribution: {},
    };
  }

  // Calculate average IV/EWMA ratio
  const validStocks = stocks.filter(
    (stock) => stock.iv_ewma_ratio !== undefined && !isNaN(stock.iv_ewma_ratio)
  );

  const ratioSum = validStocks.reduce(
    (sum, stock) => sum + stock.iv_ewma_ratio,
    0
  );
  const ratioAvg = validStocks.length > 0 ? ratioSum / validStocks.length : 0;

  // Calculate distribution of volatility categories
  const distribution: Record<string, number> = {
    'Extremamente Baixa': 0,
    'Muito Baixa': 0,
    Baixa: 0,
    Neutra: 0,
    Alta: 0,
    'Muito Alta': 0,
    'Extremamente Alta': 0,
  };

  validStocks.forEach((stock) => {
    const category = categorizeVolatility(stock.iv_ewma_ratio);
    distribution[category]++;
  });

  // Determine overall market sentiment
  let sentiment = '';
  let description = '';

  if (ratioAvg < 0.85) {
    sentiment = 'Complacente';
    description =
      'O mercado está subestimando significativamente a volatilidade, sugerindo possível complacência entre os investidores.';
  } else if (ratioAvg < 0.95) {
    sentiment = 'Calmo';
    description =
      'O mercado está relativamente calmo com volatilidade precificada abaixo dos níveis históricos.';
  } else if (ratioAvg < 1.05) {
    sentiment = 'Neutro';
    description =
      'O mercado está precificando a volatilidade em linha com os níveis históricos.';
  } else if (ratioAvg < 1.15) {
    sentiment = 'Cauteloso';
    description =
      'O mercado mostra sinais de cautela com volatilidade precificada acima dos níveis históricos.';
  } else if (ratioAvg < 1.3) {
    sentiment = 'Temeroso';
    description =
      'O mercado está precificando volatilidade significativa, sugerindo medo entre os investidores.';
  } else {
    sentiment = 'Pânico';
    description =
      'O mercado está em estado de pânico com precificação extrema de volatilidade.';
  }

  return {
    sentiment,
    description,
    ratioAvg,
    distribution,
  };
};

/**
 * Calculate volatility metrics for a specific stock
 */
export const analyzeStockVolatility = (stock: StockVolatilityData) => {
  const category = categorizeVolatility(stock.iv_ewma_ratio);
  const color = getVolatilityStatusColor(stock.iv_ewma_ratio);

  // Analyze trend based on short_term_trend and middle_term_trend
  let trend = 'Neutral';
  if (stock.short_term_trend === 1 && stock.middle_term_trend === 1) {
    trend = 'Strong Uptrend';
  } else if (stock.short_term_trend === 1) {
    trend = 'Short-term Uptrend';
  } else if (stock.middle_term_trend === 1) {
    trend = 'Medium-term Uptrend';
  } else if (stock.short_term_trend === -1 && stock.middle_term_trend === -1) {
    trend = 'Strong Downtrend';
  } else if (stock.short_term_trend === -1) {
    trend = 'Short-term Downtrend';
  } else if (stock.middle_term_trend === -1) {
    trend = 'Medium-term Downtrend';
  }

  // Analyze volatility characteristics
  let volatilityCharacteristics = [];

  if (stock.iv_ewma_ratio > 1.2) {
    volatilityCharacteristics.push(
      'Implied volatility is significantly higher than historical volatility'
    );
    volatilityCharacteristics.push(
      'Market is anticipating increased future volatility'
    );
  } else if (stock.iv_ewma_ratio < 0.8) {
    volatilityCharacteristics.push(
      'Implied volatility is significantly lower than historical volatility'
    );
    volatilityCharacteristics.push(
      'Market is expecting decreased future volatility'
    );
  }

  if (stock.iv_1y_percentile > 80) {
    volatilityCharacteristics.push(
      'Current IV is in the top 20% of the 1-year range'
    );
  } else if (stock.iv_1y_percentile < 20) {
    volatilityCharacteristics.push(
      'Current IV is in the bottom 20% of the 1-year range'
    );
  }

  if (stock.beta_ibov > 1.5) {
    volatilityCharacteristics.push(
      'Stock has very high beta relative to Ibovespa'
    );
  } else if (stock.beta_ibov < 0.5) {
    volatilityCharacteristics.push('Stock has low beta relative to Ibovespa');
  }

  return {
    category,
    color,
    trend,
    volatilityCharacteristics,
  };
};
