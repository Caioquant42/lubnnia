'use client';

import { PiggyBank, Target, Zap } from 'lucide-react';
import { useEffect, useState } from 'react';

import { MarketIntelligenceFeed } from '@/components/Dashboard/MarketIntelligenceFeed';
import { MarketVolatilityWidget } from '@/components/Dashboard/MarketVolatilityWidget';
import { OptionsStrategyWidget } from '@/components/Dashboard/OptionsStrategyWidget';
import { TradingOpportunitiesHub } from '@/components/Dashboard/TradingOpportunitiesHub';
import { FluxoDDMChart } from '@/components/Finance/FluxoDDMChart';
import { StockVariationChart } from '@/components/Finance/StockVariationChart';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

export default function DashboardPage() {
  const [userName, setUserName] = useState('User');
  const [currentTime, setCurrentTime] = useState(new Date());
  const [expandedSections, setExpandedSections] = useState({
    marketOverview: true,
    portfolio: true,
    tradingTools: true,
  });

  // Update current time every minute
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 60000);
    return () => clearInterval(timer);
  }, []);

  // Get personalized greeting based on time
  const getGreeting = () => {
    const hour = currentTime.getHours();
    if (hour < 12) return 'Bom dia';
    if (hour < 18) return 'Boa tarde';
    return 'Boa noite';
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

  return (
    <div className='space-y-6'>
      {/* Enhanced Header with Personalized Greeting */}
      <div className='flex flex-col justify-between gap-4 md:flex-row md:items-center'>
        <div>
          <div className='flex items-center gap-2 mb-1'>
            <h1 className='text-2xl font-bold tracking-tight'>Dashboard</h1>
            <Badge variant='secondary' className='text-xs'>
              {currentTime.toLocaleTimeString('pt-BR', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Badge>
          </div>
          <p className='text-muted-foreground'>
            {getGreeting()}, {userName}! Aqui está uma visão geral do seu
            portfólio financeiro.
          </p>
        </div>
      </div>

      {/* Market Overview Section */}
      <Collapsible
        open={expandedSections.marketOverview}
        onOpenChange={() => toggleSection('marketOverview')}
      >
        <CollapsibleTrigger asChild>
          <Button variant='ghost' className='w-full justify-between p-4 h-auto'>
            <div className='flex items-center gap-2'>
              <Target className='h-5 w-5' />
              <span className='font-semibold'>Visão Geral do Mercado</span>
            </div>
            <Badge variant='outline' className='text-xs'>
              {expandedSections.marketOverview ? 'Recolher' : 'Expandir'}
            </Badge>
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className='space-y-4'>
          {/* DDM Fluxo Chart */}
          <div>
            <FluxoDDMChart />
          </div>

          {/* Stock Variations Sunburst Chart */}
          <div>
            <StockVariationChart />
          </div>

          {/* Market Volatility & Trading Opportunities */}
          <div className='grid gap-4 lg:grid-cols-7'>
            <TradingOpportunitiesHub className='lg:col-span-4' />
            <MarketVolatilityWidget className='lg:col-span-3' />
          </div>
        </CollapsibleContent>
      </Collapsible>

      {/* Trading Tools Section */}
      <Collapsible
        open={expandedSections.tradingTools}
        onOpenChange={() => toggleSection('tradingTools')}
      >
        <CollapsibleTrigger asChild>
          <Button variant='ghost' className='w-full justify-between p-4 h-auto'>
            <div className='flex items-center gap-2'>
              <Zap className='h-5 w-5' />
              <span className='font-semibold'>Ferramentas de Trading</span>
            </div>
            <Badge variant='outline' className='text-xs'>
              {expandedSections.tradingTools ? 'Recolher' : 'Expandir'}
            </Badge>
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className='space-y-4'>
          {/* Options Strategy Widget */}
          <div>
            <OptionsStrategyWidget />
          </div>

          {/* Market Intelligence Feed */}
          <div>
            <MarketIntelligenceFeed />
          </div>
        </CollapsibleContent>
      </Collapsible>

      {/* Portfolio Section - Coming Soon */}
      <Collapsible
        open={expandedSections.portfolio}
        onOpenChange={() => toggleSection('portfolio')}
      >
        <CollapsibleTrigger asChild>
          <Button variant='ghost' className='w-full justify-between p-4 h-auto'>
            <div className='flex items-center gap-2'>
              <PiggyBank className='h-5 w-5' />
              <span className='font-semibold'>Meu Portfólio</span>
              <Badge
                variant='secondary'
                className='text-xs bg-muted text-muted-foreground'
              >
                Em breve
              </Badge>
            </div>
            <Badge variant='outline' className='text-xs'>
              {expandedSections.portfolio ? 'Recolher' : 'Expandir'}
            </Badge>
          </Button>
        </CollapsibleTrigger>
        <CollapsibleContent className='space-y-4'>
          <div className='flex flex-col items-center justify-center py-12 text-center'>
            <PiggyBank className='h-12 w-12 text-muted-foreground mb-4' />
            <h3 className='text-lg font-semibold mb-2'>
              Portfólio em Desenvolvimento
            </h3>
            <p className='text-muted-foreground max-w-md'>
              Esta seção será implementada em breve. Aqui você poderá visualizar
              e gerenciar seu portfólio de investimentos com análises detalhadas
              e métricas de performance.
            </p>
          </div>
        </CollapsibleContent>
      </Collapsible>
    </div>
  );
}
