'use client';

import { AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

import { fetchRecentTradingSignals } from '__api__/longshortService';

import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
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
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

import SpreadChart from '../SpreadChart';

interface RecentSignal {
  asset1: string;
  asset2: string;
  beta: number;
  current_zscore: number;
  p_value: number;
  signal_date: string;
  signal_type: 'buy' | 'sell';
}

interface RecentSignalsData {
  last_5_days_signals: RecentSignal[];
  pairs_data: {
    [key: string]: {
      asset1: string;
      asset2: string;
      zscore: number[];
      dates: string[];
      spread: number[];
    };
  };
}

const RecentSignals = () => {
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [signalsData, setSignalsData] = useState<RecentSignalsData | null>(
    null
  );
  const [selectedSignalType, setSelectedSignalType] = useState<
    'all' | 'buy' | 'sell'
  >('all');
  const [selectedPair, setSelectedPair] = useState<string | null>(null);

  useEffect(() => {
    const loadSignals = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await fetchRecentTradingSignals();
        setSignalsData(data);
      } catch (err) {
        console.error('Error loading recent trading signals:', err);
        setError(
          'Falha ao carregar sinais de trading recentes. Tente novamente mais tarde.'
        );
      } finally {
        setLoading(false);
      }
    };

    loadSignals();
  }, []);

  const handlePairSelect = (pairKey: string) => {
    if (selectedPair === pairKey) {
      setSelectedPair(null); // Deselect if already selected
    } else {
      setSelectedPair(pairKey);
    }
  };

  // Filter signals based on selected type
  const filteredSignals =
    signalsData?.last_5_days_signals.filter((signal) => {
      if (selectedSignalType === 'all') return true;
      return signal.signal_type === selectedSignalType;
    }) || [];

  // Format date for display
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return new Intl.DateTimeFormat('pt-BR', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    }).format(date);
  };

  // Get badge color based on signal type
  const getSignalBadgeVariant = (signalType: string) => {
    return signalType === 'buy' ? 'default' : 'destructive';
  };

  // Get badge color based on z-score
  const getZscoreBadgeVariant = (zscore: number) => {
    if (zscore < -2) return 'default';
    if (zscore > 2) return 'destructive';
    return 'secondary';
  };

  // Create pair key for consistency
  const createPairKey = (asset1: string, asset2: string) =>
    `${asset1}_${asset2}`;

  return (
    <Card className='w-full'>
      <CardHeader>
        <CardTitle>Sinais de Trading Recentes</CardTitle>
        <CardDescription>
          Oportunidades de trading ativas dos últimos 5 dias de trading
        </CardDescription>
      </CardHeader>

      <CardContent className='space-y-4'>
        {error && (
          <Alert variant='destructive'>
            <AlertCircle className='h-4 w-4' />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {loading ? (
          <div className='space-y-2'>
            <Skeleton className='h-8 w-full' />
            <Skeleton className='h-[300px] w-full' />
          </div>
        ) : (
          <>
            {/* Signal Type Tabs */}
            <Tabs
              defaultValue='all'
              onValueChange={(value) =>
                setSelectedSignalType(value as 'all' | 'buy' | 'sell')
              }
            >
              <TabsList className='grid w-full grid-cols-3'>
                <TabsTrigger value='all'>Todos os Sinais</TabsTrigger>
                <TabsTrigger value='buy'>Sinais de Compra</TabsTrigger>
                <TabsTrigger value='sell'>Sinais de Venda</TabsTrigger>
              </TabsList>
            </Tabs>

            {/* Signals Table */}
            <div className='rounded-md border'>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className='font-medium'>Par</TableHead>
                    <TableHead className='font-medium'>Sinal</TableHead>
                    <TableHead className='font-medium'>Z-Score</TableHead>
                    <TableHead className='font-medium'>Valor P</TableHead>
                    <TableHead className='font-medium'>Data</TableHead>
                    <TableHead className='font-medium'></TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {filteredSignals.length > 0 ? (
                    filteredSignals.map((signal, index) => {
                      const pairKey = createPairKey(
                        signal.asset1,
                        signal.asset2
                      );
                      return (
                        <TableRow
                          key={index}
                          className={selectedPair === pairKey ? 'bg-muted' : ''}
                        >
                          <TableCell className='font-medium'>
                            {signal.asset1}/{signal.asset2}
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={getSignalBadgeVariant(
                                signal.signal_type
                              )}
                            >
                              {signal.signal_type === 'buy'
                                ? 'COMPRA'
                                : 'VENDA'}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Badge
                              variant={getZscoreBadgeVariant(
                                signal.current_zscore
                              )}
                            >
                              {signal.current_zscore.toFixed(2)}
                            </Badge>
                          </TableCell>
                          <TableCell>{signal.p_value.toFixed(4)}</TableCell>
                          <TableCell>
                            {formatDate(signal.signal_date)}
                          </TableCell>
                          <TableCell>
                            <Button
                              variant='ghost'
                              size='sm'
                              onClick={() => handlePairSelect(pairKey)}
                            >
                              {selectedPair === pairKey
                                ? 'Ocultar'
                                : 'Detalhes'}
                            </Button>
                          </TableCell>
                        </TableRow>
                      );
                    })
                  ) : (
                    <TableRow>
                      <TableCell colSpan={6} className='text-center py-8'>
                        <p className='text-muted-foreground'>
                          Nenhum sinal encontrado para os critérios
                          selecionados.
                        </p>
                      </TableCell>
                    </TableRow>
                  )}
                </TableBody>
              </Table>
            </div>

            {/* Selected Pair Details */}
            {selectedPair && signalsData?.pairs_data[selectedPair] && (
              <div className='mt-6 space-y-4'>
                <div className='flex items-center justify-between'>
                  <h3 className='text-lg font-medium'>
                    Detalhes do Par:{' '}
                    {signalsData.pairs_data[selectedPair].asset1} /{' '}
                    {signalsData.pairs_data[selectedPair].asset2}
                  </h3>
                  <Button
                    variant='outline'
                    size='sm'
                    onClick={() => setSelectedPair(null)}
                  >
                    Fechar
                  </Button>
                </div>

                {/* Spread Chart */}
                <Card>
                  <CardHeader>
                    <CardTitle>Análise do Spread</CardTitle>
                    <CardDescription>
                      Evolução do spread e Z-Score ao longo do tempo
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <SpreadChart
                      data={(() => {
                        const pairData = signalsData.pairs_data[selectedPair];
                        return pairData.dates.map(
                          (date: string, index: number) => ({
                            date: date,
                            spread: pairData.spread[index] || 0,
                            zscore: pairData.zscore[index] || 0,
                          })
                        );
                      })()}
                      title={`Spread: ${signalsData.pairs_data[selectedPair].asset1} / ${signalsData.pairs_data[selectedPair].asset2}`}
                    />
                  </CardContent>
                </Card>

                {/* Trading Strategy */}
                <div className='mt-4'>
                  <h4 className='text-sm font-medium mb-2'>
                    Estratégia de Trading
                  </h4>
                  <p className='text-sm'>
                    {signalsData.pairs_data[selectedPair].zscore[
                      signalsData.pairs_data[selectedPair].zscore.length - 1
                    ] < -2
                      ? `Long ${signalsData.pairs_data[selectedPair].asset1} / Short ${signalsData.pairs_data[selectedPair].asset2} - Z-score está abaixo do limite -2`
                      : signalsData.pairs_data[selectedPair].zscore[
                            signalsData.pairs_data[selectedPair].zscore.length -
                              1
                          ] > 2
                        ? `Short ${signalsData.pairs_data[selectedPair].asset1} / Long ${signalsData.pairs_data[selectedPair].asset2} - Z-score está acima do limite 2`
                        : `Nenhum sinal claro no Z-score atual (${signalsData.pairs_data[selectedPair].zscore[signalsData.pairs_data[selectedPair].zscore.length - 1].toFixed(2)})`}
                  </p>
                </div>
              </div>
            )}
          </>
        )}
      </CardContent>

      <CardFooter>
        <p className='text-xs text-muted-foreground'>
          Exibindo sinais de trading dos últimos 5 dias de trading com 30 dias
          de dados históricos de spread.
        </p>
      </CardFooter>
    </Card>
  );
};

export { RecentSignals };
