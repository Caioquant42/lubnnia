'use client';

import { format } from 'date-fns';
import { ptBR } from 'date-fns/locale';
import { useEffect, useState } from 'react';

import {
  fetchRSIData,
  RSIDataItem,
  RSIScreenerResponse,
} from '__api__/screenerApi';

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { SimpleProgress } from '@/components/ui/simple-progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function RSIScreenerPage() {
  const [rsiData, setRsiData] = useState<RSIScreenerResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<string>('15m');

  useEffect(() => {
    const loadRSIData = async () => {
      try {
        setIsLoading(true);
        const data = await fetchRSIData();
        setRsiData(data);
        setError(null);
      } catch (err) {
        setError('Falha ao carregar dados de RSI. Tente novamente mais tarde.');
        console.error('Error loading RSI data:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadRSIData();
  }, []);

  const formatDateTime = (dateTimeString: string) => {
    try {
      const date = new Date(dateTimeString);
      return format(date, "dd 'de' MMMM 'às' HH:mm", { locale: ptBR });
    } catch (error) {
      console.error('Error formatting date:', error);
      return dateTimeString;
    }
  };

  // Get RSI color based on value
  const getRsiColor = (rsi: number) => {
    if (rsi >= 80) return 'text-red-600';
    if (rsi >= 70) return 'text-orange-500';
    if (rsi <= 20) return 'text-green-600';
    if (rsi <= 30) return 'text-lime-500';
    return 'text-blue-500';
  };

  // Get progress bar color based on RSI value
  const getProgressColor = (rsi: number) => {
    if (rsi >= 80) return 'bg-red-600';
    if (rsi >= 70) return 'bg-orange-500';
    if (rsi <= 20) return 'bg-green-600';
    if (rsi <= 30) return 'bg-lime-500';
    return 'bg-blue-500';
  };

  const renderRSIItem = (item: RSIDataItem) => (
    <div
      key={`${item.Symbol}-${item.Datetime}`}
      className='mb-4 rounded-lg border p-3'
    >
      <div className='flex items-center justify-between'>
        <div className='flex items-center space-x-2'>
          <span className='font-bold'>{item.Symbol}</span>
        </div>
        <span className={`font-bold ${getRsiColor(item.RSI)}`}>
          RSI: {item.RSI.toFixed(2)}
        </span>
      </div>
      <div className='mt-2'>
        <div className='mb-1 flex items-center justify-between'>
          <span className='text-xs text-muted-foreground'>0</span>
          <span className='text-xs text-muted-foreground'>100</span>
        </div>
        <SimpleProgress
          value={item.RSI}
          className={getProgressColor(item.RSI)}
        />
      </div>
      <div className='mt-2 text-sm'>
        <span className='text-muted-foreground'>Preço: </span>
        <span className='font-medium'>R$ {item.AdjClose.toFixed(2)}</span>
      </div>
    </div>
  );

  const renderTimeframeContent = (timeframe: string) => {
    const timeframeKey = `stockdata_${timeframe}` as keyof RSIScreenerResponse;
    const timeframeData = rsiData?.[timeframeKey];

    if (!timeframeData) {
      return (
        <div className='text-center py-6 text-gray-500'>
          Nenhum dado disponível para este timeframe
        </div>
      );
    }

    return (
      <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
        <Card>
          <CardHeader>
            <CardTitle>Sobrecomprados (RSI &gt; 70)</CardTitle>
            <CardDescription>
              {timeframeData.overbought.length} ativos com possível tendência de
              reversão para baixo
            </CardDescription>
          </CardHeader>
          <CardContent>
            {timeframeData.overbought.length > 0 ? (
              timeframeData.overbought.map(renderRSIItem)
            ) : (
              <div className='text-center py-6 text-gray-500'>
                Nenhum ativo sobrecomprado neste período
              </div>
            )}
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle>Sobrevendidos (RSI &lt; 30)</CardTitle>
            <CardDescription>
              {timeframeData.oversold.length} ativos com possível tendência de
              reversão para cima
            </CardDescription>
          </CardHeader>
          <CardContent>
            {timeframeData.oversold.length > 0 ? (
              timeframeData.oversold.map(renderRSIItem)
            ) : (
              <div className='text-center py-6 text-gray-500'>
                Nenhum ativo sobrevendido neste período
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  };

  return (
    <div className='container py-6'>
      <div className='mb-6'>
        <h1 className='text-3xl font-bold'>Screener RSI</h1>
        <p className='text-muted-foreground mt-1'>
          Análise de ativos sobrecomprados e sobrevendidos por Índice de Força
          Relativa (RSI)
        </p>
      </div>

      {isLoading ? (
        <div className='flex justify-center my-12'>
          <div className='animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary'></div>
        </div>
      ) : error ? (
        <Card>
          <CardContent className='py-6'>
            <div className='text-center text-red-500'>{error}</div>
          </CardContent>
        </Card>
      ) : (
        <Tabs defaultValue='15m' value={activeTab} onValueChange={setActiveTab}>
          <TabsList className='mb-6'>
            <TabsTrigger value='15m'>15 minutos</TabsTrigger>
            <TabsTrigger value='60m'>1 hora</TabsTrigger>
            <TabsTrigger value='1d'>Diário</TabsTrigger>
            <TabsTrigger value='1wk'>Semanal</TabsTrigger>
          </TabsList>
          <TabsContent value='15m'>{renderTimeframeContent('15m')}</TabsContent>
          <TabsContent value='60m'>{renderTimeframeContent('60m')}</TabsContent>
          <TabsContent value='1d'>{renderTimeframeContent('1d')}</TabsContent>
          <TabsContent value='1wk'>{renderTimeframeContent('1wk')}</TabsContent>
        </Tabs>
      )}
    </div>
  );
}
