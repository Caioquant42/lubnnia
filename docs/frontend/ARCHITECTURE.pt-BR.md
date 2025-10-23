# Guia de Arquitetura do Frontend

## Visão Geral

Este documento fornece uma visão abrangente da arquitetura do frontend da Zomma Quant, explicando decisões de design, organização de pastas e fundamentação técnica.

## Stack Tecnológica

### Framework Principal
- **Next.js 13.5.1** com App Router
  - Framework React moderno com renderização server-side
  - App Router usa roteamento baseado em arquivos com convenção `page.tsx`
  - NÃO `index.page.tsx` - esse é um padrão antigo do Next.js

### Componentes UI
- **Radix UI** via **shadcn/ui**
  - Primitivos de componentes acessíveis padrão da indústria
  - Componentes pré-construídos otimizados para customização
  - **Por que Radix UI?**
    - Acessível por padrão (compatível com WCAG)
    - Primitivos sem estilo permitem controle total do design
    - Mantido por equipe profissional
    - Usado por empresas como Vercel, Linear e GitHub
  - Componentes são copiados para o projeto (não pacote npm)
  - Configurado via `components.json` (separado do tsconfig)

### Estilização
- **Tailwind CSS 3.3.3**
  - Framework CSS utility-first
  - Configurado em `tailwind.config.ts`
  - Variáveis de tema customizadas em `app/globals.css`

### Estado & Dados
- **React Hooks** para gerenciamento de estado local
- **Axios** para comunicação com API
- **Supabase** para autenticação e banco de dados

## Estrutura do Projeto

```
frontend/
├── __api__/                    # Camada de serviço de API
│   ├── config.ts              # Configuração e endpoints da API
│   ├── apiService.ts          # Instância base do axios com interceptors
│   ├── collarApi.ts           # API de estratégia Collar
│   ├── coveredcallApi.ts      # API de Covered Call
│   ├── pairstrading.ts        # API de Pairs Trading
│   ├── recommendationsApi.ts  # API de recomendações de analistas
│   ├── rrgApi.ts             # API de Relative Rotation Graph
│   ├── screenerApi.ts        # API de screener de ações
│   ├── volatilityApi.ts      # API de análise de volatilidade
│   └── utils.ts              # Funções utilitárias de API
│
├── app/                       # Next.js 13 App Router
│   ├── (dashboard)/          # Rota agrupada (não afeta URL)
│   │   ├── dashboard/
│   │   ├── market-data/
│   │   ├── options/
│   │   ├── pairstrading/
│   │   ├── portfolio/
│   │   ├── recommendations/
│   │   ├── retirement/
│   │   ├── rrg/
│   │   ├── screener/
│   │   ├── volatility/
│   │   └── layout.tsx        # Wrapper de layout do dashboard
│   ├── auth/                 # Páginas de autenticação
│   ├── checkout/             # Fluxos de pagamento
│   ├── pricing/              # Página de preços
│   ├── layout.tsx            # Layout raiz
│   ├── page.tsx              # Landing page
│   └── globals.css           # Estilos globais
│
├── components/               # Componentes React
│   ├── ui/                  # Componentes shadcn/ui (50 arquivos)
│   ├── charts/              # Componentes de gráficos (RRG, Sunburst)
│   ├── dashboard/           # Widgets específicos do dashboard
│   ├── finance/             # Componentes financeiros (tabelas, gráficos)
│   ├── header/              # Componentes de cabeçalho
│   ├── layout/              # Componentes de layout (Header, Sidebar, Footer)
│   ├── pairstrading/        # Componentes de pairs trading
│   ├── recommendations/     # Componentes de recomendações
│   ├── variation/           # Componentes de variação de ações
│   └── volatility/          # Componentes de análise de volatilidade
│
├── hooks/                   # Custom React hooks
│   ├── useAuth.ts          # Hook de autenticação
│   ├── useIsAdmin.ts       # Verificação de papel admin
│   ├── use-debounce.ts     # Utilitário de debounce
│   └── use-toast.ts        # Notificações toast
│
├── types/                   # Definições de tipos TypeScript
│   ├── index.ts            # Tipos comuns
│   └── retirement.ts       # Tipos da calculadora de aposentadoria
│
├── utils/                   # Funções utilitárias
│   ├── retirementCalculator.ts
│   └── sectorMapping.ts
│
├── public/                  # Assets estáticos
│   └── Logofiles/          # Assets da marca
│       └── For Web/
│           ├── Favicons/   # Ícones do navegador
│           ├── png/        # Logos PNG
│           └── svg/        # Logos SVG
│
├── components.json          # Configuração shadcn/ui
├── tsconfig.json           # Configuração TypeScript
├── tailwind.config.ts      # Configuração Tailwind CSS
├── next.config.js          # Configuração Next.js
└── package.json            # Dependências
```

## Arquivos de Configuração Explicados

### tsconfig.json
- **Propósito**: Configuração do compilador TypeScript para Next.js
- **Aliases de Caminho**: `@/*` mapeia para `frontend/*` para imports mais limpos
- **Exemplo**: `import { Button } from '@/components/ui/button'`

