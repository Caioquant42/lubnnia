/**
 * Screener API Service
 * Provides stock screening functionality based on RSI indicators
 * across multiple timeframes (15m, 60m, 1d, 1wk)
 */
import apiService from './apiService';

export interface RSIDataItem {
  Datetime: string;
  Symbol: string;
  AdjClose: number;
  RSI: number;
}

export interface RSITimeframeData {
  overbought: RSIDataItem[];
  oversold: RSIDataItem[];
}

export interface RSIScreenerResponse {
  stockdata_15m?: RSITimeframeData;
  stockdata_60m?: RSITimeframeData;
  stockdata_1d?: RSITimeframeData;
  stockdata_1wk?: RSITimeframeData;
  [key: string]: RSITimeframeData | undefined;
}

// Mock data to use when the API is not available
const mockRSIData: RSIScreenerResponse = {
  stockdata_15m: {
    overbought: [
      {
        Datetime: "2025-05-02 19:45:00",
        Symbol: "PETR3",
        AdjClose: 32.959999084472656,
        RSI: 83.58204706297647
      },
      {
        Datetime: "2025-05-02 19:45:00",
        Symbol: "PETR4",
        AdjClose: 30.790000915527344,
        RSI: 76.92312206744975
      }
    ],
    oversold: []
  },
  stockdata_60m: {
    overbought: [
      {
        Datetime: "2025-05-02 19:00:00",
        Symbol: "BBAS3",
        AdjClose: 28.940000534057617,
        RSI: 73.91297136708636
      }
    ],
    oversold: [
      {
        Datetime: "2025-05-02 19:00:00",
        Symbol: "CMIG4",
        AdjClose: 10.329999923706055,
        RSI: 28.46149388143759
      }
    ]
  },
  stockdata_1d: {
    overbought: [
      {
        Datetime: "2025-04-30 03:00:00",
        Symbol: "BBSE3",
        AdjClose: 42.77000045776367,
        RSI: 72.65623486601628
      },
      {
        Datetime: "2025-04-30 03:00:00",
        Symbol: "CMIG4",
        AdjClose: 10.949999809265137,
        RSI: 77.32556495491394
      }
    ],
    oversold: []
  },
  stockdata_1wk: {
    overbought: [
      {
        Datetime: "2025-04-28 03:00:00",
        Symbol: "BBSE3",
        AdjClose: 42.45000076293945,
        RSI: 71.66977341215127
      }
    ],
    oversold: []
  }
};

export const fetchRSIData = async (): Promise<RSIScreenerResponse> => {
  try {
    // First try to get data from the API
    const response = await apiService.get('/api/screener-rsi');
    return response.data;
  } catch (error) {
    console.error('Error fetching RSI data:', error);
    console.warn('Using mock RSI data as fallback');
    // Return mock data as fallback
    return mockRSIData;
  }
};

export const fetchRSIDataByTimeframe = async (timeframe: string): Promise<RSITimeframeData> => {
  try {
    const response = await apiService.get(`/api/screener-rsi?timeframe=${timeframe}`);
    const key = `stockdata_${timeframe}`;
    return response.data[key];
  } catch (error) {
    console.error(`Error fetching ${timeframe} RSI data:`, error);
    console.warn(`Using mock ${timeframe} RSI data as fallback`);
    // Return mock data for the specific timeframe as fallback
    const key = `stockdata_${timeframe}` as keyof RSIScreenerResponse;
    return mockRSIData[key] as RSITimeframeData;
  }
};

export const fetchRSIDataByCondition = async (
  timeframe: string, 
  condition: 'overbought' | 'oversold'
): Promise<RSIDataItem[]> => {
  try {
    const response = await apiService.get(
      `/api/screener-rsi?timeframe=${timeframe}&condition=${condition}`
    );
    const key = `stockdata_${timeframe}`;
    return response.data[key][condition];
  } catch (error) {
    console.error(`Error fetching ${timeframe} ${condition} RSI data:`, error);
    console.warn(`Using mock ${timeframe} ${condition} RSI data as fallback`);
    // Return mock data for the specific timeframe and condition as fallback
    const key = `stockdata_${timeframe}` as keyof RSIScreenerResponse;
    const timeframeData = mockRSIData[key];
    return timeframeData ? timeframeData[condition] : [];
  }
};