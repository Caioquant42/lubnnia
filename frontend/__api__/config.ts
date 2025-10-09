/**
 * API Configuration 
 * Central configuration file for API communication between frontend and backend
 */

// API Base URL - The main entry point for all API requests
// In development, use relative URL to leverage Next.js proxy
// In production, use the actual backend URL
export const apiBaseUrl = process.env.NODE_ENV === 'development' 
  ? '' // Use relative URL in development (Next.js will proxy to backend)
  : process.env.NEXT_PUBLIC_API_URL || 'https://zommaquant.com.br';

// Default headers for API requests
export const defaultHeaders = {
  'Content-Type': 'application/json',
  'Accept': 'application/json',
};

// Request timeout in milliseconds
export const requestTimeout = 30000;

// Custom error messages
export const errorMessages = {
  default: 'Ocorreu um erro ao processar sua solicitação',
  network: 'Erro de conexão. Verifique sua internet e tente novamente',
  timeout: 'A solicitação excedeu o tempo limite',
  notFound: 'O recurso solicitado não foi encontrado',
  serverError: 'Erro no servidor. Por favor tente novamente mais tarde',
  cors: 'Erro de CORS: Verifique a configuração do servidor'
};

// API endpoints path configuration
// These paths must match the backend routes defined in routes.py
export const apiPaths = {
  rrg: '/rrg',
  brRecommendations: '/br-recommendations',
  screenerRsi: '/screener-rsi',
  volatilitySurface: '/volatility-surface',
  collar: '/collar',
  coveredCall: '/covered-call',
  pairsTrading: '/pairs-trading',
  ibovStocks: '/ibov-stocks',
  cumulativePerformance: '/cumulative-performance',
  fluxoDdm: '/fluxo-ddm',
  dividendCalendar: '/dividend-calendar',
};

// Construct full API endpoint URLs
// We don't add the '/api' prefix here because getApiUrl will add it
export const endpoints = Object.entries(apiPaths).reduce((acc, [key, path]) => {
  acc[key] = path;  // getApiUrl() will add the '/api' prefix when needed
  return acc;
}, {} as Record<string, string>);

// Development mode detection
export const isDevelopment = process.env.NODE_ENV === 'development';

// CORS Allowed origins - should match backend configuration in cors_middleware.py
export const allowedOrigins = ['http://localhost:3000', 'https://zommaquant.com.br'];

/**
 * Helper function to get the correct API URL
 * Ensures proper formatting and prevents duplicate '/api' prefixes
 * @param endpoint - The API endpoint path
 * @returns The complete API URL
 */
export function getApiUrl(endpoint: string): string {
  // Handle three cases:
  // 1. If endpoint starts with http:// or https://, it's already an absolute URL
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  
  // 2. Make sure we have exactly one "/api" prefix
  let cleanEndpoint = endpoint;
  
  // If endpoint doesn't start with /api, add it
  if (!endpoint.startsWith('/api')) {
    cleanEndpoint = `/api${endpoint}`;
  }
  
  // 3. Clean any duplicate /api/api/ patterns
  cleanEndpoint = cleanEndpoint.replace(/\/api\/api\//g, '/api/');
  
  // 4. Make sure it always starts with a slash
  if (!cleanEndpoint.startsWith('/')) {
    cleanEndpoint = `/${cleanEndpoint}`;
  }
  
  return `${apiBaseUrl}${cleanEndpoint}`;
}

/**
 * Helper function to handle API errors consistently
 * @param error - The error object from axios
 * @returns The user-friendly error message
 */
export function handleApiError(error: any): string {
  if (error.userMessage) {
    return error.userMessage;
  }
  
  if (error.response) {
    // Handle specific error codes
    if (error.response.status === 401) {
      return 'Acesso não autorizado';
    } else if (error.response.status === 404) {
      return errorMessages.notFound;
    } else if (error.response.status >= 500) {
      return errorMessages.serverError;
    }
  } else if (error.request) {
    // The request was made but no response was received
    // Check if this might be a CORS error
    if (error.message && (
        error.message.includes('Network Error') || 
        error.message.includes('CORS') || 
        error.message.includes('Origin'))
    ) {
      return errorMessages.cors;
    }
    
    // Check for timeout
    if (error.message && error.message.includes('timeout')) {
      return errorMessages.timeout;
    }
    
    return errorMessages.network;
  }
  
  return errorMessages.default;
}