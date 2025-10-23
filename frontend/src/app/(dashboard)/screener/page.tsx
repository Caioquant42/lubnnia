'use client';

import {
  ActivitySquare,
  Aperture,
  ArrowRight,
  BarChart,
  ScanSearch,
} from 'lucide-react';
import Link from 'next/link';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

export default function ScreenerPage() {
  const screenerTools = [
    {
      title: 'Índice de Força Relativa (RSI)',
      description:
        'Identifique ativos sobrecomprados e sobrevendidos usando o indicador RSI',
      icon: <ActivitySquare className='h-8 w-8 text-blue-500' />,
      link: '/screener/RSI',
      available: true,
    },
    {
      title: 'Médias Móveis',
      description:
        'Encontre ativos com cruzamentos de médias móveis e sinais de tendência',
      icon: <Aperture className='h-8 w-8 text-purple-500' />,
      link: '/screener/moving-averages',
      available: false,
    },
    {
      title: 'Bandas de Bollinger',
      description:
        'Identifique ativos próximos aos limites das Bandas de Bollinger',
      icon: <BarChart className='h-8 w-8 text-green-500' />,
      link: '/screener/bollinger',
      available: false,
    },
    {
      title: 'Screener Personalizado',
      description:
        'Crie filtros personalizados com múltiplos indicadores técnicos',
      icon: <ScanSearch className='h-8 w-8 text-orange-500' />,
      link: '/screener/custom',
      available: false,
    },
  ];

  return (
    <div className='container py-6'>
      <div className='mb-6'>
        <h1 className='text-3xl font-bold'>Screener de Mercado</h1>
        <p className='text-muted-foreground mt-1'>
          Ferramentas para identificar oportunidades de investimento com base em
          diversos indicadores técnicos
        </p>
      </div>

      <div className='grid gap-6 md:grid-cols-2'>
        {screenerTools.map((tool) => (
          <Card key={tool.title} className={tool.available ? '' : 'opacity-60'}>
            <CardHeader className='flex flex-row items-center gap-4'>
              <div className='rounded-lg bg-muted p-2'>{tool.icon}</div>
              <div>
                <CardTitle>{tool.title}</CardTitle>
                <CardDescription className='mt-1'>
                  {tool.description}
                </CardDescription>
              </div>
            </CardHeader>
            <CardFooter>
              {tool.available ? (
                <Link href={tool.link} className='w-full'>
                  <Button variant='outline' className='w-full justify-between'>
                    <span>Acessar</span>
                    <ArrowRight className='h-4 w-4' />
                  </Button>
                </Link>
              ) : (
                <Button
                  variant='outline'
                  disabled
                  className='w-full justify-between'
                >
                  <span>Em breve</span>
                  <ArrowRight className='h-4 w-4' />
                </Button>
              )}
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
