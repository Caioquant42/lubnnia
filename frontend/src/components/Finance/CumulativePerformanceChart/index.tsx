'use client';

import {
  AlertTriangle,
  BarChart3,
  CalendarDays,
  Percent,
  Target,
  TrendingUp,
} from 'lucide-react';
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import {
  CumulativePerformanceDataPoint,
  fetchCumulativePerformance,
  getCumulativePerformanceDateRange,
} from '__api__/cumulativePerformanceApi';

import { Alert, AlertDescription } from '../../ui/alert';
import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../ui/card';
import { Label } from '../../ui/label';
import { Skeleton } from '../../ui/skeleton';
import { Slider } from '../../ui/slider';
import { Switch } from '../../ui/switch';

interface CumulativePerformanceChartProps {
  className?: string;
  defaultAssets?: string[];
  showControls?: boolean;
}

// Asset colors for consistent visualization
const ASSET_COLORS = {
  CDI: '#10b981', // Green
  SP500: '#3b82f6', // Blue
  Gold: '#f59e0b', // Amber
  USDBRL: '#ef4444', // Red
  IBOV: '#8b5cf6', // Purple
} as const;

// Default assets to show
const DEFAULT_ASSETS = ['CDI', 'SP500', 'Gold', 'USDBRL', 'IBOV'];

// Time period presets for quick selection
const TIME_PERIODS = [
  { label: '3M', months: 3 },
  { label: '6M', months: 6 },
  { label: '1Y', months: 12 },
  { label: '2Y', months: 24 },
  { label: '3Y', months: 36 },
  { label: 'All', months: null },
];

