/**
 * Fluxo DDM API Service
 * Service for fetching investment flow data from the backend
 */
import apiService from './apiService';

// Types for the Fluxo DDM API
export interface FluxoDataPoint {
  Data?: string; // Date in DD/MM/YYYY format
  Estrangeiro?: number; // Foreign investor flows (in millions)
  Institucional?: number; // Institutional investor flows (in millions)
  PF?: number; // Individual investor flows (in millions)
  IF?: number; // Financial institution flows (in millions)
  Outros?: number; // Other investor flows (in millions)
}

export interface FluxoApiResponse {
  data: FluxoDataPoint[];
  metadata: {
    total_records: number;
    filtered_records: number;
    investor_types: string[];
  };
}

export interface FluxoResponse {
  data: FluxoDataPoint[];
  metadata: FluxoApiResponse['metadata'];
  error?: string;
}

// Query parameters for filtering flux data
export interface FluxoQueryParams {
  limit?: number;
  investor_type?: 'all' | 'Estrangeiro' | 'Institucional' | 'PF' | 'IF' | 'Outros';
}

/**
 * Fetch flux DDM data from the backend
 * @param params - Query parameters for filtering
 * @returns Promise with flux data
 */
export const fetchFluxoData = async (params?: FluxoQueryParams): Promise<FluxoResponse> => {
  try {
    const queryString = params ? new URLSearchParams(
      Object.entries(params)
        .filter(([_, value]) => value !== undefined && value !== null)
        .map(([key, value]) => [key, value.toString()])
    ).toString() : '';

    const url = `/fluxo-ddm${queryString ? `?${queryString}` : ''}`;
    
    console.log('Fetching flux data from:', url);
    
    const response = await apiService.get<FluxoApiResponse>(url);
    
    console.log('Flux API response:', response.data);
    
    return {
      data: response.data.data || [],
      metadata: response.data.metadata,
    };
  } catch (error: any) {
    console.error('Error fetching flux data:', error);
    
    return {
      data: [],
      metadata: {
        total_records: 0,
        filtered_records: 0,
        investor_types: ['Estrangeiro', 'Institucional', 'PF', 'IF', 'Outros']
      },
      error: error.userMessage || error.message || 'Failed to fetch flux data'
    };
  }
};

/**
 * Fetch flux data for a specific investor type
 */
export const fetchFluxoByInvestorType = async (
  investorType: FluxoQueryParams['investor_type'],
  limit: number = 50
): Promise<FluxoResponse> => {
  return fetchFluxoData({
    limit,
    investor_type: investorType
  });
};

export default {
  fetchFluxoData,
  fetchFluxoByInvestorType
};
