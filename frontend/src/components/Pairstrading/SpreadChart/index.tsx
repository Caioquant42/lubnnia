'use client';

import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

interface SpreadChartProps {
  data: Array<{
    date: string;
    spread: number;
    zscore?: number;
    signal?: 'buy' | 'sell' | null;
  }>;
  title?: string;
  description?: string;
}

const SpreadChart: React.FC<SpreadChartProps> = ({
  data,
  title = 'Spread Evolution',
  description = 'Z-score and historical spread',
}) => {
  // Format date for the chart
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  // Return different colors for signal points
  const getSignalColor = (signal: 'buy' | 'sell' | null) => {
    if (!signal) return 'transparent';
    return signal === 'buy' ? '#4CAF50' : '#FF5252';
  };

  if (!data || data.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <Skeleton className='h-[300px] w-full' />
        </CardContent>
      </Card>
    );
  }

  // Filter data to get only signals
  const hasSignals = data.some((point) => point.signal);

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div className='h-[300px] w-full'>
          <ResponsiveContainer width='100%' height='100%'>
            <LineChart
              data={data}
              margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray='3 3' opacity={0.2} />
              <XAxis
                dataKey='date'
                tickFormatter={formatDate}
                minTickGap={30}
              />
              <YAxis yAxisId='left' />
              <YAxis yAxisId='right' orientation='right' />
              <Tooltip
                labelFormatter={(label) => `Date: ${formatDate(label)}`}
              />
              <Legend />
              <ReferenceLine y={0} stroke='#666' strokeDasharray='3 3' />

              {/* Z-score line */}
              <Line
                yAxisId='right'
                type='monotone'
                dataKey='zscore'
                name='Z-Score'
                stroke='#8884d8'
                dot={false}
                activeDot={{ r: 8 }}
              />

              {/* Spread line */}
              <Line
                yAxisId='left'
                type='monotone'
                dataKey='spread'
                name='Spread'
                stroke='#82ca9d'
                dot={false}
                activeDot={{ r: 8 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
};

export { SpreadChart };
