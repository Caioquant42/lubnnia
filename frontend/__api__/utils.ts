/**
 * API Utilities
 * Common utility functions for API operations
 */
import { apiBaseUrl, errorMessages, handleApiError } from './config';

/**
 * Creates a full URL for an endpoint by combining the API base URL with the endpoint path
 * @param endpoint - The API endpoint path
 * @returns The complete API URL
 */
export function createApiUrl(endpoint: string): string {
  // Ensure endpoint starts with a slash
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  
  // Construct the full URL
  return `${apiBaseUrl}${normalizedEndpoint}`;
}

/**
 * Builds a query parameter string from an object of parameters
 * @param params - Object containing query parameters
 * @returns Encoded query string
 */
export function buildQueryParams(params: Record<string, any>): string {
  // Filter out null/undefined values
  const validParams = Object.entries(params).filter(([_, value]) => 
    value !== null && value !== undefined && value !== '');
  
  if (validParams.length === 0) {
    return '';
  }
  
  // Convert parameters to query string
  const queryString = validParams.map(([key, value]) => {
    // Handle arrays by joining with commas
    if (Array.isArray(value)) {
      return `${encodeURIComponent(key)}=${encodeURIComponent(value.join(','))}`;
    }
    return `${encodeURIComponent(key)}=${encodeURIComponent(value)}`;
  }).join('&');
  
  return `?${queryString}`;
}

/**
 * Formats error responses from APIs into a standard format
 * @param error - The error object from an API request
 * @returns A standardized error object
 */
export function formatApiError(error: any): { 
  message: string; 
  status?: number; 
  details?: string; 
  isNetworkError?: boolean;
} {
  // Get user-friendly error message
  const message = handleApiError(error);
  
  // Build standardized error object
  const formattedError = {
    message,
    isNetworkError: !error.response,
  };
  
  // Add status code if available
  if (error.response?.status) {
    Object.assign(formattedError, { status: error.response.status });
  }
  
  // Add error details if available
  if (error.response?.data?.details) {
    Object.assign(formattedError, { details: error.response.data.details });
  }
  
  return formattedError;
}

/**
 * Standardize API endpoint paths by ensuring they are formatted correctly
 * This helps prevent CORS issues with duplicate /api prefixes
 * @param path - The API endpoint path
 * @returns Normalized API path
 */
export function normalizeApiPath(path: string): string {
  // If the path starts with /api/ (like "/api/something"), remove the "/api" prefix
  // to avoid duplicate prefixes when used with getApiUrl
  if (path.startsWith('/api/')) {
    return path.substring(4); // Remove the first 4 characters (/api)
  }
  
  // Otherwise return the path as is
  return path;
}

/**
 * Returns a retry configuration for axios-retry
 * @param retries - Number of retries (default: 3)
 * @returns Retry configuration object
 */
export function getRetryConfig(retries = 3) {
  return {
    retries,
    retryDelay: (retryCount: number) => {
      return retryCount * 1000; // exponential backoff
    },
    retryCondition: (error: any) => {
      // Only retry on network errors or 5xx server errors
      return !error.response || (error.response.status >= 500 && error.response.status < 600);
    }
  };
}
