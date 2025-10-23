import { Check, Star, Zap } from 'lucide-react';
import Link from 'next/link';

import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

import { STRIPE_PRODUCTS } from '../../../stripe-config';

export default function PricingPage() {
  return (
    <div className='min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-12 md:py-24'>
      <div className='container mx-auto px-4 sm:px-6 lg:px-8'>
        <div className='mx-auto max-w-4xl text-center mb-16'>
          <h1 className='text-3xl font-bold tracking-tight sm:text-4xl md:text-5xl text-white mb-6'>
            Escolha seu Plano de Trading
          </h1>
          <p className='text-lg text-slate-300 max-w-2xl mx-auto'>
            Selecione o plano que melhor se adapta às suas necessidades de
            trading quantitativo
          </p>
        </div>

        <div className='mx-auto max-w-4xl grid gap-8 md:grid-cols-2'>
          {Object.entries(STRIPE_PRODUCTS).map(([key, product]) => (
            <Card
              key={key}
              className={`flex flex-col relative ${
                key === 'ZOMMA_PRO'
                  ? 'border-orange-500/50 shadow-2xl shadow-orange-500/20 bg-slate-800/50 backdrop-blur-xl'
                  : 'border-slate-700/50 bg-slate-800/30 backdrop-blur-xl'
              }`}
            >
              {key === 'ZOMMA_PRO' && (
                <div className='absolute -top-4 left-1/2 transform -translate-x-1/2'>
                  <div className='inline-flex items-center gap-2 px-4 py-2 rounded-full bg-gradient-to-r from-orange-500 to-orange-600 text-white text-sm font-medium'>
                    <Star className='h-4 w-4' />
                    Mais Popular
                  </div>
                </div>
              )}

              <CardHeader className='text-center pb-6'>
                <CardTitle
                  className={`text-2xl ${key === 'ZOMMA_PRO' ? 'text-white' : 'text-slate-200'}`}
                >
                  {product.name}
                </CardTitle>
                <CardDescription
                  className={`${key === 'ZOMMA_PRO' ? 'text-slate-300' : 'text-slate-400'}`}
                >
                  {product.description}
                </CardDescription>
              </CardHeader>

              <CardContent className='flex-1 px-6'>
                <div className='text-center mb-8'>
                  <span
                    className={`text-4xl font-bold ${key === 'ZOMMA_PRO' ? 'text-orange-400' : 'text-slate-200'}`}
                  >
                    {new Intl.NumberFormat('pt-BR', {
                      style: 'currency',
                      currency: product.currency,
                    }).format(product.price)}
                  </span>
                  <span
                    className={`text-sm ${key === 'ZOMMA_PRO' ? 'text-slate-300' : 'text-slate-400'}`}
                  >
                    {product.price === 0 ? '' : '/mês'}
                  </span>
                </div>

                <ul className='space-y-4'>
                  {product.features.map((feature) => (
                    <li key={feature} className='flex items-start gap-3'>
                      <Check
                        className={`h-5 w-5 mt-0.5 flex-shrink-0 ${
                          key === 'ZOMMA_PRO'
                            ? 'text-orange-400'
                            : 'text-green-400'
                        }`}
                      />
                      <span
                        className={`text-sm ${key === 'ZOMMA_PRO' ? 'text-slate-300' : 'text-slate-400'}`}
                      >
                        {feature}
                      </span>
                    </li>
                  ))}
                </ul>
              </CardContent>

              <CardFooter className='px-6 pb-6'>
                {key === 'FREE' ? (
                  <Link href='/auth/signup' className='w-full'>
                    <Button
                      className='w-full bg-slate-700 text-slate-200 hover:bg-slate-600 border border-slate-600 hover:border-slate-500 transition-all duration-300'
                      size='lg'
                    >
                      Começar Grátis
                    </Button>
                  </Link>
                ) : (
                  <Link href={`/checkout?plan=${key}`} className='w-full'>
                    <Button
                      className='w-full bg-gradient-to-r from-orange-500 to-orange-600 text-white hover:from-orange-600 hover:to-orange-700 transition-all duration-300 hover:scale-105 shadow-lg hover:shadow-orange-500/25'
                      size='lg'
                    >
                      <Zap className='mr-2 h-4 w-4' />
                      Assinar Zomma Pro
                    </Button>
                  </Link>
                )}
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Additional Information */}
        <div className='mx-auto max-w-3xl mt-16 text-center'>
          <div className='bg-slate-800/50 backdrop-blur-xl rounded-2xl border border-slate-700/50 p-8'>
            <h3 className='text-xl font-semibold text-white mb-4'>
              Por que escolher Zomma Pro?
            </h3>
            <div className='grid gap-6 md:grid-cols-3 text-sm'>
              <div className='text-center'>
                <div className='text-2xl font-bold text-orange-400 mb-2'>
                  52
                </div>
                <div className='text-slate-300'>Sinais Ativos</div>
              </div>
              <div className='text-center'>
                <div className='text-2xl font-bold text-green-400 mb-2'>
                  +47.4%
                </div>
                <div className='text-slate-300'>Alpha 30D</div>
              </div>
              <div className='text-center'>
                <div className='text-2xl font-bold text-orange-400 mb-2'>
                  74%
                </div>
                <div className='text-slate-300'>Win Rate</div>
              </div>
            </div>
            <p className='text-slate-300 mt-6'>
              Acesso completo a todas as ferramentas quantitativas
              institucionais com suporte prioritário
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
