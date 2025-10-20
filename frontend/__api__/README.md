# API Configuration and Usage

This folder contains the API configuration and services for the Zomma Quant frontend application. The API services are designed to communicate with the backend server located at `http://localhost:5000` in development mode, or the production URL specified in environment variables.

## Core Files

- `config.ts` - Central configuration for API communication
- `apiService.ts` - Base API service with Axios configuration
- `utils.ts` - Utility functions for API operations

## Specialized API Services

Each type of API has its own dedicated service file:
- `rrgApi.ts` - Relative Rotation Graph API
- `recommendationsApi.ts` - Stock recommendations API
- `screenerApi.ts` - Stock screener API
- `volatilityApi.ts` - Volatility surface API
- `collarApi.ts` - Collar strategy API
- `coveredcallApi.ts` - Covered call strategy API
- `pairstrading.ts` - Pairs trading API
- `cointegrationService.ts` - Cointegration analysis API
- `longshortService.ts` - Long-short strategy API

## Usage Example

```typescript
import { fetchRRGData } from './__api__/rrgApi';

// In a component or hook
async function loadRRGData() {
  try {
    const data = await fetchRRGData({ quadrant: 'leading', limit: 10 });
    // Process data...
  } catch (error) {
    console.error('Failed to load RRG data:', error.message);
  }
}
```

## Error Handling

The API services include consistent error handling using the `formatApiError` utility. All errors are formatted with user-friendly messages defined in `config.ts`.

## Configuration

The main configuration is in `config.ts`. Key settings include:

- `apiBaseUrl` - The base URL for all API requests
- `endpoints` - Object mapping endpoint names to paths
- `errorMessages` - User-friendly error messages

## CORS Configuration

The backend has CORS configured to allow requests from:
- `http://localhost:3000` (development)
- `https://zommaquant.com.br` (production)

## Adding a New API Service

To add a new API service:

1. Define the endpoint in `config.ts` under `apiPaths`
2. Create a new service file (e.g., `newFeatureApi.ts`)
3. Import `apiService` or `makeApiRequest` from `apiService.ts`
4. Define your API function with appropriate types and error handling