### components.json
- **Propósito**: Configuração da biblioteca de componentes shadcn/ui
- **NÃO é redundante com tsconfig**: Este define caminhos de componentes UI e estilização
- **Define**: Localização dos componentes, preferências de estilo, variáveis CSS

### Dois arquivos tsconfig?
- `frontend/tsconfig.json` - Frontend Next.js principal
- `supabase/functions/tsconfig.json` - Edge Functions Deno/Supabase (runtime diferente)

## Convenções de Caminho de Importação

### Padrão Correto
```typescript
// Use alias @ para todas as importações
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import apiService from '@/__api__/apiService';
import { STRIPE_PRODUCTS } from '@/stripe-config';
```

### Evite Caminhos Relativos
```typescript
// ❌ NÃO: Caminhos relativos
import { Button } from '../../../components/ui/button';

// ✅ FAÇA: Use alias @
import { Button } from '@/components/ui/button';
```

## Arquitetura de API

### Camada de API Centralizada
Todas as chamadas de API passam pelo diretório `__api__/`:

1. **config.ts** - URLs base, endpoints, mensagens de erro
2. **apiService.ts** - Instância Axios com interceptors
3. **APIs de Funcionalidade** - Funções de API específicas por domínio

### Exemplo de Fluxo de API
```typescript
// 1. Definir tipos
export interface StockData {
  symbol: string;
  price: number;
}

// 2. Criar função de API
export const fetchStockData = async (): Promise<StockData[]> => {
  const response = await apiService.get('/stocks');
  return response.data;
};

// 3. Usar no componente
const { data } = await fetchStockData();
```

## Padrões de Componentes

### Convenções de Nomenclatura
- **Páginas**: `page.tsx` (convenção Next.js 13 App Router)
- **Layouts**: `layout.tsx`
- **Componentes**: PascalCase (ex: `StockTable.tsx`)
- **Hooks**: camelCase com prefixo 'use' (ex: `useAuth.ts`)

### Estrutura de Componente
```typescript
/**
 * Descrição do componente
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface ComponentProps {
  title: string;
}

export default function Component({ title }: ComponentProps) {
  const [state, setState] = useState<string>('');
  
  return (
    <div>
      <h1>{title}</h1>
    </div>
  );
}
```

## Fluxo de Autenticação

1. Usuário faz login via `/auth/login`
2. Credenciais verificadas pelo Supabase
3. Dados do usuário armazenados no localStorage
4. Hook `useAuth` gerencia a sessão
5. Rotas protegidas verificam status de autenticação

## Estrutura de Implantação

- **Frontend**: App Next.js (este diretório)
- **Backend**: API Python/Flask (../backend/)
- **Banco de Dados**: PostgreSQL Supabase
- **Funções Supabase**: Edge functions (../supabase/functions/)

## Decisões-Chave de Design

### Por que Radix UI / shadcn/ui?
- **Acessibilidade**: Compatível com WCAG out of the box
- **Customização**: Controle total sobre estilização
- **Qualidade**: Componentes padrão da indústria
- **Não é bloat**: Importe apenas o que você usa
- **Manutenção**: Equipe profissional, atualizações regulares

### Por que Next.js App Router?
- **Moderno**: Arquitetura mais recente do Next.js
- **Performance**: Componentes de servidor, streaming
- **SEO**: SSR e metadata integrados
- **Roteamento baseado em arquivos**: Estrutura intuitiva

### Por que Tailwind CSS?
- **Produtividade**: Escreva estilos diretamente no JSX
- **Consistência**: Sistema de design via config
- **Performance**: Remove CSS não utilizado
- **Manutenibilidade**: Sem arquivos CSS separados

## Padrões Comuns

### Rotas Protegidas
```typescript
// No componente
const { isAuthenticated } = useAuth();

if (!isAuthenticated) {
  router.push('/auth/login');
  return null;
}
```

### Tratamento de Erros de API
```typescript
try {
  const data = await fetchData();
} catch (error) {
  const message = formatApiError(error);
  toast.error(message);
}
```

### Estados de Carregamento
```typescript
const [loading, setLoading] = useState(true);

useEffect(() => {
  fetchData()
    .then(setData)
    .finally(() => setLoading(false));
}, []);

if (loading) return <LoadingSpinner />;
```

## Considerações de Performance

- **Code Splitting**: Automático por rota no Next.js
- **Otimização de Imagem**: Use componente `<Image>` do Next.js
- **Cache de API**: Considere React Query ou SWR no futuro
- **Tamanho do Bundle**: Tree-shaking habilitado

## Melhorias Futuras

- [ ] Adicionar React Query para melhor fetching de dados
- [ ] Implementar error boundaries
- [ ] Adicionar testes E2E (Playwright/Cypress)
- [ ] Configurar Storybook para desenvolvimento de componentes
- [ ] Adicionar monitoramento de performance

## Recursos

- [Documentação Next.js](https://nextjs.org/docs)
- [Documentação shadcn/ui](https://ui.shadcn.com)
- [Documentação Radix UI](https://www.radix-ui.com)
- [Documentação Tailwind CSS](https://tailwindcss.com)

---

**Última Atualização**: Outubro 2024  
**Mantenedores**: Equipe Zomma Quant

