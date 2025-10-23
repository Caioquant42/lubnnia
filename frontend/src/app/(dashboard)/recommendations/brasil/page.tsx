'use client';

import {
  AlertCircle,
  ArrowDown,
  ArrowUp,
  BarChart3,
  ClipboardList,
  Download,
  RefreshCw,
  Search,
  Target,
  TrendingDown,
  TrendingUp,
  Users,
} from 'lucide-react';
import { useEffect, useState } from 'react';

import recommendationsApi, {
  AnalyzedRecommendation,
  RecommendationsResponse,
} from '__api__/recommendationsApi';

import { cn } from '@/lib/utils';

import { RecommendationsBarChart } from '@/components/Recommendations/BarChart';
import { RecommendationsPieChart } from '@/components/Recommendations/PieChart';
import { RecommendationBadge } from '@/components/Recommendations/RecommendationBadge';
import { RecommendationsStatsCard } from '@/components/Recommendations/StatsCard';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function BrasilRecommendationsPage() {
  // Loading states
  const [isLoadingIbov, setIsLoadingIbov] = useState(true);
  const [isLoadingB3, setIsLoadingB3] = useState(true);
  const [isLoadingBuy, setIsLoadingBuy] = useState(true);
  const [isLoadingStrongBuy, setIsLoadingStrongBuy] = useState(true);

  // Error states
  const [ibovError, setIbovError] = useState<string | null>(null);
  const [b3Error, setB3Error] = useState<string | null>(null);
  const [buyError, setBuyError] = useState<string | null>(null);
  const [strongBuyError, setStrongBuyError] = useState<string | null>(null);

  // Data states
  const [ibovData, setIbovData] = useState<RecommendationsResponse | null>(
    null
  );
  const [b3Data, setB3Data] = useState<any>(null);
  const [buyData, setBuyData] = useState<RecommendationsResponse | null>(null);
  const [strongBuyData, setStrongBuyData] =
    useState<RecommendationsResponse | null>(null);

  // Search and sort states
  const [searchTerm, setSearchTerm] = useState('');
  const [sortConfig, setSortConfig] = useState<{
    key: string;
    direction: 'asc' | 'desc';
  }>({
    key: 'relevance',
    direction: 'asc',
  });
  const [filterRecommendation, setFilterRecommendation] =
    useState<string>('all');

  // Fetch data on component mount
  useEffect(() => {
    fetchIbovData();
    fetchB3Data();
    fetchBuyData();
    fetchStrongBuyData();
  }, []);

  // Fetch IBOV data
  const fetchIbovData = async () => {
    try {
      setIsLoadingIbov(true);
      setIbovError(null);
      const response = await recommendationsApi.getIbovAnalysis();

      if (response && response.data) {
        setIbovData(response.data);
      } else {
        throw new Error('No data received from API');
      }
    } catch (error) {
      console.error('Error fetching IBOV data:', error);
      setIbovError('Failed to fetch IBOV recommendations.');
    } finally {
      setIsLoadingIbov(false);
    }
  };

  // Fetch raw B3 data
  const fetchB3Data = async () => {
    try {
      setIsLoadingB3(true);
      setB3Error(null);
      const response = await recommendationsApi.getB3Recommendations();

      if (response && response.data) {
        setB3Data(response.data);
      } else {
        throw new Error('No data received from API');
      }
    } catch (error) {
      console.error('Error fetching B3 data:', error);
      setB3Error('Failed to fetch B3 recommendations.');
    } finally {
      setIsLoadingB3(false);
    }
  };

  // Fetch Buy recommendations
  const fetchBuyData = async () => {
    try {
      setIsLoadingBuy(true);
      setBuyError(null);
      const response = await recommendationsApi.getBuyRecommendations();

      if (response && response.data) {
        setBuyData(response.data);
      } else {
        throw new Error('No data received from API');
      }
    } catch (error) {
      console.error('Error fetching Buy data:', error);
      setBuyError('Failed to fetch Buy recommendations.');
    } finally {
      setIsLoadingBuy(false);
    }
  };

  // Fetch Strong Buy recommendations
  const fetchStrongBuyData = async () => {
    try {
      setIsLoadingStrongBuy(true);
      setStrongBuyError(null);
      const response = await recommendationsApi.getStrongBuyRecommendations();

      if (response && response.data) {
        setStrongBuyData(response.data);
      } else {
        throw new Error('No data received from API');
      }
    } catch (error) {
      console.error('Error fetching Strong Buy data:', error);
      setStrongBuyError('Failed to fetch Strong Buy recommendations.');
    } finally {
      setIsLoadingStrongBuy(false);
    }
  };

  // Filter results based on search term and recommendation filter
  const filterResults = (
    data: (AnalyzedRecommendation | any)[] | undefined
  ): (AnalyzedRecommendation | any)[] => {
    if (!data) return [];

    return data.filter((item) => {
      const matchesSearch =
        item.ticker?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        item.recommendationKey
          ?.toLowerCase()
          .includes(searchTerm.toLowerCase()) ||
        item.symbol?.toLowerCase().includes(searchTerm.toLowerCase());

      const matchesFilter =
        filterRecommendation === 'all' ||
        item.recommendationKey === filterRecommendation;

      return matchesSearch && matchesFilter;
    });
  };

  // Sort results based on sort configuration
  const sortResults = (
    data: (AnalyzedRecommendation | any)[] | undefined
  ): (AnalyzedRecommendation | any)[] => {
    if (!data) return [];

    return [...data].sort((a, b) => {
      const aValue = a[sortConfig.key as keyof typeof a];
      const bValue = b[sortConfig.key as keyof typeof b];

      if (aValue === undefined || bValue === undefined) return 0;

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc'
          ? aValue - bValue
          : bValue - aValue;
      }

      const aString = String(aValue).toLowerCase();
      const bString = String(bValue).toLowerCase();

      return sortConfig.direction === 'asc'
        ? aString.localeCompare(bString)
        : bString.localeCompare(aString);
    });
  };

  // Handle sort column click
  const handleSort = (key: string) => {
    setSortConfig((prev) => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc',
    }));
  };

  // Format recommendation key for display
  const formatRecommendationKey = (key: string) => {
    const keyMap: { [key: string]: string } = {
      strong_buy: 'Compra Forte',
      buy: 'Compra',
      hold: 'Manter',
      sell: 'Venda',
      strong_sell: 'Venda Forte',
      underperform: 'Abaixo do Mercado',
      none: 'Sem Recomendação',
    };
    return keyMap[key] || key;
  };

  // Render loading skeleton
  const renderLoading = () => (
    <div className='space-y-4'>
      <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
        <div className='md:col-span-2'>
          <Skeleton className='h-[380px] w-full' />
        </div>
        <div>
          <Skeleton className='h-[200px] w-full' />
        </div>
      </div>
      <Skeleton className='h-[400px] w-full' />
    </div>
  );

  // Render error state
  const renderError = (error: string | null) => (
    <Card className='border-destructive/50'>
      <CardContent className='flex items-center gap-3 p-6'>
        <AlertCircle className='h-5 w-5 text-destructive' />
        <div>
          <p className='font-medium text-destructive'>Erro ao carregar dados</p>
          <p className='text-sm text-muted-foreground'>{error}</p>
        </div>
        <Button
          variant='outline'
          size='sm'
          onClick={() => {
            fetchIbovData();
            fetchB3Data();
            fetchBuyData();
            fetchStrongBuyData();
          }}
        >
          <RefreshCw className='h-4 w-4 mr-2' />
          Tentar Novamente
        </Button>
      </CardContent>
    </Card>
  );

  // Render sort indicator
  const renderSortIndicator = (key: string) => {
    if (sortConfig.key !== key) return null;
    return sortConfig.direction === 'asc' ? (
      <ArrowUp className='ml-1 h-3 w-3' />
    ) : (
      <ArrowDown className='ml-1 h-3 w-3' />
    );
  };

  // Render performance metrics
  const renderPerformanceMetrics = (data: (AnalyzedRecommendation | any)[]) => {
    if (!data || data.length === 0) return null;

    const positiveReturns = data.filter(
      (item) =>
        typeof item.return_target_consensus === 'number' &&
        item.return_target_consensus > 0
    );
    const negativeReturns = data.filter(
      (item) =>
        typeof item.return_target_consensus === 'number' &&
        item.return_target_consensus < 0
    );

    const avgPositiveReturn =
      positiveReturns.length > 0
        ? positiveReturns.reduce(
            (sum, item) => sum + (item.return_target_consensus || 0),
            0
          ) / positiveReturns.length
        : 0;
    const avgNegativeReturn =
      negativeReturns.length > 0
        ? negativeReturns.reduce(
            (sum, item) => sum + (item.return_target_consensus || 0),
            0
          ) / negativeReturns.length
        : 0;

    return (
      <div className='grid grid-cols-1 md:grid-cols-4 gap-4 mb-6'>
        <Card className='p-4'>
          <div className='flex items-center gap-2'>
            <TrendingUp className='h-4 w-4 text-green-600' />
            <span className='text-sm font-medium'>Retorno Médio Positivo</span>
          </div>
          <p className='text-2xl font-bold text-green-600'>
            {(avgPositiveReturn * 100).toFixed(2)}%
          </p>
        </Card>

        <Card className='p-4'>
          <div className='flex items-center gap-2'>
            <TrendingDown className='h-4 w-4 text-red-600' />
            <span className='text-sm font-medium'>Retorno Médio Negativo</span>
          </div>
          <p className='text-2xl font-bold text-red-600'>
            {(avgNegativeReturn * 100).toFixed(2)}%
          </p>
        </Card>

        <Card className='p-4'>
          <div className='flex items-center gap-2'>
            <BarChart3 className='h-4 w-4 text-blue-600' />
            <span className='text-sm font-medium'>Total de Ativos</span>
          </div>
          <p className='text-2xl font-bold'>{data.length}</p>
        </Card>

        <Card className='p-4'>
          <div className='flex items-center gap-2'>
            <ClipboardList className='h-4 w-4 text-purple-600' />
            <span className='text-sm font-medium'>Analistas Ativos</span>
          </div>
          <p className='text-2xl font-bold'>
            {Math.max(...data.map((item) => item.numberOfAnalystOpinions || 0))}
          </p>
        </Card>
      </div>
    );
  };

  // IBOV tab content
  const renderIbovTab = () => {
    if (isLoadingIbov) return renderLoading();
    if (ibovError) return renderError(ibovError);

    const filteredData = filterResults(
      ibovData?.results as (AnalyzedRecommendation | any)[]
    );
    const sortedData = sortResults(filteredData);

    return (
      <div className='space-y-6'>
        {/* Performance Metrics */}
        {renderPerformanceMetrics(
          ibovData?.results as (AnalyzedRecommendation | any)[]
        )}

        {/* IBOV Charts and Stats */}
        <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
          <div className='md:col-span-2'>
            <RecommendationsPieChart
              data={ibovData?.results as AnalyzedRecommendation[]}
              translations={{
                title: 'Distribuição de Recomendações - IBOV',
                tooltipTitle: 'Tipo de Recomendação',
                keys: {
                  strong_buy: 'Compra Forte',
                  buy: 'Compra',
                  hold: 'Manter',
                  sell: 'Venda',
                  strong_sell: 'Venda Forte',
                  underperform: 'Abaixo do Mercado',
                },
              }}
            />
          </div>
          <div>
            <RecommendationsStatsCard
              data={ibovData?.results as AnalyzedRecommendation[]}
              title='Estatísticas IBOV'
            />
          </div>
        </div>

        {/* Additional Charts */}
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          <RecommendationsBarChart
            data={ibovData?.results as AnalyzedRecommendation[]}
            type='return'
            title='Top 10 - Maiores Retornos Esperados'
          />
          <RecommendationsBarChart
            data={ibovData?.results as AnalyzedRecommendation[]}
            type='price'
            title='Top 10 - Maior Potencial de Valorização'
          />
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          <RecommendationsBarChart
            data={ibovData?.results as AnalyzedRecommendation[]}
            type='analysts'
            title='Top 10 - Maior Cobertura de Analistas'
          />
          <div className='bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-6 border'>
            <h3 className='text-lg font-semibold mb-4 text-blue-900'>
              Resumo Executivo
            </h3>
            <div className='space-y-3 text-sm text-blue-800'>
              <div className='flex justify-between'>
                <span>Total de Ativos Analisados:</span>
                <span className='font-medium'>
                  {ibovData?.results?.length || 0}
                </span>
              </div>
              <div className='flex justify-between'>
                <span>Recomendações de Compra:</span>
                <span className='font-medium'>
                  {ibovData?.results?.filter(
                    (item: any) =>
                      item.recommendationKey === 'strong_buy' ||
                      item.recommendationKey === 'buy'
                  ).length || 0}
                </span>
              </div>
              <div className='flex justify-between'>
                <span>Retorno Médio Esperado:</span>
                <span className='font-medium'>
                  {ibovData?.results?.length
                    ? `${(
                        ((ibovData.results as any[]).reduce(
                          (sum, item) =>
                            sum + (item.return_target_consensus || 0),
                          0
                        ) /
                          ibovData.results.length) *
                          100
                      ).toFixed(2)}%`
                    : 'N/A'}
                </span>
              </div>
              <div className='flex justify-between'>
                <span>Última Atualização:</span>
                <span className='font-medium'>
                  {new Date().toLocaleDateString('pt-BR')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* IBOV Table */}
        <Card>
          <CardHeader className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
            <div>
              <CardTitle>Recomendações IBOV</CardTitle>
              <p className='text-sm text-muted-foreground mt-1'>
                {sortedData.length} ativos encontrados
              </p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' size='sm'>
                <Download className='h-4 w-4 mr-2' />
                Exportar
              </Button>
              <Button variant='outline' size='sm' onClick={fetchIbovData}>
                <RefreshCw className='h-4 w-4 mr-2' />
                Atualizar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className='rounded-md border'>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('relevance')}
                    >
                      <div className='flex items-center'>
                        Relevância {renderSortIndicator('relevance')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('ticker')}
                    >
                      <div className='flex items-center'>
                        Ticker {renderSortIndicator('ticker')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('numberOfAnalystOpinions')}
                    >
                      <div className='flex items-center'>
                        Analistas{' '}
                        {renderSortIndicator('numberOfAnalystOpinions')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('recommendationKey')}
                    >
                      <div className='flex items-center'>
                        Recomendação {renderSortIndicator('recommendationKey')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('currentPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Atual {renderSortIndicator('currentPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('targetMedianPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Mediano {renderSortIndicator('targetMedianPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('targetHighPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Alvo {renderSortIndicator('targetHighPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('price_target_consensus')}
                    >
                      <div className='flex items-center justify-end'>
                        Consenso {renderSortIndicator('price_target_consensus')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('return_target_consensus')}
                    >
                      <div className='flex items-center justify-end'>
                        Retorno Esperado{' '}
                        {renderSortIndicator('return_target_consensus')}
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedData.length > 0 ? (
                    sortedData.map((item, index) => (
                      <TableRow
                        key={item.ticker || index}
                        className='hover:bg-muted/50'
                      >
                        <TableCell>
                          <Badge variant='outline' className='text-xs'>
                            {item.relevance}
                          </Badge>
                        </TableCell>
                        <TableCell className='font-medium'>
                          {item.ticker}
                        </TableCell>
                        <TableCell>
                          <Badge variant='secondary' className='text-xs'>
                            {item.numberOfAnalystOpinions}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <RecommendationBadge
                            recommendationKey={item.recommendationKey}
                            className='text-xs'
                          />
                        </TableCell>
                        <TableCell className='text-right font-medium'>
                          R$ {item.currentPrice.toFixed(2)}
                        </TableCell>
                        <TableCell className='text-right'>
                          R$ {item.targetMedianPrice.toFixed(2)}
                        </TableCell>
                        <TableCell className='text-right'>
                          R$ {item.targetHighPrice.toFixed(2)}
                        </TableCell>
                        <TableCell className='text-right'>
                          R$ {item.price_target_consensus.toFixed(2)}
                        </TableCell>
                        <TableCell
                          className={cn(
                            'text-right font-medium',
                            item.return_target_consensus > 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          )}
                        >
                          {(item.return_target_consensus * 100).toFixed(2)}%
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={9} className='h-24 text-center'>
                        <div className='flex flex-col items-center gap-2'>
                          <AlertCircle className='h-8 w-8 text-muted-foreground' />
                          <p className='text-muted-foreground'>
                            Nenhum resultado encontrado.
                          </p>
                          <p className='text-sm text-muted-foreground'>
                            Tente ajustar os filtros de busca.
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  // B3 tab content
  const renderB3Tab = () => {
    if (isLoadingB3) return renderLoading();
    if (b3Error) return renderError(b3Error);

    if (!b3Data || !b3Data.results) {
      return renderError(
        'Os dados retornados pela API não estão no formato esperado.'
      );
    }

    // Transform the data from object format (where keys are tickers) to array format
    const allData = Object.entries(b3Data.results)
      .map(([ticker, data]) => {
        if (typeof data === 'object' && data !== null) {
          return {
            ticker,
            ...(data as any),
          };
        } else {
          return { ticker };
        }
      })
      .filter((item) =>
        item.ticker.toLowerCase().includes(searchTerm.toLowerCase())
      );

    if (allData.length === 0) {
      return (
        <Card>
          <CardHeader>
            <CardTitle>Recomendações B3</CardTitle>
          </CardHeader>
          <CardContent className='text-center'>
            <div className='flex flex-col items-center gap-2 py-6'>
              <AlertCircle className='h-8 w-8 text-muted-foreground' />
              <p className='text-muted-foreground'>
                Nenhuma recomendação B3 encontrada.
              </p>
              <p className='text-sm text-muted-foreground'>
                Tente ajustar os filtros de busca.
              </p>
            </div>
          </CardContent>
        </Card>
      );
    }

    // Sort data
    const sortedData = [...allData].sort((a, b) => {
      const aValue = a[sortConfig.key as keyof typeof a];
      const bValue = b[sortConfig.key as keyof typeof b];

      if (aValue === undefined || bValue === undefined) return 0;

      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortConfig.direction === 'asc'
          ? aValue - bValue
          : bValue - aValue;
      }

      const aString = String(aValue).toLowerCase();
      const bString = String(bValue).toLowerCase();

      return sortConfig.direction === 'asc'
        ? aString.localeCompare(bString)
        : bString.localeCompare(aString);
    });

    // Get recommendation distribution for pie chart
    const recommendationCounts: { [key: string]: number } = {};
    allData.forEach((item) => {
      const key = item.recommendationKey || 'unknown';
      recommendationCounts[key] = (recommendationCounts[key] || 0) + 1;
    });

    const pieChartData = Object.keys(recommendationCounts).map((key) => ({
      ticker: '',
      recommendationKey: key,
      numberOfAnalystOpinions: recommendationCounts[key],
      currentPrice: 0,
      price_target_consensus: 0,
      combined_score: 0,
      relevance: 0,
      return_target_consensus: 0,
      targetHighPrice: 0,
      targetMedianPrice: 0,
    }));

    // Add 'return_target_consensus' where possible
    const dataWithReturns = allData.map((item) => {
      if (
        item.targetMedianPrice &&
        item.currentPrice &&
        item.currentPrice > 0
      ) {
        const returnTarget =
          (item.targetMedianPrice - item.currentPrice) / item.currentPrice;
        return {
          ...item,
          return_target_consensus: returnTarget,
        };
      }
      return item;
    });

    return (
      <div className='space-y-6'>
        {/* Performance Metrics */}
        {renderPerformanceMetrics(dataWithReturns)}

        {/* B3 Charts and Stats */}
        <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
          <div className='md:col-span-2'>
            {Object.keys(recommendationCounts).length > 0 && (
              <RecommendationsPieChart
                data={pieChartData as AnalyzedRecommendation[]}
                translations={{
                  title: 'Distribuição de Recomendações - B3',
                  tooltipTitle: 'Tipo de Recomendação',
                  keys: {
                    strong_buy: 'Compra Forte',
                    buy: 'Compra',
                    hold: 'Manter',
                    sell: 'Venda',
                    strong_sell: 'Venda Forte',
                    underperform: 'Abaixo do Mercado',
                    unknown: 'Não especificado',
                  },
                }}
              />
            )}
          </div>
          <div>
            <RecommendationsStatsCard
              data={dataWithReturns}
              title='Estatísticas B3'
            />
          </div>
        </div>

        {/* Additional Charts for B3 */}
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          <RecommendationsBarChart
            data={dataWithReturns}
            type='return'
            title='Top 10 B3 - Maiores Retornos Esperados'
          />
          <RecommendationsBarChart
            data={dataWithReturns}
            type='price'
            title='Top 10 B3 - Maior Potencial de Valorização'
          />
        </div>

        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          <RecommendationsBarChart
            data={dataWithReturns}
            type='analysts'
            title='Top 10 B3 - Maior Cobertura de Analistas'
          />
          <div className='bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-6 border'>
            <h3 className='text-lg font-semibold mb-4 text-purple-900'>
              Resumo Executivo B3
            </h3>
            <div className='space-y-3 text-sm text-purple-800'>
              <div className='flex justify-between'>
                <span>Total de Ativos Analisados:</span>
                <span className='font-medium'>{dataWithReturns.length}</span>
              </div>
              <div className='flex justify-between'>
                <span>Recomendações de Compra:</span>
                <span className='font-medium'>
                  {
                    dataWithReturns.filter(
                      (item: any) =>
                        item.recommendationKey === 'strong_buy' ||
                        item.recommendationKey === 'buy'
                    ).length
                  }
                </span>
              </div>
              <div className='flex justify-between'>
                <span>Retorno Médio Esperado:</span>
                <span className='font-medium'>
                  {dataWithReturns.length
                    ? `${(
                        (dataWithReturns.reduce(
                          (sum, item) =>
                            sum + (item.return_target_consensus || 0),
                          0
                        ) /
                          dataWithReturns.length) *
                          100
                      ).toFixed(2)}%`
                    : 'N/A'}
                </span>
              </div>
              <div className='flex justify-between'>
                <span>Última Atualização:</span>
                <span className='font-medium'>
                  {new Date().toLocaleDateString('pt-BR')}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* B3 Table */}
        <Card>
          <CardHeader className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
            <div>
              <CardTitle>Recomendações B3</CardTitle>
              <p className='text-sm text-muted-foreground mt-1'>
                {sortedData.length} ativos encontrados
              </p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' size='sm'>
                <Download className='h-4 w-4 mr-2' />
                Exportar
              </Button>
              <Button variant='outline' size='sm' onClick={fetchB3Data}>
                <RefreshCw className='h-4 w-4 mr-2' />
                Atualizar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className='rounded-md border'>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('ticker')}
                    >
                      <div className='flex items-center'>
                        Ticker {renderSortIndicator('ticker')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('numberOfAnalystOpinions')}
                    >
                      <div className='flex items-center'>
                        Analistas{' '}
                        {renderSortIndicator('numberOfAnalystOpinions')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('recommendationKey')}
                    >
                      <div className='flex items-center'>
                        Recomendação {renderSortIndicator('recommendationKey')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('currentPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Atual {renderSortIndicator('currentPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('targetLowPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Mínimo {renderSortIndicator('targetLowPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('targetMedianPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Mediano {renderSortIndicator('targetMedianPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('targetHighPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Máximo {renderSortIndicator('targetHighPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('return_target_consensus')}
                    >
                      <div className='flex items-center justify-end'>
                        Retorno Esperado{' '}
                        {renderSortIndicator('return_target_consensus')}
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {sortedData.length > 0 ? (
                    sortedData.map((item, index) => (
                      <TableRow
                        key={item.ticker || index}
                        className='hover:bg-muted/50'
                      >
                        <TableCell className='font-medium'>
                          {item.ticker}
                        </TableCell>
                        <TableCell>
                          <Badge variant='secondary' className='text-xs'>
                            {item.numberOfAnalystOpinions || 'N/A'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <RecommendationBadge
                            recommendationKey={item.recommendationKey}
                            className='text-xs'
                          />
                        </TableCell>
                        <TableCell className='text-right font-medium'>
                          {item.currentPrice != null
                            ? `R$ ${Number(item.currentPrice).toFixed(2)}`
                            : 'N/A'}
                        </TableCell>
                        <TableCell className='text-right'>
                          {item.targetLowPrice != null
                            ? `R$ ${Number(item.targetLowPrice).toFixed(2)}`
                            : 'N/A'}
                        </TableCell>
                        <TableCell className='text-right'>
                          {item.targetMedianPrice != null
                            ? `R$ ${Number(item.targetMedianPrice).toFixed(2)}`
                            : 'N/A'}
                        </TableCell>
                        <TableCell className='text-right'>
                          {item.targetHighPrice != null
                            ? `R$ ${Number(item.targetHighPrice).toFixed(2)}`
                            : 'N/A'}
                        </TableCell>
                        <TableCell
                          className={cn(
                            'text-right font-medium',
                            item.return_target_consensus > 0
                              ? 'text-green-600'
                              : item.return_target_consensus < 0
                                ? 'text-red-600'
                                : ''
                          )}
                        >
                          {item.return_target_consensus != null
                            ? `${(item.return_target_consensus * 100).toFixed(2)}%`
                            : 'N/A'}
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} className='h-24 text-center'>
                        <div className='flex flex-col items-center gap-2'>
                          <AlertCircle className='h-8 w-8 text-muted-foreground' />
                          <p className='text-muted-foreground'>
                            Nenhum resultado encontrado.
                          </p>
                          <p className='text-sm text-muted-foreground'>
                            Tente ajustar os filtros de busca.
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  // Todas as Compras tab content
  const renderTodasComprasTab = () => {
    const combinedData = [
      ...(strongBuyData?.results || []),
      ...(buyData?.results || []),
    ];

    const filteredData = filterResults(combinedData);
    const sortedStrongBuyData = sortResults(
      filteredData.filter((item) => item.recommendationKey === 'strong_buy')
    );
    const sortedBuyData = sortResults(
      filteredData.filter((item) => item.recommendationKey === 'buy')
    );

    const renderRecommendationTable = (
      data: (AnalyzedRecommendation | any)[],
      title: string,
      error: string | null
    ) => {
      if (error) return <div className='text-destructive mb-4'>{error}</div>;

      return (
        <Card className='mb-6'>
          <CardHeader className='flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4'>
            <div>
              <CardTitle>{title}</CardTitle>
              <p className='text-sm text-muted-foreground mt-1'>
                {data.length} ativos encontrados
              </p>
            </div>
            <div className='flex gap-2'>
              <Button variant='outline' size='sm'>
                <Download className='h-4 w-4 mr-2' />
                Exportar
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <div className='rounded-md border'>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('relevance')}
                    >
                      <div className='flex items-center'>
                        Relevância {renderSortIndicator('relevance')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('ticker')}
                    >
                      <div className='flex items-center'>
                        Ticker {renderSortIndicator('ticker')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer'
                      onClick={() => handleSort('numberOfAnalystOpinions')}
                    >
                      <div className='flex items-center'>
                        Analistas{' '}
                        {renderSortIndicator('numberOfAnalystOpinions')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('currentPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Atual {renderSortIndicator('currentPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('targetMedianPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Mediano {renderSortIndicator('targetMedianPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('targetHighPrice')}
                    >
                      <div className='flex items-center justify-end'>
                        Preço Máximo {renderSortIndicator('targetHighPrice')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('price_target_consensus')}
                    >
                      <div className='flex items-center justify-end'>
                        Consenso {renderSortIndicator('price_target_consensus')}
                      </div>
                    </TableHead>
                    <TableHead
                      className='cursor-pointer text-right'
                      onClick={() => handleSort('return_target_consensus')}
                    >
                      <div className='flex items-center justify-end'>
                        Retorno Esperado{' '}
                        {renderSortIndicator('return_target_consensus')}
                      </div>
                    </TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {data.length > 0 ? (
                    data.map((item, index) => (
                      <TableRow
                        key={item.ticker || index}
                        className='hover:bg-muted/50'
                      >
                        <TableCell>
                          <Badge variant='outline' className='text-xs'>
                            {item.relevance}
                          </Badge>
                        </TableCell>
                        <TableCell className='font-medium'>
                          {item.ticker}
                        </TableCell>
                        <TableCell>
                          <Badge variant='secondary' className='text-xs'>
                            {item.numberOfAnalystOpinions}
                          </Badge>
                        </TableCell>
                        <TableCell className='text-right font-medium'>
                          R$ {item.currentPrice.toFixed(2)}
                        </TableCell>
                        <TableCell className='text-right'>
                          R$ {item.targetMedianPrice.toFixed(2)}
                        </TableCell>
                        <TableCell className='text-right'>
                          R$ {item.targetHighPrice.toFixed(2)}
                        </TableCell>
                        <TableCell className='text-right'>
                          R$ {item.price_target_consensus.toFixed(2)}
                        </TableCell>
                        <TableCell
                          className={cn(
                            'text-right font-medium',
                            item.return_target_consensus > 0
                              ? 'text-green-600'
                              : 'text-red-600'
                          )}
                        >
                          {(item.return_target_consensus * 100).toFixed(2)}%
                        </TableCell>
                      </TableRow>
                    ))
                  ) : (
                    <TableRow>
                      <TableCell colSpan={8} className='h-24 text-center'>
                        <div className='flex flex-col items-center gap-2'>
                          <AlertCircle className='h-8 w-8 text-muted-foreground' />
                          <p className='text-muted-foreground'>
                            Nenhum resultado encontrado.
                          </p>
                          <p className='text-sm text-muted-foreground'>
                            Tente ajustar os filtros de busca.
                          </p>
                        </div>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>
          </CardContent>
        </Card>
      );
    };

    return (
      <div className='space-y-6'>
        {/* Performance Metrics */}
        {renderPerformanceMetrics(combinedData)}

        {/* Stats Card for combined buy recommendations */}
        <div className='md:w-1/3 mb-6'>
          <RecommendationsStatsCard
            data={combinedData}
            title='Estatísticas de Recomendações de Compra'
          />
        </div>

        {/* Strong Buy Table */}
        {renderRecommendationTable(
          sortedStrongBuyData,
          'Recomendações de Compra Forte',
          strongBuyError
        )}

        {/* Buy Table */}
        {renderRecommendationTable(
          sortedBuyData,
          'Recomendações de Compra',
          buyError
        )}
      </div>
    );
  };

  return (
    <div className='flex-1 space-y-4 p-4 pt-6 md:p-8'>
      {/* Header Section */}
      <div className='flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4'>
        <div>
          <h1 className='text-3xl font-bold tracking-tight'>
            Recomendações de Ações Brasileiras
          </h1>
          <p className='text-muted-foreground'>
            Analise as recomendações de analistas financeiros para o mercado
            brasileiro
          </p>
        </div>

        {/* Quick Actions */}
        <div className='flex gap-2'>
          <Button
            variant='outline'
            onClick={() => {
              fetchIbovData();
              fetchB3Data();
              fetchBuyData();
              fetchStrongBuyData();
            }}
          >
            <RefreshCw className='h-4 w-4 mr-2' />
            Atualizar Todos
          </Button>
        </div>
      </div>

      {/* Search and Filter Controls */}
      <div className='flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between'>
        <div className='flex gap-4 items-center'>
          <div className='relative'>
            <Search className='absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground' />
            <Input
              type='search'
              placeholder='Buscar por ticker ou recomendação...'
              className='w-full appearance-none pl-8 md:w-[300px]'
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <Select
            value={filterRecommendation}
            onValueChange={setFilterRecommendation}
          >
            <SelectTrigger className='w-[180px]'>
              <SelectValue placeholder='Filtrar por recomendação' />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value='all'>Todas as Recomendações</SelectItem>
              <SelectItem value='strong_buy'>Compra Forte</SelectItem>
              <SelectItem value='buy'>Compra</SelectItem>
              <SelectItem value='hold'>Manter</SelectItem>
              <SelectItem value='sell'>Venda</SelectItem>
              <SelectItem value='strong_sell'>Venda Forte</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className='text-sm text-muted-foreground'>
          Última atualização: {new Date().toLocaleString('pt-BR')}
        </div>
      </div>

      {/* Market Overview Summary */}
      <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
        <Card className='p-4 bg-gradient-to-br from-green-50 to-emerald-50 border-green-200'>
          <div className='flex items-center gap-3'>
            <div className='p-2 bg-green-100 rounded-lg'>
              <TrendingUp className='h-5 w-5 text-green-600' />
            </div>
            <div>
              <p className='text-sm font-medium text-green-800'>
                Total de Ativos
              </p>
              <p className='text-2xl font-bold text-green-900'>
                {(ibovData?.results?.length || 0) +
                  (b3Data?.results ? Object.keys(b3Data.results).length : 0)}
              </p>
            </div>
          </div>
        </Card>

        <Card className='p-4 bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-200'>
          <div className='flex items-center gap-3'>
            <div className='p-2 bg-blue-100 rounded-lg'>
              <Users className='h-5 w-5 text-blue-600' />
            </div>
            <div>
              <p className='text-sm font-medium text-blue-800'>
                Analistas Ativos
              </p>
              <p className='text-2xl font-bold text-blue-900'>
                {Math.max(
                  ...(ibovData?.results?.map(
                    (item: any) => item.numberOfAnalystOpinions || 0
                  ) || []),
                  ...(b3Data?.results
                    ? Object.values(b3Data.results).map(
                        (item: any) => item.numberOfAnalystOpinions || 0
                      )
                    : [])
                )}
              </p>
            </div>
          </div>
        </Card>

        <Card className='p-4 bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200'>
          <div className='flex items-center gap-3'>
            <div className='p-2 bg-purple-100 rounded-lg'>
              <Target className='h-5 w-5 text-purple-600' />
            </div>
            <div>
              <p className='text-sm font-medium text-purple-800'>
                Compra Forte
              </p>
              <p className='text-2xl font-bold text-purple-900'>
                {(ibovData?.results?.filter(
                  (item: AnalyzedRecommendation | any) =>
                    item.recommendationKey === 'strong_buy'
                ).length || 0) +
                  (b3Data?.results
                    ? Object.values(
                        b3Data.results as Record<string, any>
                      ).filter(
                        (item: any) => item.recommendationKey === 'strong_buy'
                      ).length
                    : 0)}
              </p>
            </div>
          </div>
        </Card>

        <Card className='p-4 bg-gradient-to-br from-orange-50 to-red-50 border-orange-200'>
          <div className='flex items-center gap-3'>
            <div className='p-2 bg-orange-100 rounded-lg'>
              <BarChart3 className='h-5 w-5 text-orange-600' />
            </div>
            <div>
              <p className='text-sm font-medium text-orange-800'>
                Retorno Médio
              </p>
              <p className='text-2xl font-bold text-orange-900'>
                {(() => {
                  const allData = [
                    ...(ibovData?.results || []),
                    ...(b3Data?.results ? Object.values(b3Data.results) : []),
                  ];
                  const returns = allData.filter(
                    (item: any) =>
                      typeof item.return_target_consensus === 'number'
                  );
                  if (returns.length === 0) return 'N/A';
                  const avg =
                    returns.reduce(
                      (sum: number, item: any) =>
                        sum + (item.return_target_consensus || 0),
                      0
                    ) / returns.length;
                  return `${(avg * 100).toFixed(1)}%`;
                })()}
              </p>
            </div>
          </div>
        </Card>
      </div>

      {/* Main Content Tabs */}
      <Tabs defaultValue='ibov' className='space-y-4'>
        <TabsList className='grid w-full grid-cols-3'>
          <TabsTrigger value='ibov'>IBOV</TabsTrigger>
          <TabsTrigger value='b3'>B3</TabsTrigger>
          <TabsTrigger value='todas-compras'>Todas as Compras</TabsTrigger>
        </TabsList>

        <TabsContent value='ibov' className='mt-0 border-0 p-0'>
          {renderIbovTab()}
        </TabsContent>

        <TabsContent value='b3' className='mt-0 border-0 p-0'>
          {renderB3Tab()}
        </TabsContent>

        <TabsContent value='todas-compras' className='mt-0 border-0 p-0'>
          {renderTodasComprasTab()}
        </TabsContent>
      </Tabs>
    </div>
  );
}
