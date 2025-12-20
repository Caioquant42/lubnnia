'use client';

import { AlertCircle, RefreshCcw, SlidersHorizontal } from 'lucide-react';
import { useEffect, useState } from 'react';

// Import API functions
import {
  extractUniqueSymbols,
  getCointegrationData,
  getPairDetails,
  getRecentSignals,
  PairsResponse,
  PairsTradingParams,
} from '__api__/pairstrading';

// Import components
import CointegrationTable from '@/components/Pairstrading/CointegrationTable';
import PairDetails from '@/components/Pairstrading/PairDetails';
import RecentSignalsTable from '@/components/Pairstrading/RecentSignalsTable';
import StatsCard from '@/components/Pairstrading/StatsCard';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function PairsTradingDashboard() {
  // State for current tab
  const [activeTab, setActiveTab] = useState<string>('signals');

  // State for selected period
  const [period, setPeriod] = useState<'last_6_months' | 'last_12_months'>(
    'last_6_months'
  );

  // State for filters
  const [filters, setFilters] = useState<PairsTradingParams>({
    sort_by: 'signal_date',
    sort_order: 'desc',
    cointegrated_only: true,
    limit: 50,
  });

  // State for selected pair details
  const [selectedPair, setSelectedPair] = useState<{
    asset1: string;
    asset2: string;
  } | null>(null);

  // State for data loading and errors
  const [loadingSignals, setLoadingSignals] = useState<boolean>(true);
  const [loadingCointegration, setLoadingCointegration] =
    useState<boolean>(true);
  const [loadingPairDetails, setLoadingPairDetails] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  // State for API data
  const [signalsData, setSignalsData] = useState<PairsResponse | null>(null);
  const [cointegrationData, setCointegrationData] =
    useState<PairsResponse | null>(null);
  const [pairDetailsData, setPairDetailsData] = useState<any | null>(null);

  // State for available symbols (for filtering)
  const [availableSymbols, setAvailableSymbols] = useState<string[]>([]);

  // State for filter dropdowns
  const [filtersVisible, setFiltersVisible] = useState<boolean>(false);

  // Fetch signals data
  useEffect(() => {
    const fetchSignals = async () => {
      try {
        setLoadingSignals(true);
        setError(null);
        const data = await getRecentSignals({
          asset1: filters.asset1,
          asset2: filters.asset2,
          signal_type: filters.signal_type as 'buy' | 'sell' | undefined,
          min_zscore: filters.min_zscore,
          max_zscore: filters.max_zscore,
          min_beta: filters.min_beta,
          max_beta: filters.max_beta,
          min_half_life: filters.min_half_life,
          max_half_life: filters.max_half_life,
          sort_by: filters.sort_by,
          sort_order: filters.sort_order as 'asc' | 'desc',
          limit: filters.limit,
        });

        if (data) {
          setSignalsData(data);
          // Extract unique symbols for filtering
          const symbols = extractUniqueSymbols(data);
          setAvailableSymbols(symbols);
        }
      } catch (err) {
        console.error('Error fetching signals:', err);
        setError('Erro ao carregar sinais de trading');
      } finally {
        setLoadingSignals(false);
      }
    };

    fetchSignals();
  }, [filters]);

  // Fetch cointegration data
  useEffect(() => {
    const fetchCointegration = async () => {
      try {
        setLoadingCointegration(true);
        setError(null);
        const data = await getCointegrationData({
          period,
          asset1: filters.asset1,
          asset2: filters.asset2,
          min_beta: filters.min_beta,
          max_beta: filters.max_beta,
          min_half_life: filters.min_half_life,
          max_half_life: filters.max_half_life,
          cointegrated_only: filters.cointegrated_only,
          sort_by: filters.sort_by,
          sort_order: filters.sort_order as 'asc' | 'desc',
          limit: filters.limit,
        });

        if (data) {
          setCointegrationData(data);
        }
      } catch (err) {
        console.error('Error fetching cointegration data:', err);
        setError('Erro ao carregar dados de cointegração');
      } finally {
        setLoadingCointegration(false);
      }
    };

    fetchCointegration();
  }, [period, filters]);

  // Fetch pair details when a pair is selected
  useEffect(() => {
    if (selectedPair) {
      const fetchPairDetails = async () => {
        try {
          setLoadingPairDetails(true);
          const data = await getPairDetails(
            selectedPair.asset1,
            selectedPair.asset2
          );
          setPairDetailsData(data);
        } catch (err) {
          console.error('Error fetching pair details:', err);
          setError('Erro ao carregar detalhes do par');
        } finally {
          setLoadingPairDetails(false);
        }
      };

      fetchPairDetails();
    }
  }, [selectedPair]);

  // Handler for filter changes
  const handleFilterChange = (key: keyof PairsTradingParams, value: any) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  // Handler for period changes
  const handlePeriodChange = (value: string) => {
    setPeriod(value as 'last_6_months' | 'last_12_months');
  };

  // Handler for pair selection
  const handlePairSelect = (asset1: string, asset2: string) => {
    setSelectedPair({ asset1, asset2 });
  };

  // Handler for closing pair details
  const handleClosePairDetails = () => {
    setSelectedPair(null);
    setPairDetailsData(null);
  };

  // Reset filters
  const handleResetFilters = () => {
    setFilters({
      sort_by: 'signal_date',
      sort_order: 'desc',
      cointegrated_only: true,
      limit: 50,
    });
  };

  return (
    <div className='space-y-4'>
      {error && (
        <Alert variant='destructive'>
          <AlertCircle className='h-4 w-4' />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {selectedPair ? (
        <Card>
          <CardHeader className='flex flex-row items-center justify-between space-y-0 pb-2'>
            <div>
              <CardTitle>
                Análise do Par: {selectedPair.asset1} / {selectedPair.asset2}
              </CardTitle>
              <CardDescription>
                Análise detalhada e desempenho histórico
              </CardDescription>
            </div>
            <Button variant='outline' onClick={handleClosePairDetails}>
              Voltar ao Resumo
            </Button>
          </CardHeader>
          <CardContent>
            {loadingPairDetails ? (
              <div className='space-y-2'>
                <Skeleton className='h-8 w-full' />
                <Skeleton className='h-[400px] w-full' />
              </div>
            ) : (
              <PairDetails data={pairDetailsData} />
            )}
          </CardContent>
        </Card>
      ) : (
        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className='flex flex-col md:flex-row justify-between items-start md:items-center space-y-2 md:space-y-0 pb-4'>
            <TabsList>
              <TabsTrigger value='signals'>Sinais Recentes</TabsTrigger>
              <TabsTrigger value='cointegration'>
                Pares Cointegrados
              </TabsTrigger>
            </TabsList>

            <div className='flex space-x-2'>
              {activeTab === 'cointegration' && (
                <Select value={period} onValueChange={handlePeriodChange}>
                  <SelectTrigger className='w-[180px]'>
                    <SelectValue placeholder='Selecionar período' />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value='last_6_months'>
                      Últimos 6 Meses
                    </SelectItem>
                    <SelectItem value='last_12_months'>
                      Últimos 12 Meses
                    </SelectItem>
                  </SelectContent>
                </Select>
              )}

              <Popover open={filtersVisible} onOpenChange={setFiltersVisible}>
                <PopoverTrigger asChild>
                  <Button variant='outline' className='flex items-center gap-2'>
                    <SlidersHorizontal className='h-4 w-4' />
                    <span>Filtros</span>
                    {Object.keys(filters).filter(
                      (k) =>
                        k !== 'sort_by' &&
                        k !== 'sort_order' &&
                        k !== 'limit' &&
                        k !== 'cointegrated_only' &&
                        filters[k as keyof PairsTradingParams]
                    ).length > 0 && (
                      <Badge variant='secondary' className='ml-1'>
                        {
                          Object.keys(filters).filter(
                            (k) =>
                              k !== 'sort_by' &&
                              k !== 'sort_order' &&
                              k !== 'limit' &&
                              k !== 'cointegrated_only' &&
                              filters[k as keyof PairsTradingParams]
                          ).length
                        }
                      </Badge>
                    )}
                  </Button>
                </PopoverTrigger>
                <PopoverContent className='w-[350px] p-4' align='end'>
                  <div className='space-y-4'>
                    <div className='flex items-center justify-between'>
                      <h4 className='font-medium'>Opções de Filtro</h4>
                      <Button
                        variant='ghost'
                        size='sm'
                        onClick={handleResetFilters}
                        className='h-8 flex items-center gap-2 text-xs'
                      >
                        <RefreshCcw className='h-3 w-3' />
                        Resetar
                      </Button>
                    </div>

                    <div className='space-y-2'>
                      <Label htmlFor='asset-filter'>Filtrar por Símbolo</Label>
                      <Select
                        value={filters.asset1 || ''}
                        onValueChange={(value) =>
                          handleFilterChange(
                            'asset1',
                            value === '' ? undefined : value
                          )
                        }
                      >
                        <SelectTrigger id='asset-filter'>
                          <SelectValue placeholder='Qualquer símbolo' />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value=''>Qualquer símbolo</SelectItem>
                          {availableSymbols.map((symbol) => (
                            <SelectItem key={symbol} value={symbol}>
                              {symbol}
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>

                    {activeTab === 'signals' && (
                      <div className='space-y-2'>
                        <Label htmlFor='signal-type'>Tipo de Sinal</Label>
                        <Select
                          value={filters.signal_type || ''}
                          onValueChange={(value) =>
                            handleFilterChange(
                              'signal_type',
                              value === '' ? undefined : value
                            )
                          }
                        >
                          <SelectTrigger id='signal-type'>
                            <SelectValue placeholder='Todos os sinais' />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value=''>Todos os sinais</SelectItem>
                            <SelectItem value='buy'>
                              Sinais de compra
                            </SelectItem>
                            <SelectItem value='sell'>
                              Sinais de venda
                            </SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    )}

                    <Accordion type='single' collapsible className='w-full'>
                      <AccordionItem value='advanced'>
                        <AccordionTrigger>Filtros Avançados</AccordionTrigger>
                        <AccordionContent>
                          <div className='space-y-4'>
                            <div className='space-y-2'>
                              <div className='flex justify-between'>
                                <Label>Faixa de Z-Score</Label>
                                <div className='text-xs text-muted-foreground'>
                                  {filters.min_zscore !== undefined
                                    ? filters.min_zscore
                                    : 'Qualquer'}{' '}
                                  -{' '}
                                  {filters.max_zscore !== undefined
                                    ? filters.max_zscore
                                    : 'Qualquer'}
                                </div>
                              </div>
                              <div className='flex items-center gap-4'>
                                <Input
                                  type='number'
                                  placeholder='Mín'
                                  className='w-20'
                                  value={
                                    filters.min_zscore !== undefined
                                      ? filters.min_zscore
                                      : ''
                                  }
                                  onChange={(e) =>
                                    handleFilterChange(
                                      'min_zscore',
                                      e.target.value === ''
                                        ? undefined
                                        : parseFloat(e.target.value)
                                    )
                                  }
                                />
                                <Input
                                  type='number'
                                  placeholder='Máx'
                                  className='w-20'
                                  value={
                                    filters.max_zscore !== undefined
                                      ? filters.max_zscore
                                      : ''
                                  }
                                  onChange={(e) =>
                                    handleFilterChange(
                                      'max_zscore',
                                      e.target.value === ''
                                        ? undefined
                                        : parseFloat(e.target.value)
                                    )
                                  }
                                />
                              </div>
                            </div>

                            <div className='space-y-2'>
                              <div className='flex justify-between'>
                                <Label>Faixa de Beta (Razão de Hedge)</Label>
                                <div className='text-xs text-muted-foreground'>
                                  {filters.min_beta !== undefined
                                    ? filters.min_beta
                                    : 'Qualquer'}{' '}
                                  -{' '}
                                  {filters.max_beta !== undefined
                                    ? filters.max_beta
                                    : 'Qualquer'}
                                </div>
                              </div>
                              <div className='flex items-center gap-4'>
                                <Input
                                  type='number'
                                  placeholder='Mín'
                                  className='w-20'
                                  value={
                                    filters.min_beta !== undefined
                                      ? filters.min_beta
                                      : ''
                                  }
                                  onChange={(e) =>
                                    handleFilterChange(
                                      'min_beta',
                                      e.target.value === ''
                                        ? undefined
                                        : parseFloat(e.target.value)
                                    )
                                  }
                                />
                                <Input
                                  type='number'
                                  placeholder='Máx'
                                  className='w-20'
                                  value={
                                    filters.max_beta !== undefined
                                      ? filters.max_beta
                                      : ''
                                  }
                                  onChange={(e) =>
                                    handleFilterChange(
                                      'max_beta',
                                      e.target.value === ''
                                        ? undefined
                                        : parseFloat(e.target.value)
                                    )
                                  }
                                />
                              </div>
                            </div>

                            <div className='space-y-2'>
                              <div className='flex justify-between'>
                                <Label>Faixa de Meia-Vida (Dias)</Label>
                                <div className='text-xs text-muted-foreground'>
                                  {filters.min_half_life !== undefined
                                    ? filters.min_half_life
                                    : 'Qualquer'}{' '}
                                  -{' '}
                                  {filters.max_half_life !== undefined
                                    ? filters.max_half_life
                                    : 'Qualquer'}
                                </div>
                              </div>
                              <div className='flex items-center gap-4'>
                                <Input
                                  type='number'
                                  placeholder='Mín'
                                  className='w-20'
                                  value={
                                    filters.min_half_life !== undefined
                                      ? filters.min_half_life
                                      : ''
                                  }
                                  onChange={(e) =>
                                    handleFilterChange(
                                      'min_half_life',
                                      e.target.value === ''
                                        ? undefined
                                        : parseFloat(e.target.value)
                                    )
                                  }
                                />
                                <Input
                                  type='number'
                                  placeholder='Máx'
                                  className='w-20'
                                  value={
                                    filters.max_half_life !== undefined
                                      ? filters.max_half_life
                                      : ''
                                  }
                                  onChange={(e) =>
                                    handleFilterChange(
                                      'max_half_life',
                                      e.target.value === ''
                                        ? undefined
                                        : parseFloat(e.target.value)
                                    )
                                  }
                                />
                              </div>
                            </div>

                            {activeTab === 'cointegration' && (
                              <div className='flex items-center space-x-2 pt-2'>
                                <Checkbox
                                  id='cointegrated-only'
                                  checked={filters.cointegrated_only}
                                  onCheckedChange={(checked) =>
                                    handleFilterChange(
                                      'cointegrated_only',
                                      checked
                                    )
                                  }
                                />
                                <Label htmlFor='cointegrated-only'>
                                  Mostrar apenas pares cointegrados
                                </Label>
                              </div>
                            )}
                          </div>
                        </AccordionContent>
                      </AccordionItem>
                    </Accordion>
                  </div>
                </PopoverContent>
              </Popover>
            </div>
          </div>

          {/* Recent Signals Tab */}
          <TabsContent value='signals' className='space-y-4'>
            {signalsData?.signals?.summary && (
              <div className='grid gap-4 grid-cols-1 md:grid-cols-3 mb-4'>
                <StatsCard
                  title='Total de Sinais'
                  value={signalsData.signals.summary.total_signals.toString()}
                  description='Dos últimos 5 dias de trading'
                />
                <StatsCard
                  title='Sinais de Compra'
                  value={signalsData.signals.summary.buy_signals.toString()}
                  description={`${Math.round((signalsData.signals.summary.buy_signals / signalsData.signals.summary.total_signals) * 100)}% do total`}
                  trend='up'
                />
                <StatsCard
                  title='Sinais de Venda'
                  value={signalsData.signals.summary.sell_signals.toString()}
                  description={`${Math.round((signalsData.signals.summary.sell_signals / signalsData.signals.summary.total_signals) * 100)}% do total`}
                  trend='down'
                />
              </div>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Sinais de Trading Recentes</CardTitle>
                <CardDescription>
                  Oportunidades de trading ativas dos últimos 5 dias de trading
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loadingSignals ? (
                  <div className='space-y-2'>
                    <Skeleton className='h-8 w-full' />
                    <Skeleton className='h-[300px] w-full' />
                  </div>
                ) : (
                  <RecentSignalsTable
                    data={signalsData}
                    onPairSelect={handlePairSelect}
                  />
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Cointegration Tab */}
          <TabsContent value='cointegration' className='space-y-4'>
            {cointegrationData?.cointegration?.summary && (
              <div className='grid gap-4 grid-cols-1 md:grid-cols-3 mb-4'>
                <StatsCard
                  title='Total de Pares Analisados'
                  value={cointegrationData.cointegration.summary.total_pairs.toString()}
                  description={`Para os ${period === 'last_6_months' ? 'últimos 6 meses' : 'últimos 12 meses'}`}
                />
                <StatsCard
                  title='Pares Cointegrados'
                  value={cointegrationData.cointegration.summary.cointegrated_pairs.toString()}
                  description={`Evidência estatística de cointegração`}
                />
                <StatsCard
                  title='Taxa de Cointegração'
                  value={`${Math.round(cointegrationData.cointegration.summary.cointegrated_percentage)}%`}
                  description={`Percentual de pares analisados`}
                />
              </div>
            )}

            <Card>
              <CardHeader>
                <CardTitle>Pares Cointegrados</CardTitle>
                <CardDescription>
                  Pares de ações mostrando evidência estatística de cointegração
                </CardDescription>
              </CardHeader>
              <CardContent>
                {loadingCointegration ? (
                  <div className='space-y-2'>
                    <Skeleton className='h-8 w-full' />
                    <Skeleton className='h-[300px] w-full' />
                  </div>
                ) : (
                  <CointegrationTable
                    data={cointegrationData}
                    onPairSelect={handlePairSelect}
                  />
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
