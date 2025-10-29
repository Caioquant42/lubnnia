/**
 * API Service
 * Central service for making API requests with consistent configuration
 */
import axios from 'axios';
import {
  apiBaseUrl,
  defaultHeaders,
  getApiUrl,
  errorMessages,
  requestTimeout,
} from './config';
import { formatApiError } from './utils';

// Create an axios instance with default configuration
const apiService = axios.create({
  baseURL: apiBaseUrl,
  timeout: requestTimeout,
  headers: defaultHeaders,
  withCredentials: false, // Prevents sending cookies with cross-origin requests
});

// Request interceptor for API calls
apiService.interceptors.request.use(
  async (config) => {
    // Fix URL paths to ensure consistent API calls
    if (config.url) {
      // 1. Fix duplicate "/api" prefixes
      if (config.url.includes('/api/api/')) {
        config.url = config.url.replace(/\/api\/api\//g, '/api/');
      }

      // 2. If URL doesn't start with http:// or https:// and doesn't have /api prefix, add it
      if (
        !config.url.startsWith('http://') &&
        !config.url.startsWith('https://') &&
        !config.url.startsWith('/api')
      ) {
        config.url = `/api/${config.url.startsWith('/') ? config.url.substring(1) : config.url}`;
      }
    }

    // You can add auth tokens here if needed
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for API calls
apiService.interceptors.response.use(
  (response) => response,
  async (error) => {
    let errorMessage = errorMessages.default;

    if (error.response) {
      // Handle specific error codes
      if (error.response.status === 401) {
        errorMessage = 'Acesso não autorizado';
        console.error(errorMessage);
      } else if (error.response.status === 404) {
        errorMessage = errorMessages.notFound;
        console.error(errorMessage);
      } else if (error.response.status >= 500) {
        errorMessage = errorMessages.serverError;
        console.error(errorMessage);
      }
    } else if (error.request) {
      // The request was made but no response was received
      errorMessage = errorMessages.network;
      console.error(errorMessage);

      // Check if this might be a CORS error
      if (
        error.message &&
        (error.message.includes('Network Error') ||
          error.message.includes('CORS') ||
          error.message.includes('Origin'))
      ) {
        errorMessage = errorMessages.cors;
        console.error(errorMessage);
      }

      // Check for timeout
      if (error.message && error.message.includes('timeout')) {
        errorMessage = errorMessages.timeout;
        console.error(errorMessage);
      }
    } else {
      // Something happened in setting up the request
      console.error('Error setting up request:', error.message);
    }

    // Add the error message to the error object for components to use
    error.userMessage = errorMessage;

    return Promise.reject(error);
  }
);

// Add a response interceptor to handle cases where the data is a JSON string
apiService.interceptors.response.use(
  (response) => {
    // If the response.data is a string and looks like JSON, try to parse it
    if (
      typeof response.data === 'string' &&
      (response.data.trim().startsWith('{') ||
        response.data.trim().startsWith('['))
    ) {
      try {
        response.data = JSON.parse(response.data);
      } catch (e) {
        console.error('Error parsing response data as JSON', e);
      }
    }
    return response;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Helper function for making consistent API calls
 * @param path - API endpoint path
 * @param options - Axios request options
 * @returns Promise with the API response
 */
export const makeApiRequest = async (path: string, options = {}) => {
  // Make sure we don't have duplicate /api prefixes
  const normalizedPath = path
    .replace(/^\/api\/api\//, '/api/')
    .replace(/^\/api\//, '/');
  const url = getApiUrl(normalizedPath);

  try {
    return await apiService({
      url,
      ...options,
    });
  } catch (error) {
    // Format the error using our utility function
    const formattedError = formatApiError(error);
    console.error(
      `API request failed: ${formattedError.message}`,
      formattedError
    );
    return Promise.reject(formattedError);
  }
};

export default apiService;
