import axios from 'axios';
import { apiBaseUrl } from './config';

export type StockVariationData = {
  symbol: string;
  name: string;
  type: string;
  close: number;
  variation: number;
  volume?: number;
  sector?: string;
  market_cap?: number;
};

export type VariationApiResponse = {
  metadata: {
    total_count: number;
    filters_applied: {
      symbol?: string;
      min_variation?: number;
      max_variation?: number;
      sort_by?: string;
      sort_order?: string;
      limit?: number;
    };
  };
  results: StockVariationData[];
};

export const fetchStocksVariationData = async (
  params: {
    symbol?: string;
    min_variation?: number;
    max_variation?: number;
    sort_by?: string;
    sort_order?: string;
    limit?: number;
  } = {}
): Promise<VariationApiResponse> => {
  try {
    const response = await axios.get(`${apiBaseUrl}/api/ibov-stocks`, {
      params,
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching stocks variation data:', error);
    throw error;
  }
};

// Helper functions for variation analysis

/**
 * Categorize variation into performance status
 */
export const categorizeVariation = (variation: number): string => {
  if (variation < -3) return 'Strong Decline';
  if (variation < -1) return 'Decline';
  if (variation < -0.5) return 'Weak Decline';
  if (variation < 0.5) return 'Neutral';
  if (variation < 1) return 'Weak Gain';
  if (variation < 3) return 'Gain';
  return 'Strong Gain';
};

/**
 * Get variation status color for chart visualization
 */
export const getVariationColor = (variation: number): string => {
  // Normalize variation to a scale for color interpolation
  const normalizedVariation = Math.max(-5, Math.min(5, variation)); // Clamp between -5 and 5
  const intensity = Math.abs(normalizedVariation) / 5; // 0 to 1

  if (variation >= 0) {
    // Green shades for positive variations
    const green = Math.floor(50 + intensity * 150); // 50 to 200
    return `rgb(0, ${green}, 0)`;
  } else {
    // Red shades for negative variations
    const red = Math.floor(50 + intensity * 150); // 50 to 200
    return `rgb(${red}, 0, 0)`;
  }
};

/**
 * Get variation magnitude for bubble sizing
 */
export const getVariationMagnitude = (variation: number): number => {
  return Math.abs(variation);
};

/**
 * Transform stock data for sunburst chart visualization
 */
export const transformDataForSunburst = (stocks: StockVariationData[]) => {
  // Group stocks by sector (if available) or create a single group
  const groupedData: { [key: string]: StockVariationData[] } = {};

  stocks.forEach((stock) => {
    const sector = stock.sector || 'Uncategorized';
    if (!groupedData[sector]) {
      groupedData[sector] = [];
    }
    groupedData[sector].push(stock);
  });

  // Transform to hierarchical structure for sunburst
  const sunburstData = {
    name: 'IBOV Stocks',
    children: Object.entries(groupedData).map(([sector, sectorStocks]) => ({
      name: sector, // Keep original sector name for mapping
      children: sectorStocks.map((stock) => ({
        name: stock.symbol,
        value: getVariationMagnitude(stock.variation),
        variation: stock.variation,
        color: getVariationColor(stock.variation),
        fullName: stock.name,
        close: stock.close,
        sector: sector,
      })),
    })),
  };

  return sunburstData;
};

/**
 * Get market sentiment based on aggregated variation data
 */
export const getVariationSentiment = (stocks: StockVariationData[]) => {
  if (!stocks || stocks.length === 0) {
    return {
      sentiment: 'Unknown',
      avgVariation: 0,
      positiveCount: 0,
      negativeCount: 0,
      neutralCount: 0,
      description: 'No data available',
    };
  }

  const validStocks = stocks.filter(
    (stock) => stock.variation !== undefined && !isNaN(stock.variation)
  );

  const avgVariation =
    validStocks.reduce((sum, stock) => sum + stock.variation, 0) /
    validStocks.length;

  const positiveCount = validStocks.filter(
    (stock) => stock.variation > 0.5
  ).length;
  const negativeCount = validStocks.filter(
    (stock) => stock.variation < -0.5
  ).length;
  const neutralCount = validStocks.length - positiveCount - negativeCount;

  let sentiment = 'Neutral';
  let description = 'Market showing mixed signals';

  if (avgVariation > 1) {
    sentiment = 'Bullish';
    description = 'Market showing strong positive momentum';
  } else if (avgVariation > 0.3) {
    sentiment = 'Moderately Bullish';
    description = 'Market showing positive trends';
  } else if (avgVariation < -1) {
    sentiment = 'Bearish';
    description = 'Market showing strong negative momentum';
  } else if (avgVariation < -0.3) {
    sentiment = 'Moderately Bearish';
    description = 'Market showing negative trends';
  }

  return {
    sentiment,
    avgVariation: Number(avgVariation.toFixed(2)),
    positiveCount,
    negativeCount,
    neutralCount,
    description,
  };
};
