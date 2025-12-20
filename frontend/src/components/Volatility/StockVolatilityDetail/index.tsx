import {
  AlertCircle,
  ArrowUpDown,
  BarChart,
  Info,
  LineChart,
  TrendingDown,
  TrendingUp,
} from 'lucide-react';

import {
  analyzeStockVolatility,
  StockVolatilityData,
} from '__api__/volatilityApi';

import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';

type StockVolatilityDetailProps = {
  stock: StockVolatilityData;
};

export function StockVolatilityDetail({ stock }: StockVolatilityDetailProps) {
  const { category, color, trend, volatilityCharacteristics } =
    analyzeStockVolatility(stock);

  // Get trend icon
  const getTrendIcon = () => {
    if (trend.includes('Uptrend')) {
      return <TrendingUp className='h-5 w-5 text-green-500' />;
    } else if (trend.includes('Downtrend')) {
      return <TrendingDown className='h-5 w-5 text-red-500' />;
    }
    return <ArrowUpDown className='h-5 w-5 text-yellow-500' />;
  };

  const formatPercentage = (value: number | undefined) => {
    if (value === undefined || isNaN(value)) return '-';
    return `${value.toFixed(1)}%`;
  };

  const formatNumber = (value: number | undefined, decimals: number = 2) => {
    if (value === undefined || isNaN(value)) return '-';
    return value.toFixed(decimals);
  };

  return (
    <Card className='w-full'>
      <CardHeader>
        <div className='flex items-center justify-between'>
          <div>
            <div className='flex items-center gap-2'>
              <CardTitle>{stock.symbol}</CardTitle>
              <Badge variant='outline'>{stock.sector || 'Desconhecido'}</Badge>
            </div>
            <CardDescription>{stock.name}</CardDescription>
          </div>
          <div className='text-right'>
            <div className='text-xl font-bold'>
              {formatNumber(stock.close, 2)}
            </div>
            <div
              className={`text-sm font-medium ${
                stock.variation > 0
                  ? 'text-green-500'
                  : stock.variation < 0
                    ? 'text-red-500'
                    : ''
              }`}
            >
              {stock.variation > 0 ? '+' : ''}
              {formatPercentage(stock.variation)}
            </div>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className='grid gap-6'>
          <div className='grid gap-4 md:grid-cols-2'>
            <div className='space-y-2'>
              <div className='font-semibold flex items-center gap-1.5'>
                <BarChart className='h-4 w-4' />
                Análise de Volatilidade
              </div>
              <div className='grid gap-1.5'>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>Razão IV/EWMA:</span>
                  <span className={`font-medium text-${color}`}>
                    {stock.iv_ewma_ratio?.toFixed(2) || '-'} ({category})
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>VI Atual:</span>
                  <span>{stock.iv_current?.toFixed(1) || '-'}</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>EWMA Atual:</span>
                  <span>{stock.ewma_current?.toFixed(1) || '-'}</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>
                    Rank de VI (1A):
                  </span>
                  <span>{stock.iv_1y_rank?.toFixed(1) || '-'}</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>
                    Percentil de VI (1A):
                  </span>
                  <span>{formatPercentage(stock.iv_1y_percentile)}</span>
                </div>
              </div>
            </div>

            <div className='space-y-2'>
              <div className='font-semibold flex items-center gap-1.5'>
                <LineChart className='h-4 w-4' />
                Estatísticas de Mercado
              </div>
              <div className='grid gap-1.5'>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>
                    Tendência de Preço:
                  </span>
                  <span className='flex items-center gap-1'>
                    {getTrendIcon()}
                    {trend}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>
                    Beta (Ibovespa):
                  </span>
                  <span>{formatNumber(stock.beta_ibov)}</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>
                    Correlação (Ibovespa):
                  </span>
                  <span>{formatNumber(stock.correl_ibov)}</span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>
                    Desvio Padrão (1A):
                  </span>
                  <span>
                    {formatPercentage(
                      stock.stdv_1y ? stock.stdv_1y * 100 : undefined
                    )}
                  </span>
                </div>
                <div className='flex justify-between'>
                  <span className='text-muted-foreground'>
                    Desvio Padrão (5D):
                  </span>
                  <span>
                    {formatPercentage(
                      stock.stdv_5d ? stock.stdv_5d * 100 : undefined
                    )}
                  </span>
                </div>
              </div>
            </div>
          </div>

          <Separator />

          <div>
            <div className='font-semibold flex items-center gap-1.5 mb-2'>
              <AlertCircle className='h-4 w-4' />
              Insights de Volatilidade
            </div>
            <ul className='space-y-1.5 text-sm'>
              {volatilityCharacteristics.length > 0 ? (
                volatilityCharacteristics.map((characteristic, i) => (
                  <li key={i} className='flex items-start gap-2'>
                    <Info className='h-4 w-4 mt-0.5 flex-shrink-0' />
                    <span>{characteristic}</span>
                  </li>
                ))
              ) : (
                <li className='flex items-start gap-2'>
                  <Info className='h-4 w-4 mt-0.5 flex-shrink-0' />
                  <span>
                    As métricas de volatilidade estão dentro dos ranges normais.
                  </span>
                </li>
              )}

              {stock.iv_ewma_ratio > 1.1 && (
                <li className='flex items-start gap-2'>
                  <AlertCircle className='h-4 w-4 mt-0.5 flex-shrink-0 text-orange-500' />
                  <span>
                    As opções estão relativamente caras comparadas à
                    volatilidade histórica.
                  </span>
                </li>
              )}

              {stock.iv_ewma_ratio < 0.9 && (
                <li className='flex items-start gap-2'>
                  <AlertCircle className='h-4 w-4 mt-0.5 flex-shrink-0 text-blue-500' />
                  <span>
                    As opções estão relativamente baratas comparadas à
                    volatilidade histórica.
                  </span>
                </li>
              )}

              <li className='flex items-start gap-2 mt-2'>
                <Info className='h-4 w-4 mt-0.5 flex-shrink-0' />
                <span className='text-muted-foreground'>
                  Retorno Histórico 1A:{' '}
                  {formatPercentage(
                    stock.semi_return_1y
                      ? stock.semi_return_1y * 100
                      : undefined
                  )}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
