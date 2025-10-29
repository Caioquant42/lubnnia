import apiService from './apiService';

/**
 * Types for covered call data
 */
export interface CoveredCallOption {
  symbol: string;
  name: string;
  parent_symbol: string;
  spot_price: number;
  strike: number;
  bid: number;
  ask: number;
  days_to_maturity: number;
  due_date: string;
  cdi_relative_return: number;
  annual_return: number;
  spot_variation_to_max_return: number;
  pm_distance_to_profit: number;
  score: number;
  maturity_type: string;
  block_date?: string;
  moneyness: string;
}

export interface CoveredCallMetadata {
  total_count: number;
  symbol_count: number;
  unique_symbols: string[];
  maturity_ranges: string[];
  filters_applied: {
    maturity_range?: string;
    symbol?: string;
    min_cdi_relative_return?: number;
    sort_by?: string;
    sort_order?: string;
    limit?: number;
  };
}

export interface CoveredCallResponse {
  metadata: CoveredCallMetadata;
  results: {
    [key: string]: CoveredCallOption[];
  };
}

const coveredcallApi = {
  /**
   * Get covered call strategy options
   * @param maturityRange Optional maturity range to filter by (less_than_14_days, between_15_and_30_days, etc.)
   * @param symbol Optional underlying stock symbol to filter by
   * @param minCdiRelativeReturn Optional minimum CDI relative return
   * @param sortBy Optional field to sort by (default: cdi_relative_return)
   * @param sortOrder Optional sort order (asc or desc, default: desc)
   * @param limit Optional number of results to return
   * @returns Promise with covered call strategy data
   */
  getCoveredCalls: async (
    maturityRange?: string,
    symbol?: string,
    minCdiRelativeReturn?: number,
    sortBy: string = 'cdi_relative_return',
    sortOrder: string = 'desc',
    limit?: number
  ) => {
    try {
      const params: Record<string, string | number> = {};
      
      if (maturityRange) params.maturity_range = maturityRange;
      if (symbol) params.symbol = symbol;
      if (minCdiRelativeReturn !== undefined) params.min_cdi_relative_return = minCdiRelativeReturn;
      if (sortBy) params.sort_by = sortBy;
      if (sortOrder) params.sort_order = sortOrder;
      if (limit !== undefined) params.limit = limit;
      
      const response = await apiService.get<CoveredCallResponse>('/api/covered-call', { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching covered call strategies:', error);
      throw error;
    }
  }
};

export default coveredcallApi;