'use client';

import {
  Activity,
  ArrowRight,
  ArrowUpRight,
  BarChart,
  Calculator,
  CheckCircle,
  TrendingDown,
  TrendingUp,
  Zap,
} from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';

export default function LandingPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  const handleLogoClick = () => {
    if (isAuthenticated) {
      router.push('/dashboard');
    } else {
      router.push('/auth/login');
    }
  };
  return (
    <div className='min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900'>
      {/* Navigation */}
      <header className='fixed top-0 z-50 w-full border-b border-slate-700/50 bg-slate-900/95 backdrop-blur-xl supports-[backdrop-filter]:bg-slate-900/80'>
        <div className='container mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex h-16 items-center justify-between'>
            <div className='flex items-center gap-3'>
              <button onClick={handleLogoClick}>
                <Image
                  src='/Logofiles/For Web/png/Color logo - no background.png'
                  alt='Zomma Quant Logo'
                  width={150}
                  height={150}
                  className='h-35 w-35 cursor-pointer hover:opacity-80 transition-opacity'
                />
              </button>
            </div>

            <nav className='hidden md:flex items-center gap-8'>
              <Link
                href='/features'
                className='text-sm font-medium text-slate-300 transition-colors hover:text-white'
              >
                Recursos
              </Link>
              <Link
                href='/pricing'
                className='text-sm font-medium text-slate-300 transition-colors hover:text-white'
              >
                Preços
              </Link>
              <Link
                href='/about'
                className='text-sm font-medium text-slate-300 transition-colors hover:text-white'
              >
                Sobre
              </Link>
            </nav>

            <div className='flex items-center gap-3'>
              <Link href='/auth/login'>
                <Button
                  variant='ghost'
                  size='sm'
                  className='text-slate-300 hover:text-white hover:bg-slate-800'
                >
                  Entrar
                </Button>
              </Link>
              <Link href='/auth/register'>
                <Button
                  size='sm'
                  className='bg-gradient-to-r from-orange-500 to-orange-600 text-white hover:from-orange-600 hover:to-orange-700 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-orange-500/25'
                >
                  Começar Agora
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className='relative pt-24 pb-16 lg:pt-32 lg:pb-24'>
        {/* Background Elements */}
        <div className='absolute inset-0 overflow-hidden'>
          <div className='absolute -top-40 -right-40 h-80 w-80 rounded-full bg-gradient-to-br from-orange-500/20 to-orange-600/20 blur-3xl'></div>
          <div className='absolute -bottom-40 -left-40 h-80 w-80 rounded-full bg-gradient-to-br from-blue-500/20 to-blue-600/20 blur-3xl'></div>
        </div>

        <div className='container mx-auto px-4 sm:px-6 lg:px-8 relative z-10'>
          <div className='grid lg:grid-cols-2 gap-12 lg:gap-16 items-center'>
            {/* Left Column - Main Content */}
            <div className='space-y-8'>
              <div className='space-y-6'>
                <div className='inline-flex items-center gap-2 px-4 py-2 rounded-full bg-orange-500/10 border border-orange-500/20 text-orange-400 text-sm font-medium'>
                  <div className='h-2 w-2 rounded-full bg-orange-400 animate-pulse'></div>
                  52 Sinais Ativos em Tempo Real
                </div>

                <h1 className='text-4xl sm:text-5xl lg:text-6xl font-bold text-white leading-tight'>
                  <span className='block'>Análise Quantitativa</span>
                  <span className='block bg-gradient-to-r from-orange-400 to-orange-600 bg-clip-text text-transparent'>
                    Profissional
                  </span>
                  <span className='block text-3xl sm:text-4xl lg:text-5xl text-slate-300 mt-2'>
                    Resultados Institucionais
                  </span>
                </h1>

                <p className='text-lg sm:text-xl text-slate-300 leading-relaxed max-w-2xl'>
                  Estratégias quantitativas institucionais com análise de
                  volatilidade, pairs trading e otimização de portfólio em tempo
                  real.
                </p>
              </div>

              <div className='flex flex-col sm:flex-row gap-4'>
                <Link href='/signals'>
                  <Button
                    size='lg'
                    className='bg-gradient-to-r from-orange-500 to-orange-600 text-white hover:from-orange-600 hover:to-orange-700 px-8 py-4 text-lg font-semibold transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-orange-500/25'
                  >
                    Ver Sinais Ao Vivo
                    <TrendingUp className='ml-2 h-5 w-5' />
                  </Button>
                </Link>
                <Link href='/performance'>
                  <Button
                    size='lg'
                    variant='outline'
                    className='border-slate-600 text-slate-300 hover:bg-slate-800 hover:text-white px-8 py-4 text-lg font-semibold transition-all duration-300 hover:scale-105'
                  >
                    Performance das Estratégias
                    <ArrowUpRight className='ml-2 h-5 w-5' />
                  </Button>
                </Link>
              </div>

              <div className='flex items-center gap-6 pt-4'>
                <div className='flex -space-x-2'>
                  {[1, 2, 3, 4].map((i) => (
                    <div
                      key={i}
                      className='flex h-10 w-10 items-center justify-center rounded-full border-2 border-slate-700 bg-slate-800 text-xs font-medium text-slate-300'
                    >
                      T{i}
                    </div>
                  ))}
                </div>
                <div className='text-sm text-slate-400'>
                  <span className='font-semibold text-white'>2.847</span>{' '}
                  traders quantitativos confiam em nossos sinais
                </div>
              </div>
            </div>

            {/* Right Column - Live Dashboard */}
            <div className='relative'>
              <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-6 shadow-2xl'>
                {/* Live Status Header */}
                <div className='flex items-center justify-between mb-6'>
                  <span className='text-sm font-medium text-slate-400'>
                    Dashboard Quantitativo
                  </span>
                  <div className='flex items-center gap-2'>
                    <div className='h-2 w-2 rounded-full bg-green-400 animate-pulse'></div>
                    <span className='text-xs text-green-400 font-medium'>
                      AO VIVO
                    </span>
                  </div>
                </div>

                {/* Key Metrics Grid */}
                <div className='grid grid-cols-3 gap-4 mb-6'>
                  <div className='bg-slate-700/50 rounded-xl p-4 border border-slate-600/50'>
                    <div className='text-2xl font-bold text-orange-400 mb-1'>
                      52
                    </div>
                    <div className='text-xs text-slate-400 mb-2'>
                      Sinais Ativos
                    </div>
                    <div className='flex items-center gap-2 text-xs'>
                      <span className='text-green-400'>14 BUY</span>
                      <span className='text-slate-500'>•</span>
                      <span className='text-red-400'>38 SELL</span>
                    </div>
                  </div>

                  <div className='bg-slate-700/50 rounded-xl p-4 border border-slate-600/50'>
                    <div className='text-2xl font-bold text-green-400 mb-1'>
                      +47.4%
                    </div>
                    <div className='text-xs text-slate-400 mb-2'>Alpha 30D</div>
                    <div className='flex items-center text-xs text-green-400'>
                      <ArrowUpRight className='mr-1 h-3 w-3' />
                      <span>vs IBOV</span>
                    </div>
                  </div>

                  <div className='bg-slate-700/50 rounded-xl p-4 border border-slate-600/50'>
                    <div className='text-2xl font-bold text-orange-400 mb-1'>
                      74%
                    </div>
                    <div className='text-xs text-slate-400 mb-2'>Win Rate</div>
                    <div className='text-xs text-slate-400'>Último mês</div>
                  </div>
                </div>

                {/* Recent Signals */}
                <div className='bg-slate-700/50 rounded-xl p-4 border border-slate-600/50 mb-6'>
                  <div className='text-xs font-medium text-slate-400 mb-3'>
                    PAIRS TRADING - SINAIS RECENTES
                  </div>
                  <div className='space-y-2'>
                    <div className='flex items-center justify-between p-2 rounded-lg bg-green-500/10 border border-green-500/20'>
                      <div className='flex items-center gap-2'>
                        <span className='text-xs font-medium text-white'>
                          PETR4/VALE3
                        </span>
                        <span className='text-xs bg-green-500 text-white px-2 py-1 rounded'>
                          BUY
                        </span>
                      </div>
                      <span className='text-xs text-green-400'>
                        Z-Score: -2.1
                      </span>
                    </div>
                    <div className='flex items-center justify-between p-2 rounded-lg bg-red-500/10 border border-red-500/20'>
                      <div className='flex items-center gap-2'>
                        <span className='text-xs font-medium text-white'>
                          ITUB4/BBDC4
                        </span>
                        <span className='text-xs bg-red-500 text-white px-2 py-1 rounded'>
                          SELL
                        </span>
                      </div>
                      <span className='text-xs text-red-400'>
                        Z-Score: +1.8
                      </span>
                    </div>
                  </div>
                </div>

                {/* Strategy Performance */}
                <div className='grid grid-cols-2 gap-4'>
                  <div className='bg-slate-700/50 rounded-xl p-4 border border-slate-600/50'>
                    <div className='text-xs font-medium text-slate-400 mb-3'>
                      ESTRATÉGIAS ATIVAS
                    </div>
                    <div className='space-y-2'>
                      <div className='flex justify-between text-xs'>
                        <span className='text-slate-300'>Pairs Trading</span>
                        <span className='text-green-400 font-medium'>
                          +12.3%
                        </span>
                      </div>
                      <div className='flex justify-between text-xs'>
                        <span className='text-slate-300'>Mean Reversion</span>
                        <span className='text-green-400 font-medium'>
                          +8.7%
                        </span>
                      </div>
                      <div className='flex justify-between text-xs'>
                        <span className='text-slate-300'>Momentum</span>
                        <span className='text-red-400 font-medium'>-2.1%</span>
                      </div>
                    </div>
                  </div>

                  <div className='bg-slate-700/50 rounded-xl p-4 border border-slate-600/50'>
                    <div className='text-xs font-medium text-slate-400 mb-3'>
                      MÉTRICAS DE RISCO
                    </div>
                    <div className='space-y-2'>
                      <div className='flex justify-between text-xs'>
                        <span className='text-slate-300'>Sharpe Ratio</span>
                        <span className='text-orange-400 font-medium'>2.8</span>
                      </div>
                      <div className='flex justify-between text-xs'>
                        <span className='text-slate-300'>Max Drawdown</span>
                        <span className='text-red-400 font-medium'>-3.4%</span>
                      </div>
                      <div className='flex justify-between text-xs'>
                        <span className='text-slate-300'>Volatility</span>
                        <span className='text-slate-300'>12.1%</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className='py-20 lg:py-32 relative'>
        <div className='container mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='text-center mb-16'>
            <h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6'>
              Capacidades Quantitativas Institucionais
            </h2>
            <p className='text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed'>
              Ferramentas profissionais para análise quantitativa e geração de
              alpha consistente
            </p>
          </div>

          <div className='grid gap-8 md:grid-cols-2 lg:grid-cols-3'>
            {/* Pairs Trading Engine */}
            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 hover:border-orange-500/50 transition-all duration-300 hover:scale-105 group'>
              <div className='flex items-center gap-4 mb-6'>
                <div className='p-3 rounded-xl bg-orange-500/10 border border-orange-500/20'>
                  <TrendingUp className='h-8 w-8 text-orange-400' />
                </div>
                <h3 className='text-xl font-semibold text-white'>
                  Engine de Pairs Trading
                </h3>
              </div>
              <p className='text-slate-300 mb-6 leading-relaxed'>
                52 pares ativos com z-scores em tempo real, detecção automática
                de divergências e gestão de risco integrada.
              </p>
              <ul className='space-y-3'>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Cointegração dinâmica</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Múltiplos timeframes</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Stop-loss adaptativo</span>
                </li>
              </ul>
            </div>

            {/* Volatility Intelligence */}
            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 hover:border-orange-500/50 transition-all duration-300 hover:scale-105 group'>
              <div className='flex items-center gap-4 mb-6'>
                <div className='p-3 rounded-xl bg-orange-500/10 border border-orange-500/20'>
                  <Activity className='h-8 w-8 text-orange-400' />
                </div>
                <h3 className='text-xl font-semibold text-white'>
                  Inteligência de Volatilidade
                </h3>
              </div>
              <p className='text-slate-300 mb-6 leading-relaxed'>
                Análise de percentis IV, superfícies de volatilidade e
                identificação de oportunidades de opções.
              </p>
              <ul className='space-y-3'>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Rankings IV percentil</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Skew e termo structure</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Alertas de vol extrema</span>
                </li>
              </ul>
            </div>

            {/* RSI Screener */}
            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 hover:border-orange-500/50 transition-all duration-300 hover:scale-105 group'>
              <div className='flex items-center gap-4 mb-6'>
                <div className='p-3 rounded-xl bg-orange-500/10 border border-orange-500/20'>
                  <BarChart className='h-8 w-8 text-orange-400' />
                </div>
                <h3 className='text-xl font-semibold text-white'>
                  Screener RSI Avançado
                </h3>
              </div>
              <p className='text-slate-300 mb-6 leading-relaxed'>
                Detecção automática de sobrecompra/sobrevenda com múltiplos
                timeframes e filtros personalizáveis.
              </p>
              <ul className='space-y-3'>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Múltiplos timeframes</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Filtros setoriais</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Alertas automáticos</span>
                </li>
              </ul>
            </div>

            {/* Options Strategies */}
            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 hover:border-orange-500/50 transition-all duration-300 hover:scale-105 group'>
              <div className='flex items-center gap-4 mb-6'>
                <div className='p-3 rounded-xl bg-orange-500/10 border border-orange-500/20'>
                  <Zap className='h-8 w-8 text-orange-400' />
                </div>
                <h3 className='text-xl font-semibold text-white'>
                  Estratégias de Opções
                </h3>
              </div>
              <p className='text-slate-300 mb-6 leading-relaxed'>
                Covered Calls, Collars e spreads automatizados com análise de
                gregos e gestão de risco.
              </p>
              <ul className='space-y-3'>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Covered Calls</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Collars automáticos</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Análise de gregos</span>
                </li>
              </ul>
            </div>

            {/* Retirement Calculator */}
            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 hover:border-orange-500/50 transition-all duration-300 hover:scale-105 group'>
              <div className='flex items-center gap-4 mb-6'>
                <div className='p-3 rounded-xl bg-orange-500/10 border border-orange-500/20'>
                  <Calculator className='h-8 w-8 text-orange-400' />
                </div>
                <h3 className='text-xl font-semibold text-white'>
                  Calculadora de Aposentadoria
                </h3>
              </div>
              <p className='text-slate-300 mb-6 leading-relaxed'>
                Planejamento financeiro avançado com simulações de cenários e
                otimização de portfólio.
              </p>
              <ul className='space-y-3'>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Simulações de cenários</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Otimização de alocação</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Análise de fluxo de caixa</span>
                </li>
              </ul>
            </div>

            {/* Flow Analysis */}
            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8 hover:border-orange-500/50 transition-all duration-300 hover:scale-105 group'>
              <div className='flex items-center gap-4 mb-6'>
                <div className='p-3 rounded-xl bg-orange-500/10 border border-orange-500/20'>
                  <TrendingDown className='h-8 w-8 text-orange-400' />
                </div>
                <h3 className='text-xl font-semibold text-white'>
                  Análise de Fluxo
                </h3>
              </div>
              <p className='text-slate-300 mb-6 leading-relaxed'>
                Monitoramento de fluxo de capital institucional e análise de
                sentimentos de mercado.
              </p>
              <ul className='space-y-3'>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Fluxo institucional</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Análise de sentimentos</span>
                </li>
                <li className='flex items-center gap-3 text-sm text-slate-300'>
                  <CheckCircle className='h-4 w-4 text-green-400 flex-shrink-0' />
                  <span>Alertas de reversão</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Section */}
      <section className='py-20 lg:py-32 bg-slate-800/30 relative'>
        <div className='container mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='text-center mb-16'>
            <h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-white mb-6'>
              Confiado por Traders Quantitativos Profissionais
            </h2>
            <p className='text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed'>
              Mais de 2.847 traders confiam em nossos algoritmos para gerar
              alpha consistente
            </p>
          </div>

          {/* Statistics Grid */}
          <div className='grid gap-8 md:grid-cols-2 lg:grid-cols-4 mb-16'>
            <div className='text-center'>
              <div className='text-4xl font-bold text-orange-400 mb-3'>
                2.847
              </div>
              <div className='text-slate-300'>Traders Ativos</div>
            </div>
            <div className='text-center'>
              <div className='text-4xl font-bold text-green-400 mb-3'>
                R$ 280M
              </div>
              <div className='text-slate-300'>Volume Gerenciado</div>
            </div>
            <div className='text-center'>
              <div className='text-4xl font-bold text-orange-400 mb-3'>
                147.382
              </div>
              <div className='text-slate-300'>Trades Executados</div>
            </div>
            <div className='text-center'>
              <div className='text-4xl font-bold text-green-400 mb-3'>
                18 meses
              </div>
              <div className='text-slate-300'>Track Record</div>
            </div>
          </div>

          {/* Testimonials */}
          <div className='grid gap-8 md:grid-cols-2 lg:grid-cols-3'>
            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8'>
              <div className='mb-6'>
                <div className='flex items-center gap-1 mb-4'>
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className='h-5 w-5 text-yellow-400'>
                      ★
                    </div>
                  ))}
                </div>
                <p className='text-slate-300 leading-relaxed'>
                  "O pairs trading do Zomma Quant gerou +23% de alpha no meu
                  hedge fund. Sinais precisos e execução impecável."
                </p>
              </div>
              <div className='flex items-center gap-4'>
                <div className='h-12 w-12 rounded-full bg-slate-700 flex items-center justify-center text-sm font-medium text-white'>
                  RC
                </div>
                <div>
                  <div className='text-sm font-medium text-white'>
                    Roberto Costa
                  </div>
                  <div className='text-xs text-slate-400'>
                    Portfolio Manager, Hedge Fund
                  </div>
                </div>
              </div>
            </div>

            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8'>
              <div className='mb-6'>
                <div className='flex items-center gap-1 mb-4'>
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className='h-5 w-5 text-yellow-400'>
                      ★
                    </div>
                  ))}
                </div>
                <p className='text-slate-300 leading-relaxed'>
                  "Análise de volatilidade excepcional. Consegui identificar
                  oportunidades de arbitragem que passavam despercebidas."
                </p>
              </div>
              <div className='flex items-center gap-4'>
                <div className='h-12 w-12 rounded-full bg-slate-700 flex items-center justify-center text-sm font-medium text-white'>
                  MS
                </div>
                <div>
                  <div className='text-sm font-medium text-white'>
                    Mariana Silva
                  </div>
                  <div className='text-xs text-slate-400'>
                    Quant Trader, Family Office
                  </div>
                </div>
              </div>
            </div>

            <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8'>
              <div className='mb-6'>
                <div className='flex items-center gap-1 mb-4'>
                  {[1, 2, 3, 4, 5].map((i) => (
                    <div key={i} className='h-5 w-5 text-yellow-400'>
                      ★
                    </div>
                  ))}
                </div>
                <p className='text-slate-300 leading-relaxed'>
                  "Interface profissional e algoritmos sofisticados. Sharpe
                  ratio de 2.8 fala por si só. Recomendo sem hesitar."
                </p>
              </div>
              <div className='flex items-center gap-4'>
                <div className='h-12 w-12 rounded-full bg-slate-700 flex items-center justify-center text-sm font-medium text-white'>
                  AF
                </div>
                <div>
                  <div className='text-sm font-medium text-white'>
                    André Fernandes
                  </div>
                  <div className='text-xs text-slate-400'>
                    Head of Trading, Asset Management
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className='py-20 lg:py-32'>
        <div className='container mx-auto px-4 sm:px-6 lg:px-8 text-center'>
          <div className='max-w-4xl mx-auto space-y-8'>
            <h2 className='text-3xl sm:text-4xl lg:text-5xl font-bold text-white'>
              Pronto para Negociar como um Quant?
            </h2>
            <p className='text-xl text-slate-300 leading-relaxed'>
              Junte-se a 2.847 traders quantitativos que usam Zomma Quant para
              gerar alpha consistente com estratégias institucionais.
            </p>

            {/* Value Proposition Highlights */}
            <div className='grid gap-6 md:grid-cols-3 max-w-3xl mx-auto'>
              <div className='text-center'>
                <div className='text-3xl font-bold text-orange-400 mb-2'>
                  52
                </div>
                <div className='text-slate-300'>Sinais de Trading Ativos</div>
              </div>
              <div className='text-center'>
                <div className='text-3xl font-bold text-green-400 mb-2'>
                  +47.4%
                </div>
                <div className='text-slate-300'>Geração de Alpha 30D</div>
              </div>
              <div className='text-center'>
                <div className='text-3xl font-bold text-orange-400 mb-2'>
                  74%
                </div>
                <div className='text-slate-300'>Taxa de Acerto Média</div>
              </div>
            </div>

            <div className='space-y-4'>
              <Link href='/auth/register'>
                <Button
                  size='lg'
                  className='bg-gradient-to-r from-orange-500 to-orange-600 text-white hover:from-orange-600 hover:to-orange-700 px-12 py-6 text-xl font-semibold transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-orange-500/25'
                >
                  Começar Teste Grátis
                  <ArrowRight className='ml-3 h-6 w-6' />
                </Button>
              </Link>
              <p className='text-sm text-slate-400'>
                Sem cartão de crédito. Acesse 5 sinais de pairs trading
                gratuitamente.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className='border-t border-slate-700/50 py-12 bg-slate-800/30'>
        <div className='container mx-auto px-4 sm:px-6 lg:px-8'>
          <div className='flex flex-col md:flex-row items-center justify-between gap-6'>
            <div className='flex items-center gap-3'>
              <button onClick={handleLogoClick}>
                <Image
                  src='/Logofiles/For Web/svg/logo_modified.svg'
                  alt='Zomma Quant Logo'
                  width={32}
                  height={32}
                  className='h-8 w-8 cursor-pointer hover:opacity-80 transition-opacity'
                />
              </button>
              <p className='text-sm text-slate-400'>
                © 2025 Zomma Quant. Todos os direitos reservados.
              </p>
            </div>
            <nav className='flex gap-6 text-sm text-slate-400'>
              <Link
                href='/terms'
                className='hover:text-white transition-colors'
              >
                Termos
              </Link>
              <Link
                href='/privacy'
                className='hover:text-white transition-colors'
              >
                Privacidade
              </Link>
              <Link
                href='/contact'
                className='hover:text-white transition-colors'
              >
                Contato
              </Link>
            </nav>
          </div>
        </div>
      </footer>
    </div>
  );
}
