'use client';

import { X } from 'lucide-react';
import * as React from 'react';
import {
  Area,
  AreaChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { CollarStrategy } from '__api__/collarApi';

import { Button } from '../../ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '../../ui/card';

interface CollarStrategyDetailProps {
  strategy: CollarStrategy;
  onClose: () => void;
}

export function CollarStrategyDetail({
  strategy,
  onClose,
}: CollarStrategyDetailProps) {
  const [payoffData, setPayoffData] = React.useState<any[]>([]);
  const spotPrice = strategy.call.spot_price;

  // Check if premiums are valid (non-zero)
  const hasValidCallPremium = (strategy.call.close || 0) >= 0.01;
  const hasValidPutPremium = (strategy.put.close || 0) >= 0.01;
  const hasValidPremiums = hasValidCallPremium && hasValidPutPremium;

  React.useEffect(() => {
    // Generate optimized payoff data with adaptive step size
    const callStrike = strategy.strategy.call_strike;
    const putStrike = strategy.strategy.put_strike;
    const spotPrice = strategy.call.spot_price;

    // Calculate adaptive step size based on price range
    const priceRange =
      Math.max(callStrike, spotPrice) - Math.min(putStrike, spotPrice);
    let step = 0.01; // Default 1 cent step

    // Adjust step size based on price range for better performance
    if (priceRange > 20) {
      step = 0.1; // 10 cent steps for large ranges
    } else if (priceRange > 10) {
      step = 0.05; // 5 cent steps for medium ranges
    } else if (priceRange > 5) {
      step = 0.02; // 2 cent steps for smaller ranges
    }

    // Generate optimized data points with calculated step size
    const minX = Math.min(putStrike * 0.95, spotPrice * 0.85); // Lower buffer
    const maxX = Math.max(callStrike * 1.05, spotPrice * 1.15); // Upper buffer

    const detailedPoints = [];
    for (let price = minX; price <= maxX; price += step) {
      // Round to 2 decimal places to avoid floating point issues
      const roundedPrice = Math.round(price * 100) / 100;

      // Call payoff (sold call)
      const callPayoff =
        roundedPrice > callStrike
          ? callStrike - roundedPrice + strategy.call.close
          : strategy.call.close;

      // Put payoff (bought put)
      const putPayoff =
        roundedPrice < putStrike
          ? putStrike - roundedPrice - strategy.put.close
          : -strategy.put.close;

      // Total payoff
      const collarPayoff = roundedPrice - spotPrice + callPayoff + putPayoff;

      detailedPoints.push({
        price: roundedPrice,
        payoff: collarPayoff,
        negativePayoff: collarPayoff < 0 ? collarPayoff : null,
      });
    }

    // Sort all data points by price
    const enhancedData = detailedPoints.sort((a, b) => a.price - b.price);

    console.log(
      `Generated optimized payoff data with ${enhancedData.length} points (step: ${step})`
    );
    setPayoffData(enhancedData);
  }, [strategy]);
  // Format number to R$ currency format
  const formatCurrency = (value: number | undefined) => {
    return `R$ ${(value || 0).toFixed(2)}`;
  };

  // Format percent
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Format date from ISO string
  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  return (
    <div className='space-y-6'>
      <div className='flex items-center justify-between'>
        <div>
          <h2 className='text-2xl font-bold tracking-tight'>
            {strategy.strategy.parent_symbol} Collar Strategy
          </h2>
          <p className='text-muted-foreground'>
            Detalhes da estratégia para {strategy.strategy.call_symbol} e{' '}
            {strategy.strategy.put_symbol}
          </p>
        </div>
        <Button variant='outline' size='icon' onClick={onClose}>
          <X className='h-4 w-4' />
        </Button>
      </div>

      {/* Premium Validation Warning */}
      {!hasValidPremiums && (
        <div className='p-4 bg-amber-50 border border-amber-200 rounded-lg dark:bg-amber-900/20 dark:border-amber-800'>
          <div className='flex items-start space-x-3'>
            <div className='flex-shrink-0'>
              <svg
                className='h-5 w-5 text-amber-600 dark:text-amber-400'
                fill='currentColor'
                viewBox='0 0 20 20'
              >
                <path
                  fillRule='evenodd'
                  d='M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z'
                  clipRule='evenodd'
                />
              </svg>
            </div>
            <div className='flex-1'>
              <h3 className='text-sm font-medium text-amber-800 dark:text-amber-200'>
                Atenção: Prêmios Baixos
              </h3>
              <div className='mt-2 text-sm text-amber-700 dark:text-amber-300'>
                <p>
                  Esta estratégia possui prêmios muito baixos, o que pode não
                  ser atrativa para investimento:
                </p>
                <ul className='mt-1 list-disc list-inside space-y-1'>
                  {!hasValidCallPremium && (
                    <li>
                      Call: R$ {(strategy.call.close || 0).toFixed(2)} (muito
                      baixo)
                    </li>
                  )}
                  {!hasValidPutPremium && (
                    <li>
                      Put: R$ {(strategy.put.close || 0).toFixed(2)} (muito
                      baixo)
                    </li>
                  )}
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Strategy Overview Cards */}
      <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
        {/* Strategy Summary Card */}
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>
              Resumo da Estratégia
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='space-y-2'>
              <div className='flex justify-between'>
                <span className='text-sm text-muted-foreground'>
                  Preço Atual:
                </span>
                <span className='font-medium'>{formatCurrency(spotPrice)}</span>
              </div>
              <div className='flex justify-between'>
                <span className='text-sm text-muted-foreground'>
                  Relação Ganho/Risco:
                </span>
                <span className='font-medium'>
                  {strategy.strategy.gain_to_risk_ratio?.toFixed(2) || 'N/A'}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-sm text-muted-foreground'>
                  Pontuação Combinada:
                </span>
                <span className='font-medium'>
                  {strategy.strategy.combined_score?.toFixed(2) || 'N/A'}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Premium Information Card */}
        <Card>
          <CardHeader className='pb-2'>
            <CardTitle className='text-sm font-medium text-muted-foreground'>
              Informações de Prêmio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className='space-y-2'>
              <div className='flex justify-between'>
                <span className='text-sm text-muted-foreground'>Call:</span>
                <span
                  className={`font-medium ${hasValidCallPremium ? 'text-green-600' : 'text-amber-600'}`}
                >
                  {formatCurrency(strategy.call.close)}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-sm text-muted-foreground'>Put:</span>
                <span
                  className={`font-medium ${hasValidPutPremium ? 'text-green-600' : 'text-amber-600'}`}
                >
                  {formatCurrency(strategy.put.close)}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-sm text-muted-foreground'>Total:</span>
                <span className='font-medium'>
                  {formatCurrency(
                    (strategy.call.close || 0) + (strategy.put.close || 0)
                  )}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Call Option Card */}
        <Card>
          <CardHeader>
            <CardTitle>Opção de Compra</CardTitle>
            <CardDescription>{strategy.strategy.call_symbol}</CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Strike:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.strategy.call_strike)}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>
                Preço de Fechamento:
              </span>
              <span className='font-medium'>
                {formatCurrency(strategy.call.close)}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Moneyness:</span>
              <span className='font-medium'>{strategy.call.moneyness}</span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Valor Intrínseco:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.call.intrinsic_value || 0)}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Valor Extrínseco:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.call.extrinsic_value || 0)}
              </span>
            </div>{' '}
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Compra/Venda:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.call.bid || 0)} /{' '}
                {formatCurrency(strategy.call.ask || 0)}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Put Option Card */}
        <Card>
          <CardHeader>
            <CardTitle>Opção de Venda</CardTitle>
            <CardDescription>{strategy.strategy.put_symbol}</CardDescription>
          </CardHeader>
          <CardContent className='space-y-4'>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Strike:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.strategy.put_strike)}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>
                Preço de Fechamento:
              </span>
              <span className='font-medium'>
                {formatCurrency(strategy.put.close)}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Moneyness:</span>
              <span className='font-medium'>{strategy.put.moneyness}</span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Valor Intrínseco:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.put.intrinsic_value || 0)}
              </span>
            </div>
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Valor Extrínseco:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.put.extrinsic_value || 0)}
              </span>
            </div>{' '}
            <div className='flex justify-between'>
              <span className='text-muted-foreground'>Compra/Venda:</span>
              <span className='font-medium'>
                {formatCurrency(strategy.put.bid)} /{' '}
                {formatCurrency(strategy.put.ask)}
              </span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Payoff Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Gráfico de Payoff</CardTitle>
          <CardDescription>
            Lucro/prejuízo para diferentes níveis de preço da ação no vencimento
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className='h-[28rem] w-full'>
            <ResponsiveContainer width='100%' height='100%'>
              <AreaChart
                data={payoffData}
                margin={{ top: 40, right: 50, left: 30, bottom: 50 }}
              >
                <CartesianGrid strokeDasharray='3 3' opacity={0.2} />
                <XAxis
                  dataKey='price'
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => formatCurrency(value)}
                  label={{
                    value: 'Preço da Ação no Vencimento',
                    position: 'insideBottom',
                    offset: -10,
                  }}
                />
                <YAxis
                  tickFormatter={(value) => formatCurrency(value)}
                  label={{
                    value: 'Lucro/Prejuízo',
                    angle: -90,
                    position: 'insideLeft',
                    offset: 0,
                  }}
                />
                <Tooltip
                  formatter={(value: any) => [
                    formatCurrency(value),
                    'Lucro/Prejuízo',
                  ]}
                  labelFormatter={(label) =>
                    `Preço da Ação: ${formatCurrency(label)}`
                  }
                />
                <ReferenceLine y={0} stroke='#666' strokeDasharray='3 3' />
                <ReferenceLine
                  x={spotPrice}
                  stroke='#FF8C00'
                  strokeDasharray='3 3'
                  label={{
                    value: 'Price',
                    position: 'top',
                    fill: '#FF8C00',
                    offset: 20,
                  }}
                />
                <ReferenceLine
                  x={strategy.strategy.call_strike}
                  stroke='#00CED1'
                  strokeDasharray='3 3'
                  label={{
                    value: 'Strike Call',
                    position: 'top',
                    fill: '#00CED1',
                    offset: 20,
                  }}
                />
                <ReferenceLine
                  x={strategy.strategy.put_strike}
                  stroke='#BA55D3'
                  strokeDasharray='3 3'
                  label={{
                    value: 'Strike Put',
                    position: 'top',
                    fill: '#BA55D3',
                    offset: 20,
                  }}
                />
                {/* Replace single Area with two Areas for profit/loss distinction */}
                <defs>
                  <linearGradient
                    id='profitGradient'
                    x1='0'
                    y1='0'
                    x2='0'
                    y2='1'
                  >
                    <stop offset='5%' stopColor='#4CAF50' stopOpacity={0.8} />
                    <stop offset='95%' stopColor='#4CAF50' stopOpacity={0.2} />
                  </linearGradient>
                  <linearGradient id='lossGradient' x1='0' y1='0' x2='0' y2='1'>
                    <stop offset='5%' stopColor='#FF5252' stopOpacity={0.8} />
                    <stop offset='95%' stopColor='#FF5252' stopOpacity={0.2} />
                  </linearGradient>
                </defs>

                {/* Area for profits (values >= 0) */}
                <Area
                  type='monotone'
                  dataKey='payoff'
                  stroke='#4CAF50'
                  fill='url(#profitGradient)'
                  activeDot={{ r: 8 }}
                  baseValue={0}
                  isAnimationActive={false}
                  connectNulls
                  fillOpacity={1}
                  stackId='1'
                />

                {/* Area for losses (values < 0) */}
                <Area
                  type='monotone'
                  dataKey='negativePayoff'
                  stroke='#FF5252'
                  fill='url(#lossGradient)'
                  activeDot={{ r: 8 }}
                  baseValue={0}
                  isAnimationActive={false}
                  connectNulls
                  fillOpacity={1}
                  stackId='2'
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Risk and Return Card */}
      <Card>
        <CardHeader>
          <CardTitle>Análise de Risco e Retorno</CardTitle>
          <CardDescription>
            Métricas financeiras para esta estratégia de collar
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
            <div className='space-y-2'>
              <h4 className='text-sm font-medium'>Métricas de Retorno</h4>
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>Ganho Máximo:</span>
                <span className='font-medium text-green-500'>
                  {formatCurrency(strategy.strategy.total_gain || 0)}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>Perda Máxima:</span>
                <span className='font-medium text-red-500'>
                  {formatCurrency(strategy.strategy.total_risk || 0)}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>
                  Relação Ganho/Risco:
                </span>
                <span className='font-medium'>
                  {strategy.strategy.gain_to_risk_ratio?.toFixed(2) || 'N/A'}
                </span>
              </div>
            </div>
            <div className='space-y-2'>
              <h4 className='text-sm font-medium'>Métricas de Proteção</h4>{' '}
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>
                  Nível de Proteção:
                </span>
                <span className='font-medium'>
                  {formatPercent(
                    strategy.strategy.intrinsic_protection
                      ? (strategy.put as any).protection || 0
                      : 0
                  )}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>Resultado PM:</span>
                <span className='font-medium'>
                  {formatCurrency(strategy.strategy.pm_result || 0)}
                </span>
              </div>
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>
                  Retorno Relativo CDI:
                </span>
                <span className='font-medium'>
                  {formatPercent(strategy.strategy.cdi_relative_return || 0)}
                </span>
              </div>
            </div>
            <div className='space-y-2'>
              <h4 className='text-sm font-medium'>Pontuações da Estratégia</h4>
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>
                  Pontuação Combinada:
                </span>
                <span className='font-medium'>
                  {strategy.strategy.combined_score?.toFixed(2) || 'N/A'}
                </span>
              </div>{' '}
              <div className='flex justify-between'>
                <span className='text-muted-foreground'>
                  Liquidez das Opções:
                </span>
                <span className='font-medium'>
                  {(strategy.call.volume || 0) > 10000 &&
                  (strategy.put.volume || 0) > 10000
                    ? 'Alta'
                    : (strategy.call.volume || 0) > 1000 &&
                        (strategy.put.volume || 0) > 1000
                      ? 'Média'
                      : 'Baixa'}
                </span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
