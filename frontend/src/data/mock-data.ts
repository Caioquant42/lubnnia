// Mock data for development and testing
export const mockMarketData = [
  {
    symbol: 'PETR4',
    name: 'Petrobras',
    price: 42.50,
    change: 1.25,
    changePercent: 3.02,
    volume: 12500000,
    marketCap: 280000000000,
    sector: 'Energy',
  },
  {
    symbol: 'VALE3',
    name: 'Vale',
    price: 68.90,
    change: -0.85,
    changePercent: -1.22,
    volume: 8900000,
    marketCap: 320000000000,
    sector: 'Materials',
  },
  {
    symbol: 'ITUB4',
    name: 'Itaú Unibanco',
    price: 35.20,
    change: 0.45,
    changePercent: 1.29,
    volume: 15600000,
    marketCap: 180000000000,
    sector: 'Financial',
  },
  {
    symbol: 'BBDC4',
    name: 'Bradesco',
    price: 28.75,
    change: -0.30,
    changePercent: -1.03,
    volume: 11200000,
    marketCap: 150000000000,
    sector: 'Financial',
  },
  {
    symbol: 'ABEV3',
    name: 'Ambev',
    price: 12.85,
    change: 0.15,
    changePercent: 1.18,
    volume: 7800000,
    marketCap: 200000000000,
    sector: 'Consumer Staples',
  },
];

export const mockPortfolioData = [
  {
    symbol: 'PETR4',
    name: 'Petrobras',
    shares: 1000,
    avgPrice: 40.25,
    currentPrice: 42.50,
    marketValue: 42500,
    unrealizedPnL: 2250,
    unrealizedPnLPercent: 5.59,
    weight: 25.5,
  },
  {
    symbol: 'VALE3',
    name: 'Vale',
    shares: 500,
    avgPrice: 70.00,
    currentPrice: 68.90,
    marketValue: 34450,
    unrealizedPnL: -550,
    unrealizedPnLPercent: -1.57,
    weight: 20.7,
  },
  {
    symbol: 'ITUB4',
    name: 'Itaú Unibanco',
    shares: 800,
    avgPrice: 34.50,
    currentPrice: 35.20,
    marketValue: 28160,
    unrealizedPnL: 560,
    unrealizedPnLPercent: 2.03,
    weight: 16.9,
  },
  {
    symbol: 'BBDC4',
    name: 'Bradesco',
    shares: 600,
    avgPrice: 29.20,
    currentPrice: 28.75,
    marketValue: 17250,
    unrealizedPnL: -270,
    unrealizedPnLPercent: -1.54,
    weight: 10.4,
  },
  {
    symbol: 'ABEV3',
    name: 'Ambev',
    shares: 1200,
    avgPrice: 12.50,
    currentPrice: 12.85,
    marketValue: 15420,
    unrealizedPnL: 420,
    unrealizedPnLPercent: 2.80,
    weight: 9.3,
  },
];

export const mockPerformanceData = [
  {
    date: '2024-01-01',
    portfolio: 100000,
    benchmark: 100000,
  },
  {
    date: '2024-01-02',
    portfolio: 101250,
    benchmark: 100500,
  },
  {
    date: '2024-01-03',
    portfolio: 102100,
    benchmark: 101200,
  },
  {
    date: '2024-01-04',
    portfolio: 101800,
    benchmark: 100800,
  },
  {
    date: '2024-01-05',
    portfolio: 103200,
    benchmark: 102100,
  },
];

export const mockPairsTradingData = [
  {
    pair: 'PETR4/VALE3',
    cointegrated: true,
    p_value: 0.0234,
    beta: 0.85,
    half_life: 12.5,
    current_zscore: -1.8,
    recent_signals: [
      {
        signal_type: 'buy',
        signal_date: '2024-01-15',
        current_zscore: -2.1,
      },
      {
        signal_type: 'sell',
        signal_date: '2024-01-10',
        current_zscore: 2.3,
      },
    ],
  },
  {
    pair: 'ITUB4/BBDC4',
    cointegrated: true,
    p_value: 0.0156,
    beta: 1.12,
    half_life: 8.3,
    current_zscore: 1.2,
    recent_signals: [
      {
        signal_type: 'sell',
        signal_date: '2024-01-14',
        current_zscore: 1.8,
      },
    ],
  },
];

export const mockVolatilityData = [
  {
    symbol: 'PETR4',
    name: 'Petrobras',
    current_iv: 0.35,
    historical_iv: 0.28,
    iv_percentile: 85,
    iv_rank: 78,
    skew: -0.15,
    term_structure: 'normal',
  },
  {
    symbol: 'VALE3',
    name: 'Vale',
    current_iv: 0.42,
    historical_iv: 0.38,
    iv_percentile: 92,
    iv_rank: 88,
    skew: 0.08,
    term_structure: 'inverted',
  },
];

export const mockRecommendationsData = [
  {
    symbol: 'PETR4',
    name: 'Petrobras',
    recommendation: 'BUY',
    target_price: 45.00,
    current_price: 42.50,
    upside: 5.88,
    analyst: 'Quant Team',
    date: '2024-01-15',
    reasoning: 'Strong fundamentals and positive oil price outlook',
  },
  {
    symbol: 'VALE3',
    name: 'Vale',
    recommendation: 'HOLD',
    target_price: 70.00,
    current_price: 68.90,
    upside: 1.60,
    analyst: 'Quant Team',
    date: '2024-01-15',
    reasoning: 'Mixed signals from commodity markets',
  },
];

export const mockRetirementData = {
  currentAge: 35,
  retirementAge: 65,
  currentSavings: 500000,
  monthlyContribution: 5000,
  expectedReturn: 0.08,
  inflationRate: 0.03,
  lifeExpectancy: 85,
  monthlyExpenses: 15000,
};

export const mockDividendData = [
  {
    symbol: 'PETR4',
    name: 'Petrobras',
    ex_date: '2024-02-15',
    payment_date: '2024-03-15',
    amount: 0.85,
    yield: 2.0,
    frequency: 'quarterly',
  },
  {
    symbol: 'VALE3',
    name: 'Vale',
    ex_date: '2024-03-20',
    payment_date: '2024-04-20',
    amount: 1.20,
    yield: 1.7,
    frequency: 'quarterly',
  },
];

// Additional exports for compatibility
export const assetsData = mockMarketData;
export const marketIndicesData = [
  {
    id: 'ibov',
    symbol: 'IBOV',
    name: 'Ibovespa',
    price: 125000,
    change: 1250,
    changePercent: 1.01,
    volume: 0,
    marketCap: 0,
    sector: 'Index',
    value: 125000,
  },
  {
    id: 'ifix',
    symbol: 'IFIX',
    name: 'IFIX',
    price: 3200,
    change: -15,
    changePercent: -0.47,
    volume: 0,
    marketCap: 0,
    sector: 'Index',
    value: 3200,
  },
];
export const portfolioData = mockPortfolioData;
