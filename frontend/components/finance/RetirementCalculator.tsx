'use client';

import React, { useState, useEffect } from 'react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ReferenceLine
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { RetirementParams, RetirementResults, RetirementDataPoint } from '@/types/retirement';
import { calculateRetirementPlan } from '@/utils/retirementCalculator';
import { cn } from '@/lib/utils';

/**
 * Default parameters for retirement calculation
 */
const defaultParams: RetirementParams = {
  salary: 60000,
  current_age: 30,
  retirement_age: 65,
  max_age: 100,
  retirement_income: 120000,
  accumulation_rate: 0.12,
  distribution_rate: 0.05,
  initial_capital: 0,
};

/**
 * Retirement calculator component
 */
export default function RetirementCalculator() {
  // Helper functions
  const formatNumberDisplay = (value: number) => {
    return new Intl.NumberFormat('pt-BR').format(value);
  };

  const parseFormattedNumber = (formattedValue: string) => {
    return Number(formattedValue.replace(/\./g, '').replace(/,/g, '.'));
  };

  // State for parameters and calculation results
  const [params, setParams] = useState<RetirementParams>(defaultParams);
  const [results, setResults] = useState<RetirementResults | null>(null);
  const [activeTab, setActiveTab] = useState<string>('combined');
  
  // State for formatted display values
  const [displayValues, setDisplayValues] = useState({
    salary: formatNumberDisplay(defaultParams.salary),
    retirement_income: formatNumberDisplay(defaultParams.retirement_income),
    initial_capital: formatNumberDisplay(defaultParams.initial_capital || 0),
  });
  
  // Calculate retirement plan when parameters change
  useEffect(() => {
    try {
      const calculatedResults = calculateRetirementPlan(params);
      setResults(calculatedResults);
    } catch (error) {
      console.error('Error calculating retirement plan:', error);
    }
  }, [params]);
  
  // Handle parameter changes
  const handleParamChange = (name: keyof RetirementParams, value: number) => {
    setParams(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Update display values for monetary fields
    if (name === 'salary' || name === 'retirement_income' || name === 'initial_capital') {
      setDisplayValues(prev => ({
        ...prev,
        [name]: formatNumberDisplay(value)
      }));
    }
  };

  // Handle formatted input changes
  const handleFormattedInputChange = (name: 'salary' | 'retirement_income' | 'initial_capital', formattedValue: string) => {
    const rawValue = parseFormattedNumber(formattedValue);
    if (!isNaN(rawValue)) {
      handleParamChange(name, rawValue);
    }
  };
  
  // Format currency for display
  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('en-US', { 
      style: 'currency', 
      currency: 'BRL',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0 
    }).format(value);
  };
  
  // Format percentage for display
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(1)}%`;
  };

  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-card p-4 border rounded shadow-sm">
          <p className="font-medium">Idade {label}</p>
          
          <p className="text-sm mt-1">
            Capital: {formatCurrency(data.value)}
          </p>
          
          {data.contribution > 0 && (
            <p className="text-sm text-finance-success-500">
              Contribuição: +{formatCurrency(data.contribution)}
            </p>
          )}
          
          {data.withdrawal > 0 && (
            <p className="text-sm text-finance-danger-500">
              Saque: -{formatCurrency(data.withdrawal)}
            </p>
          )}
          
          <p className="text-xs text-muted-foreground mt-1">
            Fase: {data.phase === 'accumulation' ? 'Acumulação' : 'Distribuição'}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="grid gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Calculadora de Aposentadoria</CardTitle>
          <CardDescription>
            Planeje sua aposentadoria ajustando os parâmetros abaixo
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-6">
            {/* Input parameters */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {/* Current age */}
              <div className="space-y-2">
                <Label htmlFor="current_age">Idade Atual</Label>
                <div className="flex items-center gap-2">
                  <Slider
                    id="current_age"
                    min={18}
                    max={70}
                    step={1}
                    value={[params.current_age]}
                    onValueChange={(values) => handleParamChange('current_age', values[0])}
                  />
                  <span className="w-12 text-right">{params.current_age}</span>
                </div>
              </div>
              
              {/* Retirement age */}
              <div className="space-y-2">
                <Label htmlFor="retirement_age">Idade de Aposentadoria</Label>
                <div className="flex items-center gap-2">
                  <Slider
                    id="retirement_age"
                    min={params.current_age + 1}
                    max={85}
                    step={1}
                    value={[params.retirement_age]}
                    onValueChange={(values) => handleParamChange('retirement_age', values[0])}
                  />
                  <span className="w-12 text-right">{params.retirement_age}</span>
                </div>
              </div>
              
              {/* Maximum age */}
              <div className="space-y-2">
                <Label htmlFor="max_age">Idade Máxima</Label>
                <div className="flex items-center gap-2">
                  <Slider
                    id="max_age"
                    min={params.retirement_age + 1}
                    max={120}
                    step={1}
                    value={[params.max_age]}
                    onValueChange={(values) => handleParamChange('max_age', values[0])}
                  />
                  <span className="w-12 text-right">{params.max_age}</span>
                </div>
              </div>
              
              {/* Annual income */}
              <div className="space-y-2">
                <Label htmlFor="salary">Renda Anual (R$)</Label>
                <Input
                  id="salary"
                  type="text"
                  value={displayValues.salary}
                  onChange={(e) => handleFormattedInputChange('salary', e.target.value)}
                  placeholder="0"
                />
              </div>
              
              {/* Retirement income */}
              <div className="space-y-2">
                <Label htmlFor="retirement_income">Renda na Aposentadoria (R$)</Label>
                <Input
                  id="retirement_income"
                  type="text"
                  value={displayValues.retirement_income}
                  onChange={(e) => handleFormattedInputChange('retirement_income', e.target.value)}
                  placeholder="0"
                />
              </div>
              
              {/* Initial capital */}
              <div className="space-y-2">
                <Label htmlFor="initial_capital">Capital Inicial (R$)</Label>
                <Input
                  id="initial_capital"
                  type="text"
                  value={displayValues.initial_capital}
                  onChange={(e) => handleFormattedInputChange('initial_capital', e.target.value)}
                  placeholder="0"
                />
              </div>
              
              {/* Investment fraction */}
              <div className="space-y-2">
                <Label htmlFor="investment_fraction">
                  Fração Investida {results && `(${formatPercent(results.investment_fraction)})`}
                </Label>
                <div className="flex items-center gap-2">
                  <Slider
                    id="investment_fraction"
                    min={0.01}
                    max={0.5}
                    step={0.01}
                    value={[results?.investment_fraction || 0.1]}
                    onValueChange={(values) => handleParamChange('investment_fraction', values[0])}
                  />
                  <span className="w-20 text-right">
                    {formatPercent(results?.investment_fraction || 0)}
                  </span>
                </div>
              </div>
              
              {/* Accumulation interest rate */}
              <div className="space-y-2">
                <Label htmlFor="accumulation_rate">Taxa de Acumulação (%)</Label>
                <div className="flex items-center gap-2">
                  <Slider
                    id="accumulation_rate"
                    min={0.01}
                    max={0.2}
                    step={0.01}
                    value={[params.accumulation_rate]}
                    onValueChange={(values) => handleParamChange('accumulation_rate', values[0])}
                  />
                  <span className="w-16 text-right">
                    {formatPercent(params.accumulation_rate)}
                  </span>
                </div>
              </div>
              
              {/* Distribution interest rate */}
              <div className="space-y-2">
                <Label htmlFor="distribution_rate">Taxa de Distribuição (%)</Label>
                <div className="flex items-center gap-2">
                  <Slider
                    id="distribution_rate"
                    min={0.01}
                    max={0.1}
                    step={0.01}
                    value={[params.distribution_rate]}
                    onValueChange={(values) => handleParamChange('distribution_rate', values[0])}
                  />
                  <span className="w-16 text-right">
                    {formatPercent(params.distribution_rate)}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Summary stats */}
            {results && (
              <div className="grid gap-4 mt-4 md:grid-cols-3">
                <Card>
                  <CardHeader className="p-4">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Acumulado na Aposentadoria
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <div className="text-2xl font-bold">
                      {formatCurrency(results.final_accumulation)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Seu capital estimado aos {params.retirement_age} anos
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="p-4">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Total Contribuído
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <div className="text-2xl font-bold">
                      {formatCurrency(results.total_contributed)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      Valor investido ao longo de {params.retirement_age - params.current_age} anos
                    </p>
                  </CardContent>
                </Card>
                
                <Card>
                  <CardHeader className="p-4">
                    <CardTitle className="text-sm font-medium text-muted-foreground">
                      Retorno dos Investimentos
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <div className="text-2xl font-bold">
                      {formatCurrency(results.investment_returns)}
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {((results.investment_returns / results.total_contributed) * 100).toFixed(0)}% do seu montante final
                    </p>
                  </CardContent>
                </Card>
              </div>
            )}
            
            {/* Chart visualization */}
            <Tabs defaultValue="combined" value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-4">
                <TabsTrigger value="combined">Visão Combinada</TabsTrigger>
                <TabsTrigger value="accumulation">Fase de Acumulação</TabsTrigger>
                <TabsTrigger value="distribution">Fase de Distribuição</TabsTrigger>
              </TabsList>
              
              {results && (
                <>
                  {activeTab === 'combined' ? (
                    <CombinedRetirementChart 
                      chartData={results.chartData}
                      retirementAge={params.retirement_age}
                      depletionAge={results.depletion_age}
                    />
                  ) : (
                    <div className="h-[400px] w-full">
                      <ResponsiveContainer width="100%" height="100%">
                        <AreaChart
                          data={results.chartData}
                          margin={{ top: 10, right: 10, left: 10, bottom: 20 }}
                        >
                          <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.2} />
                          <XAxis
                            dataKey="age"
                            label={{ value: 'Idade', position: 'insideBottom', offset: -10 }}
                          />
                          <YAxis
                            tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
                            label={{
                              value: 'Capital (R$)',
                              angle: -90,
                              position: 'insideLeft',
                              style: { textAnchor: 'middle' }
                            }}
                          />
                          <Tooltip content={<CustomTooltip />} />
                          <Legend />
                          
                          {/* Reference line for retirement age */}
                          <ReferenceLine
                            x={params.retirement_age}
                            stroke="#8884d8"
                            strokeDasharray="3 3"
                            label={{
                              value: 'Aposentadoria',
                              position: 'top',
                              fill: '#8884d8',
                              fontSize: 12
                            }}
                          />
                          
                          {/* Reference line for fund depletion if applicable */}
                          {results.depletion_age && (
                            <ReferenceLine
                              x={results.depletion_age}
                              stroke="#ff7300"
                              strokeDasharray="3 3"
                              label={{
                                value: 'Depleção',
                                position: 'top',
                                fill: '#ff7300',
                                fontSize: 12
                              }}
                            />
                          )}
                          
                          {/* Areas for accumulation and distribution phases */}
                          {activeTab === 'accumulation' && (
                            <Area
                              type="monotone"
                              dataKey="value"
                              name="Fase de Acumulação"
                              stroke="hsl(var(--chart-1))"
                              fill="hsl(var(--chart-1))"
                              fillOpacity={0.3}
                              activeDot={{ r: 6 }}
                              data={results.chartData.filter(d => d.phase === 'accumulation')}
                              connectNulls={true}
                            />
                          )}
                          
                          {activeTab === 'distribution' && (
                            <Area
                              type="monotone"
                              dataKey="value"
                              name="Fase de Distribuição"
                              stroke="hsl(var(--chart-2))"
                              fill="hsl(var(--chart-2))"
                              fillOpacity={0.3}
                              activeDot={{ r: 6 }}
                              data={results.chartData.filter(d => d.phase === 'distribution')}
                              connectNulls={true}
                            />
                          )}
                        </AreaChart>
                      </ResponsiveContainer>
                    </div>
                  )}
                </>
              )}
              
              {/* Results summary */}
              {results && (
                <div className="mt-6 p-4 bg-muted rounded-lg">
                  <h3 className="font-medium mb-2">Resumo</h3>
                  
                  {/* Highlighted investment fraction section */}
                  <div className="mb-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                    <div className="text-center">
                      <p className="text-xs text-muted-foreground mb-1">Fração de Investimento Necessária</p>
                      <div className="text-2xl font-bold text-orange-500">
                        {formatPercent(results.investment_fraction)}
                      </div>
                      <p className="text-sm text-muted-foreground mt-1">
                        {formatCurrency(results.investment_fraction * params.salary)} por ano
                      </p>
                    </div>
                  </div>
                  
                  <div className="grid gap-2 text-sm">
                    <p>
                      Para atingir sua meta de aposentadoria, você deve investir <strong>{formatPercent(results.investment_fraction)}</strong> da sua renda anual ({formatCurrency(results.investment_fraction * params.salary)} por ano).
                    </p>
                    <p>
                      Aos {params.retirement_age} anos, você terá acumulado <strong>{formatCurrency(results.final_accumulation)}</strong>, sendo {formatCurrency(results.investment_returns)} provenientes de retornos dos investimentos.
                    </p>
                    <p>
                      {results.depletion_age ? (
                        <>Seus recursos se esgotarão aos <strong>{results.depletion_age}</strong> anos.</>
                      ) : (
                        <>Seus recursos durarão além dos <strong>{params.max_age}</strong> anos, com saldo final de {formatCurrency(results.distribution_ending_balance)}.</>
                      )}
                    </p>
                  </div>
                </div>
              )}
            </Tabs>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Component for displaying the combined retirement chart view
 */
const CombinedRetirementChart = ({ 
  chartData, 
  retirementAge, 
  depletionAge 
}: { 
  chartData: RetirementDataPoint[], 
  retirementAge: number,
  depletionAge: number | null
}) => {
  // Find the retirement age data point in the original data
  const retirementPoint = chartData.find(d => d.age === retirementAge);
  
  // Process data for combined view - ensuring both phases include retirement age
  const accumulationData = chartData
    .filter(d => d.phase === 'accumulation' || d.age === retirementAge)
    .map(d => ({ ...d }));
  
  const distributionData = chartData
    .filter(d => d.phase === 'distribution' || d.age === retirementAge)
    .map(d => ({ 
      ...d,
      // Ensure the retirement point in distribution dataset has the same phase
      // as in the original data to keep the chart coloring consistent
      phase: d.age === retirementAge ? 'distribution' : d.phase 
    }));
  
  // Custom tooltip for the chart
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;
      return (
        <div className="bg-card p-4 border rounded shadow-sm">
          <p className="font-medium">Idade {label}</p>
          
          <p className="text-sm mt-1">
            Capital: {new Intl.NumberFormat('en-US', { 
              style: 'currency', 
              currency: 'BRL',
              minimumFractionDigits: 0,
              maximumFractionDigits: 0 
            }).format(data.value)}
          </p>
          
          {data.contribution > 0 && (
            <p className="text-sm text-finance-success-500">
              Contribuição: +{new Intl.NumberFormat('en-US', { 
                style: 'currency', 
                currency: 'BRL',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0 
              }).format(data.contribution)}
            </p>
          )}
          
          {data.withdrawal > 0 && (
            <p className="text-sm text-finance-danger-500">
              Saque: -{new Intl.NumberFormat('en-US', { 
                style: 'currency', 
                currency: 'BRL',
                minimumFractionDigits: 0,
                maximumFractionDigits: 0 
              }).format(data.withdrawal)}
            </p>
          )}
          
          <p className="text-xs text-muted-foreground mt-1">
            Fase: {data.phase === 'accumulation' ? 'Acumulação' : 'Distribuição'}
          </p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="h-[400px] w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          margin={{ top: 40, right: 30, left: 30, bottom: 10 }}
        >
          <CartesianGrid strokeDasharray="3 3" vertical={false} strokeOpacity={0.2} />
          <XAxis
            dataKey="age"
            label={{ value: 'Idade', position: 'insideBottom', offset: 0 }}
            type="number"
            domain={['dataMin', 'dataMax']}
            allowDuplicatedCategory={false}
          />
          <YAxis
            tickFormatter={(value) => `${(value / 1000000).toFixed(1)}M`}
            label={{
              value: 'Capital (R$)',
              angle: -90,
              position: 'insideLeft',
              style: { textAnchor: 'middle' }
            }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          
          {/* Reference line for retirement age */}
          <ReferenceLine
            x={retirementAge}
            stroke="#8884d8"
            strokeDasharray="3 3"
            label={{
              value: 'Aposentadoria',
              position: 'top',
              fill: '#8884d8',
              fontSize: 12,
              offset: 20
            }}
          />
          
          {/* Reference line for fund depletion if applicable */}
          {depletionAge && (
            <ReferenceLine
              x={depletionAge}
              stroke="#ff7300"
              strokeDasharray="3 3"
              label={{
                value: 'Depleção',
                position: 'top',
                fill: '#ff7300',
                fontSize: 12,
                offset: 20
              }}
            />
          )}
          
          {/* Accumulation phase */}
          <Area
            type="monotone"
            dataKey="value"
            name="Fase de Acumulação"
            stroke="hsl(var(--chart-1))"
            fill="hsl(var(--chart-1))"
            fillOpacity={0.3}
            activeDot={{ r: 6 }}
            data={accumulationData}
            connectNulls={true}
          />
          
          {/* Distribution phase */}
          <Area
            type="monotone"
            dataKey="value"
            name="Fase de Distribuição"
            stroke="hsl(var(--chart-2))"
            fill="hsl(var(--chart-2))"
            fillOpacity={0.3}
            activeDot={{ r: 6 }}
            data={distributionData}
            connectNulls={true}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
};