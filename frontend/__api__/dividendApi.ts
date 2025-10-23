// Dividend Calendar API Service
import axios from 'axios';
import { apiBaseUrl } from './config';

// Types and interfaces - Updated to match backend response
export interface DividendData {
  pagamento: string;
  codigo: string;
  tipo: string;
  valor: number;
  valor_display: string;
  registro: string;
  ex: string;
  days_until_payment: number;
  status: 'today' | 'upcoming' | 'paid';
  payment_date_obj: string;
}

// Legacy interface for backward compatibility
export interface DividendEntry {
  codigo: string;
  tipo: string;
  valor_brl: string;
  valor_numeric: number;
  registro: string;
  ex: string;
  pagamento: string;
}

export interface DividendSummary {
  total_records: number;
  total_value: number;
  total_value_display: string;
  companies_count: number;
  unique_dates: number;
  status_breakdown: {
    today?: number;
    upcoming?: number;
    paid?: number;
  };
  type_breakdown: {
    counts: { [key: string]: number };
    values: { [key: string]: string };
  };
  upcoming_days_filter: number;
}

export interface DividendResponse {
  data: DividendData[];
  summary: DividendSummary;
  metadata: {
    total_raw_records: number;
    filtered_records: number;
    filters_applied: {
      upcoming_days: number;
      payment_date?: string;
      start_date?: string;
      end_date?: string;
      codigo?: string;
      tipo?: string;
      min_value?: number;
      max_value?: number;
    };
    sorting: {
      sort_order: string;
    };
  };
  error?: string;
}

export interface DividendFilters {
  codigo?: string;
  tipo?: 'Dividendo' | 'JCP';
  min_value?: number;
  max_value?: number;
  start_date?: string;
  end_date?: string;
  payment_date?: string;
  upcoming_days?: number;
  sort_by?: 'codigo' | 'tipo' | 'valor_numeric' | 'registro' | 'ex' | 'pagamento';
  sort_order?: 'asc' | 'desc';
  limit?: number;
  include_summary?: boolean;
}

// API Functions

/**
 * Fetch all dividend calendar data
 */
export const fetchDividendCalendar = async (filters: DividendFilters = {}): Promise<DividendResponse> => {
  try {
    const queryParams = new URLSearchParams();
    
    // Add filters to query params
    Object.entries(filters).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== '') {
        queryParams.append(key, value.toString());
      }
    });

    const endpoint = `${apiBaseUrl}/api/dividend-calendar${queryParams.toString() ? `?${queryParams.toString()}` : ''}`;
    
    const response = await axios.get<DividendResponse>(endpoint);
    
    if (response.data.error) {
      throw new Error(response.data.error);
    }
    
    return response.data;
  } catch (error) {
    console.error('Error fetching dividend calendar:', error);
    throw error;
  }
};

/**
 * Fetch dividends for a specific stock
 */
export const fetchDividendsByStock = async (codigo: string, includeSummary: boolean = true): Promise<DividendResponse> => {
  return fetchDividendCalendar({
    codigo,
    include_summary: includeSummary,
    sort_by: 'pagamento',
    sort_order: 'asc'
  });
};

/**
 * Fetch upcoming dividends in the next N days
 */
export const fetchUpcomingDividends = async (days: number = 30, includeSummary: boolean = true): Promise<DividendResponse> => {
  return fetchDividendCalendar({
    upcoming_days: days,
    include_summary: includeSummary,
    sort_by: 'pagamento',
    sort_order: 'asc'
  });
};

/**
 * Fetch dividends by type (Dividendo or JCP)
 */
export const fetchDividendsByType = async (tipo: 'Dividendo' | 'JCP', limit?: number): Promise<DividendResponse> => {
  return fetchDividendCalendar({
    tipo,
    limit,
    include_summary: true,
    sort_by: 'valor_numeric',
    sort_order: 'desc'
  });
};

/**
 * Fetch highest value dividends
 */
export const fetchHighestValueDividends = async (limit: number = 20): Promise<DividendResponse> => {
  return fetchDividendCalendar({
    sort_by: 'valor_numeric',
    sort_order: 'desc',
    limit,
    include_summary: true
  });
};

/**
 * Fetch dividends in a specific date range
 */
