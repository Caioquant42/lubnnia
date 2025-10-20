/**
 * Recommendations API Service
 * Fetches analyst recommendations and price targets for Brazilian stocks
 * Provides aggregated data on buy/sell ratings and target prices
 */
import apiService from './apiService';

/**
 * Types for recommendation data
 */
export interface RecommendationItem {
  symbol: string;
  'Strong Buy': number;
  Buy: number;
  Hold: number;
  Underperform: number;
  Sell: number;
  'Average Rating': number;
  'Median Target': number;
  'Mean Target': number;
  'High Target': number;
  'Low Target': number;
  'Current Price': number;
  '% Distance to High': number;
  '% Distance to Mean': number;
  '% Distance to Median': number;
  'Last Updated': string;
  [key: string]: any; // For any additional properties
}

export interface B3Recommendation {
  currentPrice: number;
  targetHighPrice: number;
  targetLowPrice: number;
  targetMeanPrice: number;
  targetMedianPrice: number;
  recommendationMean: number;
  recommendationKey: string;
  numberOfAnalystOpinions: number;
  averageAnalystRating?: string;
}

export interface B3RecommendationsResponse {
  analysis: string;
  description: string;
  count: number;
  results: { [ticker: string]: B3Recommendation };
}

export interface AnalyzedRecommendation {
  ticker: string;
  symbol?: string;
  combined_score: number;
  relevance: number;
  currentPrice: number;
  numberOfAnalystOpinions: number;
  price_target_consensus: number;
  recommendationKey: string;
  recommendationMean: number;
  return_target_consensus: number;
  targetHighPrice: number;
  targetMedianPrice: number;
  targetLowPrice?: number;
  '% Distance to High'?: number;
  '% Distance to Median'?: number;
  '% Distance to Low'?: number;
  [key: string]: any; // For additional properties from backend
}

export interface RecommendationsResponse {
  analysis: string;
  description: string;
  count: number;
  strong_buy_count?: number;
  buy_count?: number;
  results: RecommendationItem[] | AnalyzedRecommendation[];
}

const recommendationsApi = {
  /**
   * Get raw recommendation data for all symbols or a specific symbol
   * @param symbol Optional stock symbol to filter by
   * @returns Promise with recommendation data
   */
  getRawRecommendations: async (symbol?: string) => {
    try {
      const params = symbol ? { symbol } : {};
      const response = await apiService.get<RecommendationsResponse>('/api/br-recommendations', { params });
      return response;
    } catch (error) {
      console.error('Error fetching raw recommendations:', error);
      throw error;
    }
  },

  /**
   * Get B3 formatted recommendations with specific fields
   * @param symbol Optional stock symbol to filter by
   * @returns Promise with B3 recommendation data
   */
  getB3Recommendations: async (symbol?: string) => {
    try {
      const params = { analysis: 'b3', ...(symbol ? { symbol } : {}) };
      const response = await apiService.get<B3RecommendationsResponse>('/api/br-recommendations', { params });
      return response;
    } catch (error) {
      console.error('Error fetching B3 recommendations:', error);
      throw error;
    }
  },
  /**
   * Get analyzed IBOV stocks ranked by relevance
   * @param symbol Optional stock symbol to filter by
   * @returns Promise with IBOV analysis data
   */
  getIbovAnalysis: async (symbol?: string) => {
    try {
      const params = { analysis: 'ibov', ...(symbol ? { symbol } : {}) };
      // Use the endpoints object which contains the correct path
      const response = await apiService.get<RecommendationsResponse>(
        '/br-recommendations', 
        { params }
      );
      return response;
    } catch (error) {
      console.error('Error fetching IBOV analysis:', error);
      throw error;
    }
  },
  /**
   * Get stocks with "Buy" recommendations sorted by relevance
   * @param symbol Optional stock symbol to filter by
   * @returns Promise with Buy analysis data
   */
  getBuyRecommendations: async (symbol?: string) => {
    try {
      const params = { analysis: 'buy', ...(symbol ? { symbol } : {}) };
      const response = await apiService.get<RecommendationsResponse>(
        '/br-recommendations', 
        { params }
      );
      return response;
    } catch (error) {
      console.error('Error fetching Buy recommendations:', error);
      throw error;
    }
  },

  /**
   * Get stocks with "Strong Buy" recommendations sorted by relevance
   * @param symbol Optional stock symbol to filter by
   * @returns Promise with Strong Buy analysis data
   */  getStrongBuyRecommendations: async (symbol?: string) => {
    try {
      const params = { analysis: 'strong_buy', ...(symbol ? { symbol } : {}) };
      const response = await apiService.get<RecommendationsResponse>(
        '/br-recommendations', 
        { params }
      );
      return response;
    } catch (error) {
      console.error('Error fetching Strong Buy recommendations:', error);
      throw error; // Add throw statement to propagate error
    }
  },

  /**
   * Get combined "Buy" and "Strong Buy" recommendations
   * @param symbol Optional stock symbol to filter by
   * @returns Promise with combined buy recommendations data
   */
  getAllBuyRecommendations: async (symbol?: string) => {
    try {
      const params = { analysis: 'all_buy', ...(symbol ? { symbol } : {}) };
      const response = await apiService.get<RecommendationsResponse>('/api/br-recommendations', { params });
      return response;
    } catch (error) {
      console.error('Error fetching All Buy recommendations:', error);
      throw error;
    }
  }
};

export default recommendationsApi;
