'use client';

import { Loader2 } from 'lucide-react';
import { useEffect, useState } from 'react';
import { CollarStrategy, getCollarData } from '__api__/collarApi';

import { CollarStrategyDetail } from '@/components/Finance/CollarStrategyDetail';
import { CollarStrategyTable } from '@/components/Finance/CollarStrategyTable';
import { Badge } from '@/components/ui/badge';
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

export default function CollarStrategyPage() {
  const [loading, setLoading] = useState(true);
  const [collarData, setCollarData] = useState<{
    [key: string]: { [key: string]: CollarStrategy[] };
  }>({});
  const [selectedStrategy, setSelectedStrategy] =
    useState<CollarStrategy | null>(null);
  const { toast } = useToast();

  useEffect(() => {
    const fetchCollarData = async () => {
      try {
        setLoading(true);
        const data = await getCollarData();
        setCollarData(data.results);
      } catch (error) {
        toast({
          title: 'Erro',
          description: 'Falha ao carregar dados da estratégia de collar.',
          variant: 'destructive',
        });
        console.error('Failed to fetch collar data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchCollarData();
  }, [toast]);
  const handleStrategySelect = (strategy: CollarStrategy) => {
    setSelectedStrategy(strategy);
  };

  const handleBackToList = () => {
    setSelectedStrategy(null);
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
        <CollarStrategyDetail
          strategy={selectedStrategy}
          onClose={handleBackToList}
        />
      </div>
    );
  }

  return (
    <div className='container mx-auto py-6'>
      <div className='mb-8'>
        <h1 className='text-3xl font-bold tracking-tight'>
          Estratégia de Collar
        </h1>
        <p className='text-muted-foreground'>
          Um collar é uma estratégia de opções que limita tanto o potencial de
          alta quanto o risco de baixa de uma posição subjacente.
        </p>

        {/* Info about premium filtering */}
        <div className='mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-900/20 dark:border-blue-800'>
          <p className='text-blue-800 dark:text-blue-200 text-sm'>
            ℹ️ Apenas estratégias com prêmios de R$ 0,01 ou superior são exibidas
            para garantir estratégias atrativas.
          </p>
        </div>
      </div>

      {collarData && (
        <Tabs defaultValue='intrinsic' className='space-y-4'>
          <div className='flex items-center justify-between'>
            <TabsList>
              <TabsTrigger value='intrinsic'>
                Proteção Intrínseca
                {collarData.intrinsic && (
                  <Badge variant='secondary' className='ml-2'>
                    {Object.values(collarData.intrinsic).flat().length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value='otm'>
                Estratégias OTM
                {collarData.otm && (
                  <Badge variant='secondary' className='ml-2'>
                    {Object.values(collarData.otm).flat().length}
                  </Badge>
                )}
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value='intrinsic' className='space-y-4'>
            {collarData.intrinsic && (
              <Tabs defaultValue='less_than_14_days' className='space-y-4'>
                <TabsList>
                  <TabsTrigger value='less_than_14_days'>
                    &lt; 14 Dias
                    {collarData.intrinsic.less_than_14_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.intrinsic.less_than_14_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value='between_15_and_30_days'>
                    15-30 Dias
                    {collarData.intrinsic.between_15_and_30_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.intrinsic.between_15_and_30_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value='between_30_and_60_days'>
                    30-60 Dias
                    {collarData.intrinsic.between_30_and_60_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.intrinsic.between_30_and_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value='more_than_60_days'>
                    &gt; 60 Dias
                    {collarData.intrinsic.more_than_60_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.intrinsic.more_than_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                </TabsList>

                <TabsContent value='less_than_14_days' className='space-y-4'>
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar de Curto Prazo (&lt; 14 dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar com menos de 14 dias para o
                        vencimento que fornecem proteção intrínseca
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.intrinsic.less_than_14_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent
                  value='between_15_and_30_days'
                  className='space-y-4'
                >
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar de Médio Prazo (15-30 dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar com 15-30 dias para o vencimento
                        que fornecem proteção intrínseca
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.intrinsic.between_15_and_30_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent
                  value='between_30_and_60_days'
                  className='space-y-4'
                >
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar de Médio-Longo Prazo (30-60 dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar com 30-60 dias para o vencimento
                        que fornecem proteção intrínseca
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.intrinsic.between_30_and_60_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value='more_than_60_days' className='space-y-4'>
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar de Longo Prazo (&gt; 60 dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar com mais de 60 dias para o
                        vencimento que fornecem proteção intrínseca
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.intrinsic.more_than_60_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            )}
          </TabsContent>

          <TabsContent value='otm' className='space-y-4'>
            {collarData.otm && (
              <Tabs defaultValue='less_than_14_days' className='space-y-4'>
                <TabsList>
                  <TabsTrigger value='less_than_14_days'>
                    &lt; 14 Dias
                    {collarData.otm.less_than_14_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.otm.less_than_14_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value='between_15_and_30_days'>
                    15-30 Dias
                    {collarData.otm.between_15_and_30_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.otm.between_15_and_30_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value='between_30_and_60_days'>
                    30-60 Dias
                    {collarData.otm.between_30_and_60_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.otm.between_30_and_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value='more_than_60_days'>
                    &gt; 60 Dias
                    {collarData.otm.more_than_60_days && (
                      <Badge variant='secondary' className='ml-2'>
                        {collarData.otm.more_than_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                </TabsList>

                <TabsContent value='less_than_14_days' className='space-y-4'>
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar OTM de Curto Prazo (&lt; 14 dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar fora do dinheiro com menos de 14
                        dias para o vencimento
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.otm.less_than_14_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent
                  value='between_15_and_30_days'
                  className='space-y-4'
                >
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar OTM de Médio Prazo (15-30 dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar fora do dinheiro com 15-30 dias
                        para o vencimento
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.otm.between_15_and_30_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent
                  value='between_30_and_60_days'
                  className='space-y-4'
                >
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar OTM de Médio-Longo Prazo (30-60
                        dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar fora do dinheiro com 30-60 dias
                        para o vencimento
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.otm.between_30_and_60_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>

                <TabsContent value='more_than_60_days' className='space-y-4'>
                  <Card>
                    <CardHeader>
                      <CardTitle>
                        Estratégias de Collar OTM de Longo Prazo (&gt; 60 dias)
                      </CardTitle>
                      <CardDescription>
                        Estratégias de collar fora do dinheiro com mais de 60
                        dias para o vencimento
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <CollarStrategyTable
                        data={collarData.otm.more_than_60_days || []}
                        onSelectStrategy={handleStrategySelect}
                      />
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}
