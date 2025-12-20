import { ArrowDown, ArrowUp, Minus } from 'lucide-react';

import {
  categorizeVolatility,
  getVolatilityStatusColor,
} from '__api__/volatilityApi';

import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

type VolatilityStatusCardProps = {
  title: string;
  symbol?: string;
  ratio: number;
  description?: string;
};

export function VolatilityStatusCard({
  title,
  symbol,
  ratio,
  description,
}: VolatilityStatusCardProps) {
  const category = categorizeVolatility(ratio);
  const colorClass = getVolatilityStatusColor(ratio);

  let indicatorIcon: any;
  if (ratio > 1.1) {
    indicatorIcon = <ArrowUp className='h-4 w-4 text-red-500' />;
  } else if (ratio < 0.9) {
    indicatorIcon = <ArrowDown className='h-4 w-4 text-blue-500' />;
  } else {
    indicatorIcon = <Minus className='h-4 w-4 text-yellow-500' />;
  }

  return (
    <Card>
      <CardHeader className='pb-2'>
        <CardTitle className='text-md flex items-center justify-between'>
          {title}
          {symbol && <Badge variant='outline'>{symbol}</Badge>}
        </CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className='flex items-center justify-between'>
          <div className='flex items-center space-x-2'>
            {indicatorIcon}
            <span className={`text-lg font-semibold text-${colorClass}`}>
              {category}
            </span>
          </div>
          <span className='text-lg font-bold'>{ratio.toFixed(2)}</span>
        </div>
      </CardContent>
    </Card>
  );
}
