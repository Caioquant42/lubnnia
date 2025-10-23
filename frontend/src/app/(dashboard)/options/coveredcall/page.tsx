'use client';

import { Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';

import coveredcallApi, {
  CoveredCallOption,
  CoveredCallResponse,
} from '__api__/coveredcallApi';

import { CoveredCallStrategyDetail } from '@/components/Finance/CoveredCallStrategyDetail';
import { CoveredCallStrategyTable } from '@/components/Finance/CoveredCallStrategyTable';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/components/ui/use-toast';

export default function CoveredCallStrategyPage() {
  const { toast } = useToast();
  const [loading, setLoading] = useState<boolean>(true);
  const [coveredCallData, setCoveredCallData] =
    useState<CoveredCallResponse | null>(null);
  const [selectedStrategy, setSelectedStrategy] =
    useState<CoveredCallOption | null>(null);
  const [activeTab, setActiveTab] = useState<string>('less_than_14_days');

  const maturityRangeTitles: Record<string, string> = {
    less_than_14_days: 'Menos de 14 dias',
    between_15_and_30_days: '15-30 dias',
    between_30_and_60_days: '30-60 dias',
    more_than_60_days: 'Mais de 60 dias',
  };
  useEffect(() => {
    const fetchCoveredCallData = async () => {
      try {
        setLoading(true);
        const data = await coveredcallApi.getCoveredCalls();
        setCoveredCallData(data);
      } catch (error) {
        console.error('Failed to fetch covered call data:', error);
        toast({
          title: 'Erro',
          description:
            'Falha ao carregar estratégias de call coberto. Por favor, tente novamente mais tarde.',
          variant: 'destructive',
        });
      } finally {
        setLoading(false);
      }
    };

    fetchCoveredCallData();
  }, [toast]);

  const handleStrategySelect = (strategy: CoveredCallOption) => {
    setSelectedStrategy(strategy);
  };

  const handleBackToList = () => {
    setSelectedStrategy(null);
  };
  // Format the date from the API to a more readable format
  const formatMaturityDate = (blockDate?: string, daysToMaturity?: number) => {
    if (!blockDate) return daysToMaturity ? `${daysToMaturity} days` : 'N/A';

    // Format the date as DD/MM/YYYY
    const date = new Date(blockDate);
    return `${date.getDate().toString().padStart(2, '0')}/${(
      date.getMonth() + 1
    )
      .toString()
      .padStart(2, '0')}/${date.getFullYear()} (${daysToMaturity} days)`;
  };

  if (loading) {
    return (
      <div className='flex h-full items-center justify-center'>
        <Loader2 className='h-8 w-8 animate-spin text-muted-foreground' />
      </div>
    );
  }

  if (selectedStrategy) {
    return (
      <div className='container mx-auto py-6'>
        <div className='mb-4'>
          <Button variant='outline' onClick={handleBackToList}>
            Voltar às estratégias
          </Button>
        </div>
        <CoveredCallStrategyDetail
          option={selectedStrategy}
          onClose={handleBackToList}
        />
      </div>
    );
  }
  return (
    <div className='container mx-auto px-4 py-8'>
      <div className='mb-6'>
        <Button
          variant='outline'
          onClick={() => window.history.back()}
          className='mb-4'
        >
          ← Voltar às estratégias
        </Button>

        <h1 className='text-3xl font-bold text-gray-900 dark:text-white mb-2'>
          Estratégia de Call Coberto
        </h1>
        <p className='text-gray-600 dark:text-gray-400'>
          Estratégias de call coberto com prêmios atrativos e retornos
          superiores ao CDI
        </p>

        {/* Info about premium filtering */}
        <div className='mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-900/20 dark:border-blue-800'>
          <p className='text-blue-800 dark:text-blue-200 text-sm'>
            ℹ️ Apenas opções com prêmios de R$ 0,01 ou superior são exibidas para
            garantir estratégias atrativas.
          </p>
        </div>
      </div>

      {!coveredCallData ? (
        <Card>
          <CardContent className='pt-6'>
            <p className='text-center text-muted-foreground'>
              Nenhum dado de call coberto disponível
            </p>
          </CardContent>
        </Card>
      ) : (
        <Tabs
          defaultValue={activeTab}
          onValueChange={setActiveTab}
          className='w-full'
        >
          <TabsList className='grid grid-cols-4 mb-4'>
            {Object.entries(maturityRangeTitles).map(([key, title]) => (
              <TabsTrigger
                key={key}
                value={key}
                disabled={
                  !coveredCallData.results[key] ||
                  coveredCallData.results[key].length === 0
                }
              >
                {title}
              </TabsTrigger>
            ))}
          </TabsList>

          {Object.entries(maturityRangeTitles).map(([key, title]) => {
            const options = coveredCallData.results[key] || [];

            return (
              <TabsContent key={key} value={key} className='mt-0'>
                <Card>
                  <CardHeader>
                    <CardTitle>Vencimento {title}</CardTitle>
                    <CardDescription>
                      Mostrando {options.length} estratégias de call coberto
                      ordenadas por retorno relativo CDI
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    {options.length > 0 ? (
                      <CoveredCallStrategyTable
                        options={options}
                        formatMaturityDate={formatMaturityDate}
                        onSelectStrategy={handleStrategySelect}
                      />
                    ) : (
                      <p className='text-center text-muted-foreground py-8'>
                        Nenhuma estratégia de call coberto disponível para este
                        período de vencimento
                      </p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>
            );
          })}
        </Tabs>
      )}
    </div>
  );
}
