'use client';

import Link from 'next/link';
import { useEffect, useState } from 'react';
import {
  Activity,
  AlertTriangle,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';

import {
  fetchStocksVolatilityData,
  StockVolatilityData,
  VolatilityApiResponse,
} from '__api__/volatilityApi';

import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../ui/card';
import { Skeleton } from '../../ui/skeleton';

interface MarketVolatilityWidgetProps {
  className?: string;
}

export function MarketVolatilityWidget({
  className,
}: MarketVolatilityWidgetProps) {
  const [volatilityData, setVolatilityData] = useState<StockVolatilityData[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const response: VolatilityApiResponse =
          await fetchStocksVolatilityData();
        setVolatilityData(response.results.slice(0, 10)); // Top 10 for widget
      } catch (err) {
        setError('Failed to load volatility data');
        console.error('Error fetching volatility data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const averageIV =
    volatilityData.length > 0
      ? volatilityData.reduce((sum, item) => sum + item.iv_current, 0) /
        volatilityData.length
      : 0;

  const highIVStocks = volatilityData
    .filter((stock) => stock.iv_1y_percentile > 75)
    .slice(0, 3);

  const lowIVStocks = volatilityData
    .filter((stock) => stock.iv_1y_percentile < 25)
    .slice(0, 3);

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <Activity className='h-5 w-5' />
            Market Volatility
          </CardTitle>
          <CardDescription>
            Current volatility levels and opportunities
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className='space-y-4'>
            <Skeleton className='h-8 w-full' />
            <Skeleton className='h-6 w-3/4' />
            <Skeleton className='h-6 w-1/2' />
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <AlertTriangle className='h-5 w-5 text-destructive' />
            Market Volatility
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className='text-sm text-muted-foreground'>{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className='flex items-center gap-2'>
          <Activity className='h-5 w-5 text-finance-secondary-400' />
          Market Volatility
        </CardTitle>
        <CardDescription>
          Current volatility levels and opportunities
        </CardDescription>
      </CardHeader>
      <CardContent className='space-y-4'>
        {/* Average IV */}
        <div className='flex items-center justify-between'>
          <span className='text-sm font-medium'>Market Average IV</span>
          <span className='text-lg font-bold'>{averageIV.toFixed(1)}%</span>
        </div>

        {/* High IV Opportunities */}
        <div>
          <h4 className='text-sm font-medium mb-2 flex items-center gap-1'>
            <TrendingUp className='h-4 w-4 text-red-500' />
            High IV Opportunities
          </h4>
          <div className='space-y-1'>
            {highIVStocks.map((stock) => (
              <div
                key={stock.symbol}
                className='flex items-center justify-between text-sm'
              >
                <span className='font-medium'>{stock.symbol}</span>
                <div className='flex items-center gap-2'>
                  <span>{stock.iv_current.toFixed(1)}%</span>
                  <Badge variant='destructive' className='text-xs'>
                    {stock.iv_1y_percentile.toFixed(0)}th
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Low IV Opportunities */}
        <div>
          <h4 className='text-sm font-medium mb-2 flex items-center gap-1'>
            <TrendingDown className='h-4 w-4 text-green-500' />
            Low IV Opportunities
          </h4>
          <div className='space-y-1'>
            {lowIVStocks.map((stock) => (
              <div
                key={stock.symbol}
                className='flex items-center justify-between text-sm'
              >
                <span className='font-medium'>{stock.symbol}</span>
                <div className='flex items-center gap-2'>
                  <span>{stock.iv_current.toFixed(1)}%</span>
                  <Badge variant='outline' className='text-xs'>
                    {stock.iv_1y_percentile.toFixed(0)}th
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Button */}
        <Link href='/volatility'>
          <Button variant='outline' className='w-full'>
            View Full Analysis
          </Button>
        </Link>
      </CardContent>
    </Card>
  );
}
