'use client';

import { ArrowDown, ArrowUp, MoreHorizontal } from 'lucide-react';
import { useState } from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { ChartDataSeries, ChartTimePeriod } from '@/@types';

import { cn } from '@/lib/utils';

import { Button } from '../../ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../ui/card';
import { Popover, PopoverContent, PopoverTrigger } from '../../ui/popover';

type ChartCardProps = {
  title: string;
  value: number;
  change: number;
  changePercent: number;
  description?: string;
  className?: string;
  initialSeries?: ChartDataSeries;
  initialTimePeriod?: ChartTimePeriod;
  startValue?: number;
  volatility?: number;
};

const TIME_PERIODS: ChartTimePeriod[] = [
  '1D',
  '1W',
  '1M',
  '3M',
  '6M',
  'YTD',
  '1Y',
  '5Y',
  'MAX',
];

export function ChartCard({
  title,
  value,
  change,
  changePercent,
  description,
  className,
  initialSeries,
  initialTimePeriod = '1M',
  startValue = 100,
  volatility = 0.02,
}: ChartCardProps) {
  const [activePeriod, setActivePeriod] =
    useState<ChartTimePeriod>(initialTimePeriod);
  const [series, setSeries] = useState<ChartDataSeries>(
    initialSeries || {
      name: title,
      data: [{ timestamp: startValue, value: volatility }],
    }
  );

  const handlePeriodChange = (period: ChartTimePeriod) => {
    setActivePeriod(period);
    // Generate new chart data for the selected period
    setSeries({
      name: title,
      data: [{ timestamp: startValue, value: volatility }],
    });
  };

  // Format date for tooltip
  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year:
        activePeriod !== '1D' && activePeriod !== '1W' ? 'numeric' : undefined,
    });
  };

  // Format time for tooltip (only for 1D view)
  const formatTime = (timestamp: number) => {
    if (activePeriod === '1D') {
      const date = new Date(timestamp);
      return date.toLocaleTimeString(undefined, {
        hour: '2-digit',
        minute: '2-digit',
      });
    }
    return '';
  };

  const customTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className='custom-tooltip bg-card p-2 rounded border shadow-sm'>
          <p className='text-xs font-medium'>{formatDate(data.timestamp)}</p>
          {activePeriod === '1D' && (
            <p className='text-xs text-muted-foreground'>
              {formatTime(data.timestamp)}
            </p>
          )}
          <p className='text-sm font-bold'>${data.value.toFixed(2)}</p>
        </div>
      );
    }
    return null;
  };

  const getChartColor = () => {
    return change >= 0 ? 'hsl(var(--chart-1))' : 'hsl(var(--chart-3))';
  };

  return (
    <Card className={cn('finance-card h-full', className)}>
      <CardHeader className='flex flex-row items-center justify-between pb-2 pt-4'>
        <div>
          <CardTitle className='text-base'>{title}</CardTitle>
          {description && <CardDescription>{description}</CardDescription>}
        </div>

        <div className='flex items-center'>
          <div className='mr-4 flex items-baseline'>
            <span className='text-xl font-bold'>${value.toLocaleString()}</span>
            <div
              className={cn(
                'ml-2 flex items-center text-xs font-medium',
                change >= 0
                  ? 'text-finance-success-500'
                  : 'text-finance-danger-500'
              )}
            >
              {change >= 0 ? (
                <ArrowUp className='mr-1 h-3 w-3' />
              ) : (
                <ArrowDown className='mr-1 h-3 w-3' />
              )}
              {Math.abs(changePercent).toFixed(2)}%
            </div>
          </div>

          <Popover>
            <PopoverTrigger asChild>
              <Button variant='ghost' size='sm' className='h-8 w-8 p-0'>
                <MoreHorizontal className='h-4 w-4' />
              </Button>
            </PopoverTrigger>
            <PopoverContent align='end' className='w-48'>
              <div className='grid gap-1'>
                <Button variant='ghost' size='sm' className='justify-start'>
                  View Details
                </Button>
                <Button variant='ghost' size='sm' className='justify-start'>
                  Add to Watchlist
                </Button>
                <Button variant='ghost' size='sm' className='justify-start'>
                  Export Data
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        </div>
      </CardHeader>

      <CardContent className='pb-4 pt-0'>
        <div className='h-[200px] w-full'>
          <ResponsiveContainer width='100%' height='100%'>
            <AreaChart
              data={series.data}
              margin={{
                top: 5,
                right: 0,
                left: 0,
                bottom: 5,
              }}
            >
              <defs>
                <linearGradient
                  id={`colorGradient-${title}`}
                  x1='0'
                  y1='0'
                  x2='0'
                  y2='1'
                >
                  <stop
                    offset='5%'
                    stopColor={getChartColor()}
                    stopOpacity={0.3}
                  />
                  <stop
                    offset='95%'
                    stopColor={getChartColor()}
                    stopOpacity={0}
                  />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray='3 3'
                vertical={false}
                strokeOpacity={0.2}
              />
              <XAxis
                dataKey='timestamp'
                tickFormatter={formatDate}
                tick={{ fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                minTickGap={30}
                stroke='#888888'
              />
              <YAxis
                domain={['auto', 'auto']}
                tickFormatter={(value) => `$${value}`}
                tick={{ fontSize: 10 }}
                axisLine={false}
                tickLine={false}
                width={40}
                stroke='#888888'
              />
              <Tooltip content={customTooltip} />
              <Area
                type='monotone'
                dataKey='value'
                stroke={getChartColor()}
                fill={`url(#colorGradient-${title})`}
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className='mt-3 flex flex-wrap gap-1'>
          {TIME_PERIODS.map((period) => (
            <Button
              key={period}
              variant={activePeriod === period ? 'secondary' : 'ghost'}
              size='sm'
              className={cn(
                'h-7 px-2 text-xs',
                activePeriod === period && 'bg-muted'
              )}
              onClick={() => handlePeriodChange(period)}
            >
              {period}
            </Button>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
