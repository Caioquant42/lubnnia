'use client';

import * as React from 'react';
import { 
  Card, 
  CardContent, 
  CardDescription, 
  CardHeader, 
  CardTitle 
} from '@/components/ui/card';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
  ResponsiveContainer,
} from 'recharts';
import { CoveredCallOption } from '@/__api__/coveredcallApi';
import { Badge } from '@/components/ui/badge';

interface CoveredCallStrategyDetailProps {
  option: CoveredCallOption;
  onClose: () => void;
}

export default function CoveredCallStrategyDetail({ option, onClose }: CoveredCallStrategyDetailProps) {
  const [payoffData, setPayoffData] = React.useState<any[]>([]);
  const spotPrice = option.spot_price;
  const strikePrice = option.strike;
  const premium = option.bid || 0;

  // Check if premium is valid (non-zero)
  const hasValidPremium = premium >= 0.01;

  React.useEffect(() => {
    // Generate payoff data for a covered call
    const minPrice = spotPrice * 0.7;
    const maxPrice = spotPrice * 1.3;
    
    // Generate detailed data points
    const detailedPoints = [];
    const step = (maxPrice - minPrice) / 100;
    
    for (let price = minPrice; price <= maxPrice; price += step) {
      // Round to 2 decimal places to avoid floating point issues
      const roundedPrice = Math.round(price * 100) / 100;
      
      // Covered call payoff calculation:
      // If price at expiry > strikePrice, call is exercised (profit is capped)
      // If price at expiry <= strikePrice, call expires worthless (full downside exposure + premium)
      const payoff = roundedPrice > strikePrice
        ? strikePrice - spotPrice + premium // Capped profit
        : roundedPrice - spotPrice + premium; // Full downside risk + premium
      
      detailedPoints.push({
        price: roundedPrice,
        payoff: payoff,
        // Separate negative values for styling
        negativePayoff: payoff < 0 ? payoff : null,
        // Separate positive values for styling
        positivePayoff: payoff >= 0 ? payoff : null
      });
    }
    
    setPayoffData(detailedPoints);
  }, [option, spotPrice, strikePrice, premium]);

  // Format number to R$ currency format
  const formatCurrency = (value: number) => {
    return `R$ ${value.toFixed(2)}`;
  };

  // Format percent
  const formatPercent = (value: number | undefined) => {
    if (value === undefined || isNaN(value)) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  // Format date from ISO string
  const formatDate = (dateString?: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Calculate important values
  const breakEvenPrice = spotPrice - premium;
  const maxProfit = (strikePrice - spotPrice) + premium;
  const maxLoss = spotPrice - premium; // If stock goes to zero

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Estratégia de Call Coberto: {option.parent_symbol}
          </h1>
          <p className="text-muted-foreground">
            Detalhes da estratégia para {option.symbol} vencendo {formatDate(option.block_date)}
          </p>
        </div>
      </div>

      {/* Strategy Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Preço Atual</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(spotPrice)}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Preço Strike</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(strikePrice)}</div>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Prêmio</CardTitle>
          </CardHeader>
          <CardContent>
            {hasValidPremium ? (
              <div className="text-2xl font-bold">{formatCurrency(premium)}</div>
            ) : (
              <div className="text-lg text-amber-600 font-medium">
                Prêmio muito baixo
              </div>
            )}
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Retorno CDI</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatPercent(option.cdi_relative_return)}</div>
          </CardContent>
        </Card>
      </div>

      {/* Payoff Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Diagrama de Payoff</CardTitle>
          <CardDescription>
            Lucro/Prejuízo no vencimento baseado no preço da ação subjacente
          </CardDescription>
        </CardHeader>
        <CardContent>
          {!hasValidPremium && (
            <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-lg">
              <p className="text-amber-800 text-sm">
                ⚠️ Atenção: Esta estratégia tem um prêmio muito baixo, o que pode não ser atrativa para investimento.
              </p>
            </div>
          )}
          <div className="h-[400px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart
                data={payoffData}
                margin={{ top: 40, right: 50, left: 30, bottom: 50 }}
              >
                <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                <XAxis 
                  dataKey="price"
                  type="number"
                  scale="linear"
                  domain={['dataMin', 'dataMax']}
                  tickFormatter={(value) => `R$ ${value.toFixed(0)}`}
                  label={{ value: 'Preço da Ação no Vencimento', position: 'insideBottom', offset: -10 }}
                />
                <YAxis 
                  domain={['dataMin - 1', 'dataMax + 1']}
                  tickFormatter={(value) => `R$ ${value.toFixed(1)}`}
                  label={{ value: 'Lucro/Prejuízo', angle: -90, position: 'insideLeft', offset: 0 }}
                />
                <Tooltip 
                  labelFormatter={(value) => `Preço da Ação: R$ ${Number(value).toFixed(2)}`}
                  formatter={(value: any, name: string) => [
                    `R$ ${Number(value).toFixed(2)}`,
                    name === 'negativePayoff' ? 'Perda' : 'Lucro'
                  ]}
                  contentStyle={{
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    border: 'none',
                    borderRadius: '6px',
                    color: 'white'
                  }}
                />
                <ReferenceLine y={0} stroke="#666" strokeDasharray="2 2" />
                <ReferenceLine 
                  x={spotPrice} 
                  stroke="#ff6b35" 
                  strokeDasharray="5 5" 
                  label={{ value: 'Price', position: 'top', fill: '#ff6b35', offset: 20 }} 
                />
                <ReferenceLine 
                  x={strikePrice} 
                  stroke="#4ecdc4" 
                  strokeDasharray="5 5" 
                  label={{ value: 'Strike', position: 'top', fill: '#4ecdc4', offset: 20 }} 
                />
                <ReferenceLine 
                  x={breakEvenPrice} 
                  stroke="#ffe66d" 
                  strokeDasharray="5 5" 
                  label={{ value: 'BE', position: 'top', fill: '#ffe66d', offset: 20 }} 
                />
                
                {/* Negative payoff area (red) */}
                <Area
                  type="monotone"
                  dataKey="negativePayoff"
                  stroke="#ef4444"
                  fill="#ef4444"
                  fillOpacity={0.3}
                  connectNulls={false}
                />
                
                {/* Positive payoff area (green) */}
                <Area
                  type="monotone"
                  dataKey="positivePayoff"
                  stroke="#10b981"
                  fill="#10b981"
                  fillOpacity={0.3}
                  connectNulls={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      {/* Strategy Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Key Metrics */}
        <Card>
          <CardHeader>
            <CardTitle>Métricas Principais</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm text-muted-foreground">Preço Break-even</div>
                <div className="text-lg font-bold">{formatCurrency(breakEvenPrice)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Lucro Máximo</div>
                <div className="text-lg font-bold text-green-600">{formatCurrency(maxProfit)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Perda Máxima</div>
                <div className="text-lg font-bold text-red-600">{formatCurrency(maxLoss)}</div>
              </div>
              <div>
                <div className="text-sm text-muted-foreground">Pontuação</div>
                <div className="text-lg font-bold">{option.score?.toFixed(2) || 'N/A'}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Additional Details */}
        <Card>
          <CardHeader>
            <CardTitle>Detalhes da Estratégia</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-2 text-sm">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Símbolo:</span>
                <span className="font-medium">{option.symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Subjacente:</span>
                <span className="font-medium">{option.parent_symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Dias para Vencimento:</span>
                <span className="font-medium">{option.days_to_maturity}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Retorno Anual:</span>
                <span className="font-medium">{formatPercent(option.annual_return)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Variação Spot para Retorno Máximo:</span>
                <span className="font-medium">{formatPercent(option.spot_variation_to_max_return)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Distância PM para Lucro:</span>
                <span className="font-medium">{formatPercent(option.pm_distance_to_profit)}</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Risk Analysis */}
              <Card>
          <CardHeader>
            <CardTitle>Análise de Risco</CardTitle>
            <CardDescription>
              Entendendo os riscos e recompensas desta estratégia de call coberto
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="font-medium mb-2">Visão Geral da Estratégia</h4>
                <p className="text-sm text-muted-foreground">
                  Esta estratégia de call coberto envolve manter ações {option.parent_symbol} e vender uma opção de compra 
                  com preço strike {formatCurrency(strikePrice)}. Você recebe {formatCurrency(premium)} em prêmio 
                  e limita seu ganho em {formatCurrency(maxProfit)} se a ação subir acima do preço strike.
                </p>
              </div>
              
              <div>
                <h4 className="font-medium mb-2">Considerações de Risco</h4>
                <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                  <li>Ganho limitado: Os lucros são limitados se o preço da ação exceder {formatCurrency(strikePrice)}</li>
                  <li>Exposição total à baixa: Você assume toda a perda se a ação cair</li>
                  <li>Ponto de equilíbrio: {formatCurrency(breakEvenPrice)} (preço atual menos prêmio recebido)</li>
                  <li>Perda máxima: {formatCurrency(maxLoss)} se a ação for a zero</li>
                </ul>
              </div>
            </div>
          </CardContent>
        </Card>
    </div>
  );
}