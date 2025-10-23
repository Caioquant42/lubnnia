import { ArrowDown, ArrowUp } from 'lucide-react';

import { cn } from '@/lib/utils';

import { Card, CardContent, CardHeader, CardTitle } from '../../ui/card';

type StatCardProps = {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  className?: string;
};

export function StatCard({
  title,
  value,
  icon,
  change,
  trend,
  className,
}: StatCardProps) {
  // Format value if it's a number
  const formattedValue =
    typeof value === 'number'
      ? value.toLocaleString(undefined, {
          style: value > 1000 ? 'currency' : undefined,
          currency: value > 1000 ? 'USD' : undefined,
          minimumFractionDigits: 2,
          maximumFractionDigits: 2,
        })
      : value;

  return (
    <Card className={cn('finance-card', className)}>
      <CardHeader className='flex flex-row items-center justify-between pb-2'>
        <CardTitle className='text-sm font-medium text-muted-foreground'>
          {title}
        </CardTitle>
        {icon && <div className='text-muted-foreground'>{icon}</div>}
      </CardHeader>
      <CardContent>
        <div className='text-2xl font-bold'>{formattedValue}</div>
        {(change !== undefined || trend !== undefined) && (
          <p
            className={cn(
              'mt-1 flex items-center text-xs',
              trend === 'up' || (change !== undefined && change > 0)
                ? 'text-finance-success-500'
                : trend === 'down' || (change !== undefined && change < 0)
                  ? 'text-finance-danger-500'
                  : 'text-muted-foreground'
            )}
          >
            {trend === 'up' || (change !== undefined && change > 0) ? (
              <ArrowUp className='mr-1 h-3 w-3' />
            ) : trend === 'down' || (change !== undefined && change < 0) ? (
              <ArrowDown className='mr-1 h-3 w-3' />
            ) : null}
            {change !== undefined && (
              <span>{Math.abs(change).toFixed(2)}%</span>
            )}
            {trend && !change && (
              <span>
                {trend === 'up'
                  ? 'Increase'
                  : trend === 'down'
                    ? 'Decrease'
                    : 'No change'}
              </span>
            )}
          </p>
        )}
      </CardContent>
    </Card>
  );
}
