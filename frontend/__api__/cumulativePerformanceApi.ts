/**
 * Cumulative Performance API Service
 * Service for fetching cumulative performance data from the backend
 */
import apiService from './apiService';

// Types for the cumulative performance API
export interface CumulativePerformanceDataPoint {
  date: string;
  CDI?: number | null;
  SP500?: number | null;
  Gold?: number | null;
  USDBRL?: number | null;
  IBOV?: number | null;
  [key: string]: string | number | null | undefined;
}

export interface CumulativePerformanceApiResponse {
  data: {
    dates: string[];
    assets: {
      [assetName: string]: (number | null)[];
    };
  };
  metadata: {
    total_assets: number;
    available_assets: string[];
    date_range: {
      start_date: string;
      end_date: string;
      total_periods: number;
    };
    normalized: boolean;
    filters_applied: {
      start_date: string | null;
      end_date: string | null;
      assets: string | null;
    };
    performance_metrics?: {
      [asset: string]: {
        total_return: number;
        volatility: number;
        min_value: number;
        max_value: number;
        current_value: number;
      };
    };
  };
}

export interface CumulativePerformanceResponse {
  data: CumulativePerformanceDataPoint[];
  metadata: CumulativePerformanceApiResponse['metadata'];
}

export interface CumulativePerformanceParams {
  start_date?: string;
  end_date?: string;
  assets?: string[];
  normalize?: boolean;
  calculate_metrics?: boolean;
}

/**
 * Fetch cumulative performance data
 */
export const fetchCumulativePerformance = async (
  params: CumulativePerformanceParams = {}
): Promise<CumulativePerformanceResponse> => {
  try {
    const queryParams = new URLSearchParams();
    
    if (params.start_date) {
      queryParams.append('start_date', params.start_date);
    }
    
    if (params.end_date) {
      queryParams.append('end_date', params.end_date);
    }
    
    if (params.assets && params.assets.length > 0) {
      queryParams.append('assets', params.assets.join(','));
    }
    
    if (params.normalize !== undefined) {
      queryParams.append('normalize', params.normalize.toString());
    }
    
    if (params.calculate_metrics !== undefined) {
      queryParams.append('calculate_metrics', params.calculate_metrics.toString());
    }

    const url = `/cumulative-performance${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    const apiResponse = await apiService.get(url);
    
    // Transform the API response to the expected format
    const rawResponse: CumulativePerformanceApiResponse = apiResponse.data;
    
    // Convert the data structure from { dates: [...], assets: { CDI: [...], ... } }
    // to [{ date: "...", CDI: value, SP500: value, ... }]
    const transformedData: CumulativePerformanceDataPoint[] = rawResponse.data.dates.map((date, index) => {
      const dataPoint: CumulativePerformanceDataPoint = { date };
      
      // Add each asset's value for this date
      Object.entries(rawResponse.data.assets).forEach(([assetName, values]) => {
        dataPoint[assetName] = values[index];
      });
      
      return dataPoint;
    });
    
    return {
      data: transformedData,
      metadata: rawResponse.metadata
    };
  } catch (error) {
    console.error('Error fetching cumulative performance data:', error);
    throw new Error('Failed to fetch cumulative performance data');
  }
};

/**
 * Get available date range for cumulative performance data
 */
export const getCumulativePerformanceDateRange = async (): Promise<{
  min_date: string;
  max_date: string;
  available_assets: string[];
}> => {
  try {
    // Since the backend doesn't have a dedicated date range endpoint,
    // we'll fetch a small sample to get the metadata
    const response = await fetchCumulativePerformance({});
    
    return {
      min_date: response.metadata.date_range.start_date,
      max_date: response.metadata.date_range.end_date,
      available_assets: response.metadata.available_assets,
    };
  } catch (error) {
    console.error('Error fetching date range:', error);
    throw new Error('Failed to fetch date range');
  }
};

// Default export
export default {
  fetchCumulativePerformance,
  getCumulativePerformanceDateRange,
};
