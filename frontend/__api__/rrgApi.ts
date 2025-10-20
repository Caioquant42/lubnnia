/**
 * Relative Rotation Graph (RRG) API Service
 * Fetches RRG data for visualizing relative strength and momentum
 * of stocks compared to benchmark (IBOV)
 */
import { apiBaseUrl } from './config';

export type RRGDataPoint = {
  symbol: string;
  date: string;
  rs_ratio: number;
  rs_momentum: number;
  quadrant: 'leading' | 'weakening' | 'lagging' | 'improving';
};

export type RRGResponse = {
  metadata: {
    total_count: number;
    symbol_count: number;
    unique_symbols: string[];
    quadrant_counts: {
      leading: number;
      weakening: number;
      lagging: number;
      improving: number;
    };
    filters_applied: {
      symbol?: string;
      min_rs_ratio?: number;
      max_rs_ratio?: number;
      min_rs_momentum?: number;
      max_rs_momentum?: number;
      quadrant?: string;
      date?: string;
    }
  };
  results: RRGDataPoint[];
};

export type RRGFilters = {
  symbol?: string | string[];
  quadrant?: 'leading' | 'weakening' | 'lagging' | 'improving';
  min_rs_ratio?: number;
  max_rs_ratio?: number;
  min_rs_momentum?: number;
  max_rs_momentum?: number;
  sort_by?: 'symbol' | 'rs_ratio' | 'rs_momentum' | 'date';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  date?: string;
};

/**
 * Fetches RRG data based on the provided filters
 */
export async function fetchRRGData(filters: RRGFilters = {}): Promise<RRGResponse> {
  try {
    // Convert filters to query parameters
    const params = new URLSearchParams();
    
    if (filters.symbol) {
      if (Array.isArray(filters.symbol)) {
        params.append('symbol', filters.symbol.join(','));
      } else {
        params.append('symbol', filters.symbol);
      }
    }
    
    if (filters.quadrant) {
      params.append('quadrant', filters.quadrant);
    }
    
    if (filters.min_rs_ratio !== undefined) {
      params.append('min_rs_ratio', filters.min_rs_ratio.toString());
    }
    
    if (filters.max_rs_ratio !== undefined) {
      params.append('max_rs_ratio', filters.max_rs_ratio.toString());
    }
    
    if (filters.min_rs_momentum !== undefined) {
      params.append('min_rs_momentum', filters.min_rs_momentum.toString());
    }
    
    if (filters.max_rs_momentum !== undefined) {
      params.append('max_rs_momentum', filters.max_rs_momentum.toString());
    }
    
    if (filters.sort_by) {
      params.append('sort_by', filters.sort_by);
    }
    
    if (filters.sort_order) {
      params.append('sort_order', filters.sort_order);
    }
    
    if (filters.limit) {
      params.append('limit', filters.limit.toString());
    }
    
    if (filters.date) {
      params.append('date', filters.date);
    }
    
    const queryString = params.toString();
    const url = `${apiBaseUrl}/api/rrg${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`Error fetching RRG data: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch RRG data:', error);
    throw error;
  }
}

/**
 * Get all available symbols from the RRG data
 */
export async function getAvailableRRGSymbols(): Promise<string[]> {
  try {
    // Fetch with a small limit just to get metadata
    const response = await fetchRRGData({ limit: 1 });
    return response.metadata.unique_symbols;
  } catch (error) {
    console.error('Failed to fetch available symbols:', error);
    throw error;
  }
}

/**
 * Get all available dates in the RRG data
 */
export async function getAvailableRRGDates(): Promise<string[]> {
  try {
    // Fetch data without date filter to get all available dates
    const response = await fetchRRGData({ limit: 1000 });
    
    // Extract all unique dates from the results
    const uniqueDates = new Set<string>();
    response.results.forEach(item => {
      uniqueDates.add(item.date);
    });
    
    return Array.from(uniqueDates).sort();
  } catch (error) {
    console.error('Failed to fetch available dates:', error);
    throw error;
  }
}

/**
 * Get data for tracking RRG movement over time for specific symbols
 */
export async function getRRGTimeSeries(symbols: string[]): Promise<RRGResponse> {
  try {
    if (!symbols.length) {
      throw new Error('No symbols provided for time series data');
    }
    
    // Get data for the specified symbols without date filtering
    // to retrieve all available data points for time series analysis
    return await fetchRRGData({
      symbol: symbols,
      sort_by: 'date',
      sort_order: 'asc',
      limit: 1000, // Adjust as needed
    });
  } catch (error) {
    console.error('Failed to fetch RRG time series data:', error);
    throw error;
  }
}

/**
 * Fetch data for a specific quadrant
 */
export async function fetchRRGQuadrantData(
  quadrant: 'leading' | 'weakening' | 'lagging' | 'improving',
  limit: number = 50
): Promise<RRGResponse> {
  try {
    return await fetchRRGData({
      quadrant,
      limit,
      sort_by: 'rs_ratio',
      sort_order: quadrant === 'leading' || quadrant === 'weakening' ? 'desc' : 'asc'
    });
  } catch (error) {
    console.error(`Failed to fetch ${quadrant} quadrant data:`, error);
    throw error;
  }
}