export function CumulativePerformanceChart({
  className,
  defaultAssets = DEFAULT_ASSETS,
  showControls = true,
}: CumulativePerformanceChartProps) {
  // State management
  const [data, setData] = useState<CumulativePerformanceDataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<{ min: string; max: string }>({
    min: '',
    max: '',
  });
  const [availableAssets, setAvailableAssets] = useState<string[]>([]);
  // Chart controls
  const [selectedAssets, setSelectedAssets] = useState<string[]>(defaultAssets);
  const [showMetrics, setShowMetrics] = useState(true);
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [sliderRange, setSliderRange] = useState<[number, number]>([70, 100]);
  const [selectedPeriod, setSelectedPeriod] = useState<string>('1Y');

  // Performance metrics
  const [performanceMetrics, setPerformanceMetrics] = useState<any>(null);
  const [metadata, setMetadata] = useState<any>(null); // Calculate date range based on selected period
  const calculateDateRange = useCallback((period: string, maxDate: string) => {
    const endDate = new Date(maxDate);
    const startDate = new Date(maxDate);

    const periodConfig = TIME_PERIODS.find((p) => p.label === period);
    if (periodConfig && periodConfig.months) {
      startDate.setMonth(endDate.getMonth() - periodConfig.months);
    } else {
      // For "All", use the minimum available date
      return null; // Will be handled separately
    }

    return {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0],
    };
  }, []);
  // Calculate cumulative returns from price data
  const calculateCumulativeReturns = useCallback(
    (rawData: CumulativePerformanceDataPoint[], startDateForCalc: string) => {
      if (!rawData || rawData.length === 0) return [];

      // Find the start date index
      const startIndex = rawData.findIndex((d) => d.date >= startDateForCalc);
      if (startIndex === -1) return rawData;

      // Get start prices for each asset
      const startPrices: { [key: string]: number } = {};
      const startDataPoint = rawData[startIndex];

      // Assets that are already in percentage format (like CDI)
      const percentageAssets = ['CDI']; // CDI is already in percentage format

      Object.keys(startDataPoint).forEach((key) => {
        if (
          key !== 'date' &&
          typeof startDataPoint[key] === 'number' &&
          startDataPoint[key] !== null
        ) {
          startPrices[key] = startDataPoint[key] as number;
        }
      });

      // Calculate cumulative returns for each data point
      return rawData.slice(startIndex).map((dataPoint) => {
        const newDataPoint: CumulativePerformanceDataPoint = {
          date: dataPoint.date,
        };

        Object.keys(dataPoint).forEach((key) => {
          if (
            key !== 'date' &&
            typeof dataPoint[key] === 'number' &&
            dataPoint[key] !== null
          ) {
            const currentValue = dataPoint[key] as number;
            const startValue = startPrices[key];

            if (startValue && startValue !== 0) {
              if (percentageAssets.includes(key)) {
                // For assets already in percentage format (like CDI),
                // calculate the difference from start value
                newDataPoint[key] = currentValue - startValue;
              } else {
                // For nominal assets, calculate cumulative return: (current_price / start_price - 1) * 100
                newDataPoint[key] = (currentValue / startValue - 1) * 100;
              }
            } else {
              newDataPoint[key] = 0;
            }
          } else {
            newDataPoint[key] = dataPoint[key];
          }
        });

        return newDataPoint;
      });
    },
    []
  );
  // Load initial data and date range
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get available date range
        const dateRangeData = await getCumulativePerformanceDateRange();
        setDateRange({
          min: dateRangeData.min_date,
          max: dateRangeData.max_date,
        });
        setAvailableAssets(dateRangeData.available_assets);

        // Calculate initial date range based on selected period
        const calculatedRange = calculateDateRange(
          selectedPeriod,
          dateRangeData.max_date
        );
        const initialStartDate = calculatedRange
          ? calculatedRange.start
          : dateRangeData.min_date;
        const initialEndDate = calculatedRange
          ? calculatedRange.end
          : dateRangeData.max_date;

        setStartDate(initialStartDate);
        setEndDate(initialEndDate);

        // Load initial performance data - always get raw data for cumulative return calculation
        const performanceData = await fetchCumulativePerformance({
          start_date: dateRangeData.min_date, // Get full range for proper calculation
          end_date: initialEndDate,
          assets: selectedAssets,
          normalize: false, // Always get raw price data
          calculate_metrics: false, // We'll calculate our own metrics
        });

        // Calculate cumulative returns based on selected start date
        const cumulativeData = calculateCumulativeReturns(
          performanceData.data,
          initialStartDate
        );

        // Filter data to selected date range
        const filteredData = cumulativeData.filter(
          (d) => d.date >= initialStartDate && d.date <= initialEndDate
        );

        setData(filteredData);
        setMetadata(performanceData.metadata); // Calculate custom performance metrics for cumulative returns
        const customMetrics: any = {};
        if (filteredData.length > 0) {
          const percentageAssets = ['CDI']; // CDI is already in percentage format

          selectedAssets.forEach((asset) => {
            const assetData = filteredData
              .map((d) => d[asset] as number)
              .filter((v) => v !== null && !isNaN(v));
            if (assetData.length > 0) {
              const returns = assetData.slice(1).map((value, index) => {
                const prevValue = assetData[index];
                if (percentageAssets.includes(asset)) {
                  // For CDI (already in %), calculate daily change directly
                  return value - prevValue;
                } else {
                  // For other assets, calculate percentage change from cumulative returns
                  return prevValue !== 0
                    ? ((value - prevValue) / (100 + prevValue)) * 100
                    : 0;
                }
              });

              const totalReturn = assetData[assetData.length - 1];
              const volatility =
                returns.length > 1
                  ? Math.sqrt(
                      returns.reduce(
                        (sum, r) =>
                          sum +
                          (r -
                            returns.reduce((a, b) => a + b, 0) /
                              returns.length) **
                            2,
                        0
                      ) /
                        (returns.length - 1)
                    )
                  : 0;

              // Calculate max drawdown
              let maxDrawdown = 0;
              let peak = assetData[0];
              for (const value of assetData) {
                if (value > peak) peak = value;
                const drawdown = Math.abs(peak - value); // Use absolute difference for percentage assets
                if (drawdown > maxDrawdown) maxDrawdown = drawdown;
              }

              customMetrics[asset] = {
                total_return: totalReturn,
                volatility: volatility * Math.sqrt(252), // Annualized
                min_value: Math.min(...assetData),
                max_value: Math.max(...assetData),
                current_value: assetData[assetData.length - 1],
                sharpeRatio:
                  volatility !== 0
                    ? totalReturn / (volatility * Math.sqrt(252))
                    : 0,
                maxDrawdown: maxDrawdown,
              };
            }
          });
        }

        setPerformanceMetrics(customMetrics);
      } catch (err) {
        console.error('Error loading cumulative performance data:', err);
        setError('Failed to load cumulative performance data');
      } finally {
        setLoading(false);
      }
    };
    loadInitialData();
  }, [selectedPeriod, calculateDateRange, calculateCumulativeReturns]);

  // Update data when controls change
  useEffect(() => {
    if (!dateRange.min || !dateRange.max || !startDate || !endDate) return;

    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Always fetch raw data (normalize=false) and calculate cumulative returns on frontend
        const performanceData = await fetchCumulativePerformance({
          start_date: dateRange.min, // Fetch full range to calculate cumulative returns properly
          end_date: endDate,
          assets: selectedAssets,
          normalize: false, // Always get raw price data
          calculate_metrics: false, // We'll calculate our own metrics
        });

        // Calculate cumulative returns based on selected start date
        const cumulativeData = calculateCumulativeReturns(
          performanceData.data,
          startDate
        );

        // Filter data to selected date range
        const filteredData = cumulativeData.filter(
          (d) => d.date >= startDate && d.date <= endDate
        );

        setData(filteredData);
        setMetadata(performanceData.metadata);
        // Calculate custom performance metrics for cumulative returns
        const customMetrics: any = {};
        if (filteredData.length > 0) {
          const percentageAssets = ['CDI']; // CDI is already in percentage format

          selectedAssets.forEach((asset) => {
            const assetData = filteredData
              .map((d) => d[asset] as number)
              .filter((v) => v !== null && !isNaN(v));
            if (assetData.length > 0) {
              const returns = assetData.slice(1).map((value, index) => {
                const prevValue = assetData[index];
                if (percentageAssets.includes(asset)) {
                  // For CDI (already in %), calculate daily change directly
                  return value - prevValue;
                } else {
                  // For other assets, calculate percentage change from cumulative returns
                  return prevValue !== 0
                    ? ((value - prevValue) / (100 + prevValue)) * 100
                    : 0;
                }
              });

              const totalReturn = assetData[assetData.length - 1];
              const volatility =
                returns.length > 1
                  ? Math.sqrt(
                      returns.reduce(
                        (sum, r) =>
                          sum +
                          (r -
                            returns.reduce((a, b) => a + b, 0) /
                              returns.length) **
                            2,
                        0
                      ) /
                        (returns.length - 1)
                    )
                  : 0;

              // Calculate max drawdown
              let maxDrawdown = 0;
              let peak = assetData[0];
              for (const value of assetData) {
                if (value > peak) peak = value;
                const drawdown = Math.abs(peak - value); // Use absolute difference for percentage assets
                if (drawdown > maxDrawdown) maxDrawdown = drawdown;
              }

              customMetrics[asset] = {
                total_return: totalReturn,
                volatility: volatility * Math.sqrt(252), // Annualized
                min_value: Math.min(...assetData),
                max_value: Math.max(...assetData),
                current_value: assetData[assetData.length - 1],
                sharpeRatio:
                  volatility !== 0
                    ? totalReturn / (volatility * Math.sqrt(252))
                    : 0,
                maxDrawdown: maxDrawdown,
              };
            }
          });
        }

        setPerformanceMetrics(customMetrics);
      } catch (err) {
        console.error('Error updating cumulative performance data:', err);
        setError('Failed to update data');
      } finally {
        setLoading(false);
      }
    };

    const timeoutId = setTimeout(loadData, 300); // Debounce API calls
    return () => clearTimeout(timeoutId);
  }, [
    selectedAssets,
    showMetrics,
    startDate,
    endDate,
    dateRange.min,
    calculateCumulativeReturns,
  ]); // Handle period selection
  const handlePeriodChange = useCallback(
    (period: string) => {
      setSelectedPeriod(period);

      if (!dateRange.max) return;

      const calculatedRange = calculateDateRange(period, dateRange.max);
      if (calculatedRange) {
        setStartDate(calculatedRange.start);
        setEndDate(calculatedRange.end);

        // Update slider to match the selected period
        const minTime = new Date(dateRange.min).getTime();
        const maxTime = new Date(dateRange.max).getTime();
        const startTime = new Date(calculatedRange.start).getTime();
        const endTime = new Date(calculatedRange.end).getTime();
        const totalRange = maxTime - minTime;

        const startPercent = ((startTime - minTime) / totalRange) * 100;
        const endPercent = ((endTime - minTime) / totalRange) * 100;

        setSliderRange([Math.max(0, startPercent), Math.min(100, endPercent)]);
      } else {
        // "All" period selected
        setStartDate(dateRange.min);
        setEndDate(dateRange.max);
        setSliderRange([0, 100]);
      }
    },
    [dateRange, calculateDateRange]
  );

  // Helper function to adjust date range by percentage
  const adjustDateRange = useCallback(
    (startPercent: number, endPercent: number) => {
      if (!dateRange.min || !dateRange.max) return;

      const minTime = new Date(dateRange.min).getTime();
      const maxTime = new Date(dateRange.max).getTime();
      const totalRange = maxTime - minTime;

      const newStartPercent = Math.max(0, Math.min(100, startPercent));
      const newEndPercent = Math.max(0, Math.min(100, endPercent));

      // Ensure start is always before end
      const finalStartPercent = Math.min(newStartPercent, newEndPercent - 1);
      const finalEndPercent = Math.max(newEndPercent, newStartPercent + 1);

      setSliderRange([finalStartPercent, finalEndPercent]);
    },
    [dateRange]
  );

  // Quick date range shortcuts
  const quickRangeShortcuts = useMemo(
    () => [
      {
        label: 'Last 30D',
        action: () =>
          adjustDateRange(
            Math.max(
              0,
              sliderRange[1] -
                (30 /
                  ((new Date(dateRange.max).getTime() -
                    new Date(dateRange.min).getTime()) /
                    (1000 * 60 * 60 * 24))) *
                  100
            ),
            sliderRange[1]
          ),
      },
      {
        label: 'Last 90D',
        action: () =>
          adjustDateRange(
            Math.max(
              0,
              sliderRange[1] -
                (90 /
                  ((new Date(dateRange.max).getTime() -
                    new Date(dateRange.min).getTime()) /
                    (1000 * 60 * 60 * 24))) *
                  100
            ),
            sliderRange[1]
          ),
      },
      {
        label: 'YTD',
        action: () => {
          const currentYear = new Date().getFullYear();
          const yearStart = new Date(currentYear, 0, 1);
          const minTime = new Date(dateRange.min).getTime();
          const maxTime = new Date(dateRange.max).getTime();
          const totalRange = maxTime - minTime;
          const yearStartPercent = Math.max(
            0,
            ((yearStart.getTime() - minTime) / totalRange) * 100
          );
          adjustDateRange(yearStartPercent, 100);
        },
      },
      { label: 'Reset', action: () => setSliderRange([0, 100]) },
    ],
    [adjustDateRange, sliderRange, dateRange]
  );
  // Convert date range slider to actual dates
  useEffect(() => {
    if (!dateRange.min || !dateRange.max) return;

    const minTime = new Date(dateRange.min).getTime();
    const maxTime = new Date(dateRange.max).getTime();
    const totalRange = maxTime - minTime;

    const startTime = minTime + (totalRange * sliderRange[0]) / 100;
    const endTime = minTime + (totalRange * sliderRange[1]) / 100;

    const newStartDate = new Date(startTime).toISOString().split('T')[0];
    const newEndDate = new Date(endTime).toISOString().split('T')[0];

    // Only update if dates actually changed to prevent infinite loops
    if (newStartDate !== startDate || newEndDate !== endDate) {
      setStartDate(newStartDate);
      setEndDate(newEndDate);

      // Set to custom only if user manually moved the slider (not from period selection)
      if (selectedPeriod !== 'Custom') {
        // Check if the current slider position matches the selected period
        const periodRange = calculateDateRange(selectedPeriod, dateRange.max);
        if (periodRange) {
          const expectedStartTime = new Date(periodRange.start).getTime();
          const expectedEndTime = new Date(periodRange.end).getTime();
          const expectedStartPercent =
            ((expectedStartTime - minTime) / totalRange) * 100;
          const expectedEndPercent =
            ((expectedEndTime - minTime) / totalRange) * 100;

          // If slider moved away from expected period position, set to custom
          if (
            Math.abs(sliderRange[0] - expectedStartPercent) > 1 ||
            Math.abs(sliderRange[1] - expectedEndPercent) > 1
          ) {
            setSelectedPeriod('Custom');
          }
        } else if (sliderRange[0] !== 0 || sliderRange[1] !== 100) {
          // For "All" period, if not at full range, set to custom
          setSelectedPeriod('Custom');
        }
      }
    }
  }, [sliderRange, dateRange, selectedPeriod, calculateDateRange]);

  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };
  // Format value for tooltip
  const formatValue = (value: number) => {
    return `${value.toFixed(2)}%`;
  }; // Custom tooltip

  const CustomTooltip = useCallback(({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      // Calculate daily changes if possible
      const currentIndex = data.findIndex((d) => d.date === label);
      const previousData = currentIndex > 0 ? data[currentIndex - 1] : null;

      return (
        <div className='bg-white p-4 border border-gray-200 rounded-lg shadow-lg max-w-xs'>
          <p className='font-semibold text-gray-900 mb-3 border-b pb-2'>
            {formatDate(label)}
          </p>
          <div className='space-y-2'>
            {payload.map((entry: any, index: number) => {
              const currentValue = entry.value as number;
              const previousValue = previousData
                ? (previousData[entry.dataKey] as number)
                : null;
              const dailyChange =
                previousValue !== null ? currentValue - previousValue : 0;

              return (
                <div key={index} className='flex flex-col gap-1'>
                  <div className='flex items-center justify-between gap-3'>
                    <div className='flex items-center gap-2'>
                      <div
                        className='w-3 h-3 rounded-full'
                        style={{ backgroundColor: entry.color }}
                      />
                      <span className='text-sm font-medium'>{entry.name}</span>
                    </div>
                    <span className='text-sm font-semibold'>
                      {formatValue(currentValue)}
                    </span>
                  </div>
                  {previousData && previousValue && (
                    <div className='ml-5 text-xs'>
                      <span
                        className={`${dailyChange >= 0 ? 'text-green-600' : 'text-red-600'}`}
                      >
                        {dailyChange >= 0 ? '+' : ''}
                        {dailyChange.toFixed(2)}% daily
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      );
    }
    return null;
  }, []);
  // Toggle asset selection
  const toggleAsset = (asset: string) => {
    setSelectedAssets((prev) =>
      prev.includes(asset) ? prev.filter((a) => a !== asset) : [...prev, asset]
    );
  };

  // Calculate additional metrics
  const additionalMetrics = useMemo(() => {
    if (!performanceMetrics || !data.length) return null;

    const metrics: any = {};

    selectedAssets.forEach((asset) => {
      const assetData = data
        .map((d) => d[asset])
        .filter((v) => v !== null && v !== undefined) as number[];
      const assetMetrics = performanceMetrics[asset];

      if (assetData.length > 1 && assetMetrics) {
        // Calculate Sharpe ratio (simplified - assuming risk-free rate is CDI if available)
        const riskFreeReturn = performanceMetrics.CDI?.total_return || 0;
        const excessReturn = assetMetrics.total_return - riskFreeReturn;
        const sharpeRatio =
          assetMetrics.volatility > 0
            ? excessReturn / assetMetrics.volatility
            : 0;

        // Calculate maximum drawdown
        let maxDrawdown = 0;
        let peak = assetData[0];

        for (let i = 1; i < assetData.length; i++) {
          if (assetData[i] > peak) {
            peak = assetData[i];
          }
          const drawdown = (peak - assetData[i]) / peak;
          maxDrawdown = Math.max(maxDrawdown, drawdown);
        }

        metrics[asset] = {
          ...assetMetrics,
          sharpeRatio,
          maxDrawdown: maxDrawdown * 100,
        };
      }
    });

    return metrics;
  }, [performanceMetrics, data, selectedAssets]);

  if (loading && data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <BarChart3 className='h-5 w-5' />
            Cumulative Performance
          </CardTitle>
          <CardDescription>
            Historical performance comparison across asset classes
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Skeleton className='h-[400px] w-full' />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <BarChart3 className='h-5 w-5' />
            Cumulative Performance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }
  return (
    <Card className={className}>
      <CardHeader>
        <div className='flex flex-col gap-4'>
          <div className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
            <div>
              <CardTitle className='flex items-center gap-2'>
                <BarChart3 className='h-5 w-5' />
                Cumulative Performance Analysis
              </CardTitle>{' '}
              <CardDescription>
                Cumulative return comparison across asset classes
                {startDate && endDate && (
                  <span className='block text-xs mt-1'>
                    {formatDate(startDate)} - {formatDate(endDate)} (Returns
                    from {formatDate(startDate)})
                  </span>
                )}
              </CardDescription>
            </div>
            {showControls && (
              <div className='flex items-center gap-3'>
                <div className='flex items-center space-x-2'>
                  <Switch
                    id='metrics'
                    checked={showMetrics}
                    onCheckedChange={setShowMetrics}
                  />
                  <Label htmlFor='metrics' className='text-sm'>
                    Metrics
                  </Label>
                </div>
              </div>
            )}
          </div>

          {showControls && (
            <div className='space-y-4'>
              {/* Time Period Selection */}
              <div>
                <Label className='text-sm font-medium mb-3 block'>
                  Time Period
                </Label>
                <div className='flex flex-wrap gap-2'>
                  {TIME_PERIODS.map((period) => (
                    <Button
                      key={period.label}
                      variant={
                        selectedPeriod === period.label ? 'default' : 'outline'
                      }
                      size='sm'
                      onClick={() => handlePeriodChange(period.label)}
                      className='h-8'
                    >
                      {period.label}
                    </Button>
                  ))}
                  {selectedPeriod === 'Custom' && (
                    <Badge
                      variant='secondary'
                      className='h-8 px-3 flex items-center'
                    >
                      Custom Range
                    </Badge>
                  )}
                </div>
              </div>
              {/* Asset Selection */}
              <div>
                <Label className='text-sm font-medium mb-3 block'>Assets</Label>
                <div className='flex flex-wrap gap-2'>
                  {availableAssets.map((asset) => (
                    <Badge
                      key={asset}
                      variant={
                        selectedAssets.includes(asset) ? 'default' : 'outline'
                      }
                      className='cursor-pointer hover:bg-gray-100 transition-colors h-8 px-3'
                      style={{
                        backgroundColor: selectedAssets.includes(asset)
                          ? ASSET_COLORS[asset as keyof typeof ASSET_COLORS] ||
                            '#6b7280'
                          : 'transparent',
                        borderColor:
                          ASSET_COLORS[asset as keyof typeof ASSET_COLORS] ||
                          '#6b7280',
                        color: selectedAssets.includes(asset)
                          ? 'white'
                          : 'inherit',
                      }}
                      onClick={() => toggleAsset(asset)}
                    >
                      {asset}
                    </Badge>
                  ))}
                </div>
              </div>{' '}
              {/* Fine-tune Date Range Slider */}
              <div>
                <Label className='text-sm font-medium mb-3 block items-center gap-2'>
                  <CalendarDays className='h-4 w-4' />
                  Custom Date Range
                  <span className='text-xs text-gray-500 font-normal'>
                    (Drag both handles to adjust start and end dates)
                  </span>
                </Label>

                <div className='space-y-3'>
                  {/* Date Range Display */}
                  <div className='flex items-center justify-between text-sm'>
                    <div className='flex flex-col'>
                      <span className='text-xs text-gray-500'>Start Date</span>
                      <span className='font-medium text-green-600'>
                        {formatDate(startDate)}
                      </span>
                    </div>
                    <div className='flex flex-col text-center'>
                      <span className='text-xs text-gray-500'>Duration</span>
                      <span className='font-medium text-blue-600'>
                        {startDate &&
                          endDate &&
                          `${Math.round((new Date(endDate).getTime() - new Date(startDate).getTime()) / (1000 * 60 * 60 * 24))} days`}
                      </span>
                    </div>
                    <div className='flex flex-col text-right'>
                      <span className='text-xs text-gray-500'>End Date</span>
                      <span className='font-medium text-red-600'>
                        {formatDate(endDate)}
                      </span>
                    </div>
                  </div>

                  {/* Dual-handle Slider */}
                  <Slider
                    value={sliderRange}
                    onValueChange={(value) =>
                      setSliderRange(value as [number, number])
                    }
                    min={0}
                    max={100}
                    step={0.1}
                    className='w-full'
                  />

                  {/* Full Range Labels */}
                  <div className='flex justify-between text-xs text-gray-500'>
                    <span>{formatDate(dateRange.min)}</span>
                    <span className='text-center'>
                      Available Range:{' '}
                      {dateRange.min &&
                        dateRange.max &&
                        `${Math.round((new Date(dateRange.max).getTime() - new Date(dateRange.min).getTime()) / (1000 * 60 * 60 * 24))} days`}
                    </span>
                    <span>{formatDate(dateRange.max)}</span>
                  </div>
                  {/* Quick Reset Button and Shortcuts */}
                  <div className='flex justify-between items-center'>
                    <div className='flex gap-1'>
                      {quickRangeShortcuts.map((shortcut, index) => (
                        <Button
                          key={index}
                          variant='ghost'
                          size='sm'
                          onClick={shortcut.action}
                          className='text-xs h-6 px-2'
                        >
                          {shortcut.label}
                        </Button>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </CardHeader>{' '}
      <CardContent>
        {/* Performance Metrics */}
        {showMetrics && additionalMetrics && (
          <div className='mb-6'>
            <div className='flex items-center gap-2 mb-4'>
              <TrendingUp className='h-4 w-4' />
              <span className='font-medium text-sm'>Performance Metrics</span>
            </div>

            <div className='grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4'>
              {Object.entries(additionalMetrics).map(
                ([asset, metrics]: [string, any]) => (
                  <div
                    key={asset}
                    className='p-4 border rounded-lg bg-gray-50/50 hover:bg-gray-50 transition-colors'
                    style={{
                      borderColor:
                        ASSET_COLORS[asset as keyof typeof ASSET_COLORS] ||
                        '#6b7280',
                    }}
                  >
                    <div className='flex items-center gap-2 mb-3'>
                      <div
                        className='w-3 h-3 rounded-full'
                        style={{
                          backgroundColor:
                            ASSET_COLORS[asset as keyof typeof ASSET_COLORS] ||
                            '#6b7280',
                        }}
                      />
                      <span className='font-semibold text-sm'>{asset}</span>
                    </div>

                    <div className='space-y-2 text-xs'>
                      <div className='flex justify-between items-center'>
                        <div className='flex items-center gap-1'>
                          <Percent className='h-3 w-3 text-gray-500' />
                          <span>Total Return:</span>
                        </div>
                        <span
                          className={`font-medium ${metrics.total_return >= 0 ? 'text-green-600' : 'text-red-600'}`}
                        >
                          {metrics.total_return >= 0 ? '+' : ''}
                          {metrics.total_return.toFixed(1)}%
                        </span>
                      </div>

                      <div className='flex justify-between items-center'>
                        <div className='flex items-center gap-1'>
                          <AlertTriangle className='h-3 w-3 text-gray-500' />
                          <span>Volatility:</span>
                        </div>
                        <span className='font-medium text-gray-700'>
                          {metrics.volatility.toFixed(1)}%
                        </span>
                      </div>

                      <div className='flex justify-between items-center'>
                        <span>Sharpe Ratio:</span>
                        <span
                          className={`font-medium ${metrics.sharpeRatio >= 1 ? 'text-green-600' : metrics.sharpeRatio >= 0.5 ? 'text-yellow-600' : 'text-red-600'}`}
                        >
                          {metrics.sharpeRatio.toFixed(2)}
                        </span>
                      </div>

                      <div className='flex justify-between items-center'>
                        <span>Max Drawdown:</span>
                        <span className='font-medium text-red-600'>
                          -{metrics.maxDrawdown.toFixed(1)}%
                        </span>
                      </div>

                      <div className='flex justify-between items-center'>
                        <span>Current:</span>
                        <span className='font-medium'>
                          {metrics.current_value?.toFixed(2) || 'N/A'}
                        </span>
                      </div>

                      <div className='pt-1 border-t border-gray-200'>
                        <div className='flex justify-between items-center text-xs'>
                          <span>Range:</span>
                          <span className='font-medium'>
                            {metrics.min_value.toFixed(2)} -{' '}
                            {metrics.max_value.toFixed(2)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              )}
            </div>
          </div>
        )}{' '}
        {/* Chart */}
        <div className='relative'>
          <div className='h-[450px] w-full'>
            <ResponsiveContainer width='100%' height='100%'>
              <LineChart
                data={data}
                margin={{ top: 20, right: 30, left: 20, bottom: 20 }}
              >
                <CartesianGrid strokeDasharray='3 3' opacity={0.3} />
                <XAxis
                  dataKey='date'
                  tickFormatter={formatDate}
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  minTickGap={40}
                />{' '}
                <YAxis
                  tick={{ fontSize: 11 }}
                  tickLine={false}
                  axisLine={false}
                  tickFormatter={(value) => `${value.toFixed(1)}%`}
                  domain={['dataMin - 2', 'dataMax + 2']}
                />
                <Tooltip content={<CustomTooltip />} />
                <Legend wrapperStyle={{ paddingTop: '24px' }} iconType='line' />
                {selectedAssets.map((asset) => (
                  <Line
                    key={asset}
                    type='monotone'
                    dataKey={asset}
                    stroke={
                      ASSET_COLORS[asset as keyof typeof ASSET_COLORS] ||
                      '#6b7280'
                    }
                    strokeWidth={2.5}
                    dot={false}
                    activeDot={{
                      r: 5,
                      stroke:
                        ASSET_COLORS[asset as keyof typeof ASSET_COLORS] ||
                        '#6b7280',
                      strokeWidth: 2,
                      fill: 'white',
                    }}
                    connectNulls={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>

          {loading && (
            <div className='absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center rounded-lg'>
              <div className='text-sm text-gray-600 flex items-center gap-2'>
                <div className='w-4 h-4 border-2 border-gray-300 border-t-blue-500 rounded-full animate-spin'></div>
                Updating chart...
              </div>
            </div>
          )}
        </div>
        {/* Summary Statistics */}
        {selectedAssets.length > 1 && additionalMetrics && (
          <div className='mt-6 pt-4 border-t border-gray-200'>
            <div className='flex items-center gap-2 mb-3'>
              <Target className='h-4 w-4' />
              <span className='font-medium text-sm'>Comparison Summary</span>
            </div>
            <div className='grid grid-cols-2 md:grid-cols-4 gap-4 text-sm'>
              <div>
                <span className='text-gray-600'>Best Performer:</span>
                <div className='font-medium mt-1'>
                  {(() => {
                    const entries = Object.entries(additionalMetrics) as [
                      string,
                      any,
                    ][];
                    const best = entries.reduce((a, b) =>
                      a[1].total_return > b[1].total_return ? a : b
                    );
                    return (
                      <div className='flex items-center gap-2'>
                        <div
                          className='w-3 h-3 rounded-full'
                          style={{
                            backgroundColor:
                              ASSET_COLORS[
                                best[0] as keyof typeof ASSET_COLORS
                              ],
                          }}
                        />
                        {best[0]} ({best[1].total_return.toFixed(1)}%)
                      </div>
                    );
                  })()}
                </div>
              </div>

              <div>
                <span className='text-gray-600'>Lowest Volatility:</span>
                <div className='font-medium mt-1'>
                  {(() => {
                    const entries = Object.entries(additionalMetrics) as [
                      string,
                      any,
                    ][];
                    const safest = entries.reduce((a, b) =>
                      a[1].volatility < b[1].volatility ? a : b
                    );
                    return (
                      <div className='flex items-center gap-2'>
                        <div
                          className='w-3 h-3 rounded-full'
                          style={{
                            backgroundColor:
                              ASSET_COLORS[
                                safest[0] as keyof typeof ASSET_COLORS
                              ],
                          }}
                        />
                        {safest[0]} ({safest[1].volatility.toFixed(1)}%)
                      </div>
                    );
                  })()}
                </div>
              </div>

              <div>
                <span className='text-gray-600'>Best Sharpe:</span>
                <div className='font-medium mt-1'>
                  {(() => {
                    const entries = Object.entries(additionalMetrics) as [
                      string,
                      any,
                    ][];
                    const bestSharpe = entries.reduce((a, b) =>
                      a[1].sharpeRatio > b[1].sharpeRatio ? a : b
                    );
                    return (
                      <div className='flex items-center gap-2'>
                        <div
                          className='w-3 h-3 rounded-full'
                          style={{
                            backgroundColor:
                              ASSET_COLORS[
                                bestSharpe[0] as keyof typeof ASSET_COLORS
                              ],
                          }}
                        />
                        {bestSharpe[0]} ({bestSharpe[1].sharpeRatio.toFixed(2)})
                      </div>
                    );
                  })()}
                </div>
              </div>

              <div>
                <span className='text-gray-600'>Min Drawdown:</span>
                <div className='font-medium mt-1'>
                  {(() => {
                    const entries = Object.entries(additionalMetrics) as [
                      string,
                      any,
                    ][];
                    const minDrawdown = entries.reduce((a, b) =>
                      a[1].maxDrawdown < b[1].maxDrawdown ? a : b
                    );
                    return (
                      <div className='flex items-center gap-2'>
                        <div
                          className='w-3 h-3 rounded-full'
                          style={{
                            backgroundColor:
                              ASSET_COLORS[
                                minDrawdown[0] as keyof typeof ASSET_COLORS
                              ],
                          }}
                        />
                        {minDrawdown[0]} (-
                        {minDrawdown[1].maxDrawdown.toFixed(1)}%)
                      </div>
                    );
                  })()}
                </div>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
