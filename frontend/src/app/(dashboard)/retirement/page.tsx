import { Calculator, PiggyBank, TrendingUp, Wallet } from 'lucide-react';

import { RetirementCalculator } from '@/components/Finance/RetirementCalculator';

export const metadata = {
  title: 'Planejamento de Aposentadoria | Zomma Quant',
  description:
    'Planeje sua estratégia de aposentadoria com nossa calculadora abrangente',
};

export default function RetirementPlanningPage() {
  return (
    <div className='container mx-auto py-6'>
      <div className='flex flex-col gap-2 mb-6'>
        <h1 className='text-3xl font-bold tracking-tight'>
          Planejamento de Aposentadoria
        </h1>
        <p className='text-muted-foreground'>
          Planeje sua estratégia financeira de aposentadoria usando nossa
          calculadora avançada.
        </p>
      </div>

      <div className='grid gap-6'>
        {/* Intro cards */}
        <div className='grid gap-4 md:grid-cols-2 lg:grid-cols-4'>
          <div className='rounded-lg border bg-card p-4 shadow-sm'>
            <div className='flex items-center gap-2 mb-3'>
              <Calculator className='h-5 w-5 text-finance-secondary-400' />
              <h3 className='font-medium'>Calcular Poupança</h3>
            </div>
            <p className='text-sm text-muted-foreground'>
              Determine quanto você precisa economizar para atingir seus
              objetivos de aposentadoria.
            </p>
          </div>

          <div className='rounded-lg border bg-card p-4 shadow-sm'>
            <div className='flex items-center gap-2 mb-3'>
              <PiggyBank className='h-5 w-5 text-finance-secondary-400' />
              <h3 className='font-medium'>Otimizar Contribuições</h3>
            </div>
            <p className='text-sm text-muted-foreground'>
              Encontre a taxa de contribuição ideal baseada em sua renda e
              objetivos.
            </p>
          </div>

          <div className='rounded-lg border bg-card p-4 shadow-sm'>
            <div className='flex items-center gap-2 mb-3'>
              <TrendingUp className='h-5 w-5 text-finance-secondary-400' />
              <h3 className='font-medium'>Crescimento dos Investimentos</h3>
            </div>
            <p className='text-sm text-muted-foreground'>
              Visualize como seus investimentos crescerão ao longo do tempo com
              diferentes taxas.
            </p>
          </div>

          <div className='rounded-lg border bg-card p-4 shadow-sm'>
            <div className='flex items-center gap-2 mb-3'>
              <Wallet className='h-5 w-5 text-finance-secondary-400' />
              <h3 className='font-medium'>Estratégia de Saque</h3>
            </div>
            <p className='text-sm text-muted-foreground'>
              Planeje sua renda na aposentadoria e veja por quanto tempo seus
              fundos durarão.
            </p>
          </div>
        </div>

        {/* Main calculator */}
        <RetirementCalculator />

        {/* Additional information */}
        <div className='mt-10 text-sm text-muted-foreground'>
          <h2 className='text-lg font-medium text-foreground mb-2'>
            Sobre o Planejamento de Aposentadoria
          </h2>
          <p className='mb-4'>
            O planejamento de aposentadoria é o processo de determinar objetivos
            de renda na aposentadoria, as ações e decisões necessárias para
            alcançar esses objetivos. A calculadora acima ajuda você a entender
            como sua taxa de poupança atual, retornos dos investimentos e idade
            de aposentadoria podem afetar seu futuro financeiro.
          </p>
          <h3 className='font-medium text-foreground mb-2'>
            Conceitos Principais
          </h3>
          <ul className='list-disc pl-5 space-y-2'>
            <li>
              <strong>Fase de Acumulação:</strong> O período durante o qual você
              economiza e investe para a aposentadoria.
            </li>
            <li>
              <strong>Fase de Distribuição:</strong> O período durante a
              aposentadoria quando você faz saques de suas economias.
            </li>
            <li>
              <strong>Fração de Investimento:</strong> A porcentagem de sua
              renda que você economiza para a aposentadoria.
            </li>
            <li>
              <strong>Juros Compostos:</strong> Juros ganhos tanto sobre o
              principal inicial quanto sobre os juros acumulados.
            </li>
            <li>
              <strong>Idade de Depleção:</strong> A idade na qual seus fundos de
              aposentadoria são projetados para serem totalmente esgotados.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
