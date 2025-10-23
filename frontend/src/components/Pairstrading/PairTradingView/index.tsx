'use client';

import { AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

import { getPairDetails } from '__api__/pairstrading';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
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

interface PairTradingViewProps {
  asset1: string;
  asset2: string;
  period: 'last_6_months' | 'last_12_months';
}

const PairTradingView: React.FC<PairTradingViewProps> = ({
  asset1,
  asset2,
  period,
}) => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [pairData, setPairData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<string>('price');

  useEffect(() => {
    const fetchPairDetails = async () => {
      try {
        setLoading(true);
        setError(null);

        const data = await getPairDetails(asset1, asset2, period);
        setPairData(data);
      } catch (err) {
        console.error(`Error fetching details for ${asset1}/${asset2}:`, err);
        setError(
          `Falha ao carregar detalhes do par. Tente novamente mais tarde.`
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPairDetails();
  }, [asset1, asset2, period]);

  // Format date for the chart
  const formatDate = (dateString: string) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', { month: 'short', day: 'numeric' });
  };

  return (
    <div className='space-y-4'>
      {error && (
        <Alert variant='destructive'>
          <AlertCircle className='h-4 w-4' />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {loading ? (
        <div className='space-y-4'>
          <Skeleton className='h-[400px] w-full' />
          <Skeleton className='h-[200px] w-full' />
        </div>
      ) : pairData ? (
        <div className='space-y-6'>
          <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
            <TabsList className='mb-4'>
              <TabsTrigger value='price'>Comparação de Preços</TabsTrigger>
              <TabsTrigger value='ratio'>Razão de Preços</TabsTrigger>
              <TabsTrigger value='spread'>Análise do Spread</TabsTrigger>
              <TabsTrigger value='stats'>Estatísticas</TabsTrigger>
            </TabsList>

            <TabsContent value='price'>
              <Card>
                <CardHeader>
                  <CardTitle>Comparação de Preços</CardTitle>
                  <CardDescription>
                    Evolução dos preços de {asset1} vs {asset2} ao longo do
                    tempo
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='h-[300px] flex items-center justify-center text-muted-foreground'>
                    Gráfico de comparação de preços será implementado aqui
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value='ratio'>
              <Card>
                <CardHeader>
                  <CardTitle>Razão de Preços</CardTitle>
                  <CardDescription>
                    Razão entre os preços de {asset1} e {asset2}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='h-[300px] flex items-center justify-center text-muted-foreground'>
                    Gráfico da razão de preços será implementado aqui
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value='spread'>
              <Card>
                <CardHeader>
                  <CardTitle>Análise do Spread</CardTitle>
                  <CardDescription>
                    Spread entre os preços normalizados e oportunidades de
                    trading
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='h-[300px] flex items-center justify-center text-muted-foreground'>
                    Gráfico de análise do spread será implementado aqui
                  </div>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value='stats'>
              <Card>
                <CardHeader>
                  <CardTitle>Estatísticas do Par</CardTitle>
                  <CardDescription>
                    Métricas estatísticas e indicadores de cointegração
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className='grid grid-cols-1 md:grid-cols-2 gap-4'>
                    <div>
                      <h4 className='font-medium mb-2'>
                        Métricas de Cointegração
                      </h4>
                      <div className='space-y-2 text-sm'>
                        <div className='flex justify-between'>
                          <span>Valor P:</span>
                          <span className='font-medium'>
                            {pairData.p_value?.toFixed(4) || 'N/A'}
                          </span>
                        </div>
                        <div className='flex justify-between'>
                          <span>Beta:</span>
                          <span className='font-medium'>
                            {pairData.beta?.toFixed(3) || 'N/A'}
                          </span>
                        </div>
                        <div className='flex justify-between'>
                          <span>Meia-Vida:</span>
                          <span className='font-medium'>
                            {pairData.half_life
                              ? Math.round(pairData.half_life)
                              : 'N/A'}{' '}
                            dias
                          </span>
                        </div>
                        <div className='flex justify-between'>
                          <span>Z-Score Atual:</span>
                          <span className='font-medium'>
                            {pairData.current_zscore?.toFixed(2) || 'N/A'}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className='font-medium mb-2'>Status de Trading</h4>
                      <div className='space-y-2'>
                        {pairData.current_zscore !== undefined && (
                          <div>
                            {Math.abs(pairData.current_zscore) > 2 ? (
                              <Badge
                                variant={
                                  pairData.current_zscore > 2
                                    ? 'destructive'
                                    : 'default'
                                }
                              >
                                {pairData.current_zscore > 2
                                  ? 'Sobrevalorizado'
                                  : 'Subvalorizado'}
                              </Badge>
                            ) : (
                              <Badge variant='secondary'>
                                Dentro da Faixa Normal
                              </Badge>
                            )}
                          </div>
                        )}

                        {pairData.cointegrated ? (
                          <Badge variant='default'>Par Cointegrado</Badge>
                        ) : (
                          <Badge variant='secondary'>Par Não Cointegrado</Badge>
                        )}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>

          {pairData.signals && pairData.signals.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Sinais de Trading Recentes</CardTitle>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Data</TableHead>
                      <TableHead>Tipo de Sinal</TableHead>
                      <TableHead>Z-Score</TableHead>
                      <TableHead>Ação</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {pairData.signals
                      .slice(0, 5)
                      .map((signal: any, index: number) => (
                        <TableRow key={index}>
                          <TableCell>
                            {formatDate(signal.signal_date)}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={
                                signal.signal_type === 'buy'
                                  ? 'default'
                                  : 'destructive'
                              }
                            >
                              {signal.signal_type === 'buy'
                                ? 'COMPRA'
                                : 'VENDA'}
                            </Badge>
                          </TableCell>
                          <TableCell>{signal.zscore.toFixed(2)}</TableCell>
                          <TableCell>
                            {signal.signal_type === 'buy' ? (
                              <span>
                                Long {asset1} / Short {asset2}
                              </span>
                            ) : (
                              <span>
                                Short {asset1} / Long {asset2}
                              </span>
                            )}
                          </TableCell>
                        </TableRow>
                      ))}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </div>
      ) : (
        <div className='text-center py-8'>
          <p className='text-muted-foreground'>
            Nenhum dado disponível para este par.
          </p>
        </div>
      )}
    </div>
  );
};

export { PairTradingView };
