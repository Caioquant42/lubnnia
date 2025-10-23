'use client';

import { AlertCircle, ArrowRight, Search } from 'lucide-react';
import { useEffect, useState } from 'react';

import {
  fetchStocksVolatilityData,
  getMarketSentiment,
  StockVolatilityData,
} from '__api__/volatilityApi';

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { StockVolatilityDetail } from '@/components/Volatility/StockVolatilityDetail';
import { VolatilityDataTable } from '@/components/Volatility/VolatilityDataTable';
import { VolatilityDistributionChart } from '@/components/Volatility/VolatilityDistributionChart';
import { VolatilityStatusCard } from '@/components/Volatility/VolatilityStatusCard';

export default function VolatilityPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [allStocks, setAllStocks] = useState<StockVolatilityData[]>([]);
  const [searchSymbol, setSearchSymbol] = useState('');
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  const [selectedStock, setSelectedStock] =
    useState<StockVolatilityData | null>(null);
  const [activeTab, setActiveTab] = useState('market');

  // Fetch all stocks volatility data on component mount
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetchStocksVolatilityData({
          sort_by: 'iv_ewma_ratio',
          sort_order: 'desc',
        });
        setAllStocks(response.results);
        setError(null);
      } catch (err) {
        console.error('Error fetching volatility data:', err);
        setError(
          'Falha ao carregar dados de volatilidade. Por favor, tente novamente mais tarde.'
        );
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  // Handle stock selection
  const handleStockSelect = (symbol: string) => {
    const stock = allStocks.find((s) => s.symbol === symbol);
    if (stock) {
      setSelectedStock(stock);
      setSelectedSymbol(symbol);
      setActiveTab('stock');
    }
  };

  // Handle search submission
  const handleSearch = () => {
    if (searchSymbol.trim()) {
      const stock = allStocks.find(
        (s) => s.symbol.toUpperCase() === searchSymbol.toUpperCase()
      );
      if (stock) {
        setSelectedStock(stock);
        setSelectedSymbol(stock.symbol);
        setActiveTab('stock');
      } else {
        setError(`Símbolo "${searchSymbol}" não encontrado`);
        setTimeout(() => setError(null), 3000);
      }
    }
  };

  // Calculate market sentiment
  const marketSentiment = getMarketSentiment(allStocks);

  // Get top stocks with highest and lowest IV/EWMA ratios
  const topHighVolatilityStocks = [...allStocks]
    .filter(
      (stock) =>
        stock.iv_ewma_ratio !== undefined &&
        !isNaN(stock.iv_ewma_ratio) &&
        stock.iv_ewma_ratio > 0.01 // Filter out zero or very low values
    )
    .sort((a, b) => b.iv_ewma_ratio - a.iv_ewma_ratio)
    .slice(0, 5);

  const topLowVolatilityStocks = [...allStocks]
    .filter(
      (stock) =>
        stock.iv_ewma_ratio !== undefined &&
        !isNaN(stock.iv_ewma_ratio) &&
        stock.iv_ewma_ratio > 0.01 // Filter out zero or very low values
    )
    .sort((a, b) => a.iv_ewma_ratio - b.iv_ewma_ratio)
    .slice(0, 5);

  return (
    <div className='container mx-auto py-4 space-y-6'>
      <div className='flex flex-col gap-2'>
        <h1 className='text-3xl font-bold'>Análise de Volatilidade</h1>
        <p className='text-muted-foreground'>
          Análise abrangente da volatilidade do mercado usando razão IV/EWMA e
          outras métricas.
        </p>
      </div>

      {/* Search Bar */}
      <div className='flex gap-2'>
        <div className='relative flex-1'>
          <Search className='absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground' />
          <Input
            placeholder='Buscar por símbolo (ex. PETR4)'
            value={searchSymbol}
            onChange={(e) => setSearchSymbol(e.target.value)}
            className='pl-8'
            onKeyUp={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>
        <Button onClick={handleSearch}>Analisar</Button>
      </div>

      {/* Error Alert */}
      {error && (
        <Alert variant='destructive'>
          <AlertCircle className='h-4 w-4' />
          <AlertTitle>Erro</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {/* Loading State */}
      {loading ? (
        <div className='space-y-4'>
          <Skeleton className='h-[120px] w-full' />
          <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4'>
            <Skeleton className='h-[100px] w-full' />
            <Skeleton className='h-[100px] w-full' />
            <Skeleton className='h-[100px] w-full' />
            <Skeleton className='h-[100px] w-full' />
          </div>
          <Skeleton className='h-[300px] w-full' />
        </div>
      ) : (
        <Tabs value={activeTab} onValueChange={setActiveTab} className='w-full'>
          <TabsList className='grid w-full grid-cols-2'>
            <TabsTrigger value='market'>Visão Geral do Mercado</TabsTrigger>
            <TabsTrigger value='stock' disabled={!selectedStock}>
              Análise da Ação {selectedSymbol && `(${selectedSymbol})`}
            </TabsTrigger>
          </TabsList>

          <TabsContent value='market' className='space-y-6'>
            {/* Market Sentiment */}
            <Card>
              <CardHeader>
                <CardTitle>Sentimento de Volatilidade do Mercado</CardTitle>
                <CardDescription>
                  Sentimento atual de volatilidade do mercado baseado na análise
                  da razão IV/EWMA.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className='grid gap-6'>
                  <div className='text-center'>
                    <h3 className='text-2xl font-bold'>
                      {marketSentiment.sentiment}
                    </h3>
                    <p className='text-muted-foreground mt-1'>
                      Razão Média IV/EWMA: {marketSentiment.ratioAvg.toFixed(2)}
                    </p>
                  </div>
                  <p>{marketSentiment.description}</p>
                </div>
              </CardContent>
            </Card>

            {/* Distribution Chart */}
            <VolatilityDistributionChart
              distribution={marketSentiment.distribution}
              title='Distribuição de Volatilidade'
              description='Distribuição das ações em diferentes categorias de volatilidade baseada na razão IV/EWMA.'
            />

            {/* High & Low Volatility Stocks */}
            <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
              <Card>
                <CardHeader>
                  <CardTitle>Ações com Maior Volatilidade</CardTitle>
                  <CardDescription>
                    Ações com as maiores razões IV/EWMA - volatilidade atual é
                    alta em relação aos níveis históricos.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='space-y-4'>
                    {topHighVolatilityStocks.length > 0 ? (
                      topHighVolatilityStocks.map((stock) => (
                        <div
                          key={stock.symbol}
                          className='flex items-center justify-between'
                        >
                          <div>
                            <div className='font-medium'>{stock.symbol}</div>
                            <div className='text-sm text-muted-foreground'>
                              {stock.name?.substring(0, 20)}
                              {stock.name?.length > 20 ? '...' : ''}
                            </div>
                          </div>
                          <div className='text-right'>
                            <div className='font-bold text-red-500'>
                              {stock.iv_ewma_ratio.toFixed(2)}
                            </div>
                            <Button
                              variant='ghost'
                              size='sm'
                              className='h-6 text-xs px-2'
                              onClick={() => handleStockSelect(stock.symbol)}
                            >
                              Detalhes <ArrowRight className='ml-1 h-3 w-3' />
                            </Button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className='text-center py-4'>
                        <p className='text-muted-foreground'>
                          Nenhuma ação com dados válidos de alta volatilidade
                          encontrada. Isso pode indicar problemas de qualidade
                          dos dados ou condições de mercado.
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Ações com Menor Volatilidade</CardTitle>
                  <CardDescription>
                    Ações com as menores razões IV/EWMA - volatilidade atual é
                    baixa em relação aos níveis históricos.
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='space-y-4'>
                    {topLowVolatilityStocks.length > 0 ? (
                      topLowVolatilityStocks.map((stock) => (
                        <div
                          key={stock.symbol}
                          className='flex items-center justify-between'
                        >
                          <div>
                            <div className='font-medium'>{stock.symbol}</div>
                            <div className='text-sm text-muted-foreground'>
                              {stock.name?.substring(0, 20)}
                              {stock.name?.length > 20 ? '...' : ''}
                            </div>
                          </div>
                          <div className='text-right'>
                            <div className='font-bold text-blue-500'>
                              {stock.iv_ewma_ratio.toFixed(2)}
                            </div>
                            <Button
                              variant='ghost'
                              size='sm'
                              className='h-6 text-xs px-2'
                              onClick={() => handleStockSelect(stock.symbol)}
                            >
                              Detalhes <ArrowRight className='ml-1 h-3 w-3' />
                            </Button>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className='text-center py-4'>
                        <p className='text-muted-foreground'>
                          Nenhuma ação com dados válidos de baixa volatilidade
                          encontrada. Isso pode indicar problemas de qualidade
                          dos dados ou condições de mercado.
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Full Data Table */}
            <Card>
              <CardHeader>
                <CardTitle>Dados de Volatilidade de Todas as Ações</CardTitle>
                <CardDescription>
                  Dados completos de volatilidade para todas as ações. Clique em
                  uma linha para ver análise detalhada.
                </CardDescription>
              </CardHeader>
              <CardContent>
                <VolatilityDataTable
                  data={allStocks}
                  onStockSelect={handleStockSelect}
                />
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value='stock' className='space-y-6'>
            {selectedStock ? (
              <>
                <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
                  <VolatilityStatusCard
                    title='Razão IV/EWMA'
                    symbol={selectedStock.symbol}
                    ratio={selectedStock.iv_ewma_ratio}
                    description='Volatilidade Implícita vs. Volatilidade Histórica'
                  />
                  <Card>
                    <CardHeader className='pb-2'>
                      <CardTitle className='text-md'>Percentis IV</CardTitle>
                      <CardDescription>
                        IV atual em relação aos ranges históricos
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className='space-y-2'>
                        <div className='flex justify-between'>
                          <span className='text-muted-foreground'>
                            Percentil 1 Ano:
                          </span>
                          <span className='font-medium'>
                            {selectedStock.iv_1y_percentile?.toFixed(1)}%
                          </span>
                        </div>
                        <div className='flex justify-between'>
                          <span className='text-muted-foreground'>
                            Percentil 6 Meses:
                          </span>
                          <span className='font-medium'>
                            {selectedStock.iv_6m_percentile?.toFixed(1)}%
                          </span>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                  <Card>
                    <CardHeader className='pb-2'>
                      <CardTitle className='text-md'>Beta da Ação</CardTitle>
                      <CardDescription>
                        Sensibilidade aos movimentos do mercado
                      </CardDescription>
                    </CardHeader>
                    <CardContent className='text-center'>
                      <div className='text-3xl font-bold'>
                        {selectedStock.beta_ibov?.toFixed(2)}
                      </div>
                      <div className='mt-2 text-sm text-muted-foreground'>
                        {selectedStock.beta_ibov > 1.3
                          ? 'Alta sensibilidade aos movimentos do mercado'
                          : selectedStock.beta_ibov < 0.7
                            ? 'Baixa sensibilidade aos movimentos do mercado'
                            : 'Sensibilidade média aos movimentos do mercado'}
                      </div>
                    </CardContent>
                  </Card>
                </div>

                <StockVolatilityDetail stock={selectedStock} />
              </>
            ) : (
              <div className='text-center py-10'>
                <h3 className='text-lg font-medium'>
                  Nenhuma ação selecionada
                </h3>
                <p className='text-muted-foreground'>
                  Busque por uma ação ou selecione uma da visão geral do
                  mercado.
                </p>
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