export const fetchDividendsByDateRange = async (
  startDate: string, 
  endDate: string, 
  includeSummary: boolean = true
): Promise<DividendResponse> => {
  return fetchDividendCalendar({
    start_date: startDate,
    end_date: endDate,
    include_summary: includeSummary,
    sort_by: 'pagamento',
    sort_order: 'asc'
  });
};

/**
 * Fetch dividends by value range
 */
export const fetchDividendsByValueRange = async (
  minValue: number, 
  maxValue: number, 
  limit?: number
): Promise<DividendResponse> => {
  return fetchDividendCalendar({
    min_value: minValue,
    max_value: maxValue,
    limit,
    include_summary: true,
    sort_by: 'valor_numeric',
    sort_order: 'desc'
  });
};

/**
 * Search dividends with multiple filters
 */
export const searchDividends = async (searchParams: {
  codigo?: string;
  tipo?: 'Dividendo' | 'JCP';
  minValue?: number;
  maxValue?: number;
  startDate?: string;
  endDate?: string;
  sortBy?: 'codigo' | 'tipo' | 'valor_numeric' | 'pagamento';
  sortOrder?: 'asc' | 'desc';
  limit?: number;
}): Promise<DividendResponse> => {
  return fetchDividendCalendar({
    codigo: searchParams.codigo,
    tipo: searchParams.tipo,
    min_value: searchParams.minValue,
    max_value: searchParams.maxValue,
    start_date: searchParams.startDate,
    end_date: searchParams.endDate,
    sort_by: searchParams.sortBy || 'pagamento',
    sort_order: searchParams.sortOrder || 'asc',
    limit: searchParams.limit,
    include_summary: true
  });
};

// Utility functions for data processing

/**
 * Format currency value for display
 */
export const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL',
    minimumFractionDigits: 2,
    maximumFractionDigits: 6
  }).format(value);
};

/**
 * Format date for display (DD/MM/YYYY)
 */
export const formatDate = (dateString: string): string => {
  if (!dateString) return '';
  
  // If already in DD/MM/YYYY format, return as is
  if (dateString.match(/^\d{2}\/\d{2}\/\d{4}$/)) {
    return dateString;
  }
  
  // Try to parse and format
  try {
    const [day, month, year] = dateString.split('/');
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    return date.toLocaleDateString('pt-BR');
  } catch {
    return dateString;
  }
};

/**
 * Calculate days until payment
 */
export const getDaysUntilPayment = (paymentDate: string): number => {
  try {
    const [day, month, year] = paymentDate.split('/');
    const payment = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    const today = new Date();
    const diffTime = payment.getTime() - today.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    return diffDays;
  } catch {
    return 0;
  }
};

/**
 * Check if payment is upcoming (within next 30 days)
 */
export const isUpcoming = (paymentDate: string, days: number = 30): boolean => {
  const daysUntil = getDaysUntilPayment(paymentDate);
  return daysUntil >= 0 && daysUntil <= days;
};

/**
 * Group dividends by stock code
 */
export const groupDividendsByStock = (dividends: DividendData[]): Record<string, DividendData[]> => {
  return dividends.reduce((acc, dividend) => {
    if (!acc[dividend.codigo]) {
      acc[dividend.codigo] = [];
    }
    acc[dividend.codigo].push(dividend);
    return acc;
  }, {} as Record<string, DividendData[]>);
};

/**
 * Group dividends by payment date
 */
export const groupDividendsByDate = (dividends: DividendData[]): Record<string, DividendData[]> => {
  return dividends.reduce((acc, dividend) => {
    if (!acc[dividend.pagamento]) {
      acc[dividend.pagamento] = [];
    }
    acc[dividend.pagamento].push(dividend);
    return acc;
  }, {} as Record<string, DividendData[]>);
};

/**
 * Calculate total dividend value for a stock
 */
export const calculateTotalValueByStock = (dividends: DividendData[]): Record<string, number> => {
  return dividends.reduce((acc, dividend) => {
    if (!acc[dividend.codigo]) {
      acc[dividend.codigo] = 0;
    }
    acc[dividend.codigo] += dividend.valor;
    return acc;
  }, {} as Record<string, number>);
};
