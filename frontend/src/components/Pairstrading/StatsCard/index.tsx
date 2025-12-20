import { ArrowDown, ArrowUp, Minus } from 'lucide-react';

import { Card, CardContent } from '@/components/ui/card';

interface StatsCardProps {
  title: string;
  value: string;
  description: string;
  trend?: 'up' | 'down' | 'neutral';
}

export default function StatsCard({
  title,
  value,
  description,
  trend,
}: StatsCardProps) {
  return (
    <Card>
      <CardContent className='p-6'>
        <div className='flex items-center justify-between'>
          <div>
            <p className='text-sm font-medium text-muted-foreground'>{title}</p>
            <p className='text-2xl font-bold'>{value}</p>
          </div>
          {trend && (
            <div>
              {trend === 'up' && (
                <div className='h-8 w-8 rounded-full bg-green-100 flex items-center justify-center'>
                  <ArrowUp className='h-4 w-4 text-green-600' />
                </div>
              )}
              {trend === 'down' && (
                <div className='h-8 w-8 rounded-full bg-red-100 flex items-center justify-center'>
                  <ArrowDown className='h-4 w-4 text-red-600' />
                </div>
              )}
              {trend === 'neutral' && (
                <div className='h-8 w-8 rounded-full bg-gray-100 flex items-center justify-center'>
                  <Minus className='h-4 w-4 text-gray-600' />
                </div>
              )}
            </div>
          )}
        </div>
        <p className='text-xs text-muted-foreground mt-2'>{description}</p>
      </CardContent>
    </Card>
  );
}
