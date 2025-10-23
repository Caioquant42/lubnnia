'use client';

import { useCallback } from 'react';
import {
  Cell,
  Legend,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
} from 'recharts';
import { PortfolioPosition } from '@/@types';
import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';

type AllocationChartProps = {
  positions: PortfolioPosition[];
  className?: string;
};

export function AllocationChart({
  positions,
  className,
}: AllocationChartProps) {
  // Group small positions into "Other" category
  const threshold = 3; // Positions smaller than 3% will be grouped

  let chartData = [...positions]
    .sort((a, b) => b.allocation - a.allocation)
    .map((position) => ({
      name: position.symbol,
      value: position.allocation,
      color: `hsl(var(--chart-${Math.floor(Math.random() * 5) + 1}))`,
    }));

  // Find small positions
  const smallPositions = chartData.filter((item) => item.value < threshold);

  // If we have small positions, replace them with an "Other" category
  if (smallPositions.length > 1) {
    const otherValue = smallPositions.reduce(
      (sum, item) => sum + item.value,
      0
    );

    chartData = chartData
      .filter((item) => item.value >= threshold)
      .concat([
        {
          name: 'Other',
          value: otherValue,
          color: 'hsl(var(--muted-foreground))',
        },
      ]);
  }

  // Custom tooltip
  const CustomTooltip = useCallback(({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className='custom-tooltip bg-card p-2 rounded border shadow-sm'>
          <p className='text-sm font-medium'>{payload[0].name}</p>
          <p className='text-sm text-muted-foreground'>
            {payload[0].value.toFixed(2)}%
          </p>
        </div>
      );
    }
    return null;
  }, []);

  return (
    <Card className={className}>
      <CardHeader className='pb-2'>
        <CardTitle className='text-base'>Portfolio Allocation</CardTitle>
      </CardHeader>
      <CardContent>
        <div className='h-[300px]'>
          <ResponsiveContainer width='100%' height='100%'>
            <PieChart>
              <Pie
                data={chartData}
                cx='50%'
                cy='50%'
                labelLine={false}
                outerRadius={100}
                innerRadius={40}
                fill='#8884d8'
                dataKey='value'
                nameKey='name'
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
              <Legend
                layout='vertical'
                verticalAlign='middle'
                align='right'
                formatter={(value, entry: any, index) => (
                  <span className='text-xs'>
                    {value} ({chartData[index].value.toFixed(1)}%)
                  </span>
                )}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  );
}
