# Guia de Contribuição Frontend

## Bem-vindo!

Obrigado por contribuir com o frontend da Zomma Quant! Este guia vai ajudá-lo a entender nossos padrões de código, convenções e melhores práticas.

## Começando

### Pré-requisitos
- Node.js 18+ e npm/yarn
- Conhecimento básico de React, TypeScript e Next.js
- Familiaridade com Tailwind CSS

### Configuração
```bash
cd frontend
npm install
npm run dev
```

A aplicação rodará em `http://localhost:3000`

## Padrões de Código

### Convenções de Nomenclatura de Arquivos

#### Next.js App Router (✅ Correto)
```
app/
├── page.tsx           # ✅ Página raiz
├── layout.tsx         # ✅ Layout raiz
└── dashboard/
    └── page.tsx       # ✅ Página do dashboard
```

#### NÃO Estes Padrões (❌ Incorreto)
```
app/
├── index.page.tsx     # ❌ Pages Router antigo do Next.js
├── Dashboard.tsx      # ❌ Não é um arquivo de página
└── dashboard.tsx      # ❌ Minúscula para rotas
```

#### Componentes
```
components/
├── ui/
│   └── button.tsx          # ✅ kebab-case para primitivos UI
└── finance/
    └── StockTable.tsx      # ✅ PascalCase para componentes de funcionalidade
```

#### Hooks
```
hooks/
├── useAuth.ts              # ✅ camelCase com prefixo 'use'
└── useIsAdmin.ts           # ✅ camelCase
```

### Ordem de Importação & Convenções

#### Sempre Use Aliases de Caminho
```typescript
// ✅ BOM: Use alias @
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import apiService from '@/__api__/apiService';

// ❌ RUIM: Caminhos relativos
import { Button } from '../../../components/ui/button';
import { useAuth } from '../../hooks/useAuth';
```

#### Ordem de Importação
1. Importações React & Next.js
2. Bibliotecas externas
3. Componentes internos (alias @)
4. Tipos & interfaces
5. Utilitários & helpers
6. Estilos (se houver)

```typescript
// 1. React/Next
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// 2. Bibliotecas externas
import axios from 'axios';
import { format } from 'date-fns';

// 3. Componentes internos
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import StockTable from '@/components/finance/StockTable';

// 4. Tipos
import type { StockData } from '@/types';

// 5. Utilitários
import { formatCurrency } from '@/utils/format';
```

### Diretrizes TypeScript

#### Sempre Defina Tipos
```typescript
// ✅ BOM: Tipos explícitos
interface ComponentProps {
  title: string;
  data: StockData[];
  onSelect?: (id: string) => void;
}

export default function Component({ title, data, onSelect }: ComponentProps) {
  // ...
}

// ❌ RUIM: Sem tipos
export default function Component({ title, data, onSelect }) {
  // TypeScript não pode te ajudar aqui
}
```

#### Use Importações de Tipo Quando Possível
```typescript
// ✅ BOM
import type { User } from '@/types';

// ✅ Também aceitável
import { type User } from '@/types';
```

### Estrutura de Componentes

#### Template de Componentes Funcionais
```typescript
/**
 * Breve descrição do que este componente faz
 * 
 * @example
 * <StockTable data={stocks} onSelect={handleSelect} />
 */
import { useState } from 'react';
import { Button } from '@/components/ui/button';

interface StockTableProps {
  data: Stock[];
  onSelect?: (symbol: string) => void;
}

export default function StockTable({ data, onSelect }: StockTableProps) {
  // 1. Hooks
  const [selectedSymbol, setSelectedSymbol] = useState<string | null>(null);
  
  // 2. Estado derivado
  const sortedData = data.sort((a, b) => b.volume - a.volume);
  
  // 3. Event handlers
  const handleRowClick = (symbol: string) => {
    setSelectedSymbol(symbol);
    onSelect?.(symbol);
  };
  
  // 4. Effects (se necessário)
  useEffect(() => {
    // ...
  }, [data]);
  
  // 5. Helpers de renderização (se complexo)
  const renderRow = (stock: Stock) => (
    <tr key={stock.symbol} onClick={() => handleRowClick(stock.symbol)}>
      {/* ... */}
    </tr>
  );
  
  // 6. Renderização principal
  return (
    <table>
      <tbody>
        {sortedData.map(renderRow)}
      </tbody>
    </table>
  );
}
```

### Estilização com Tailwind

#### Organização de Nomes de Classes
```typescript
// ✅ BOM: Agrupamento lógico
<div className="
  flex items-center justify-between gap-4
  p-4 rounded-lg
  bg-slate-800 hover:bg-slate-700
  transition-colors duration-200
">
```

#### Use `cn()` para Classes Condicionais
```typescript
import { cn } from '@/lib/utils';

<Button 
  className={cn(
    "base-classes",
    isActive && "active-classes",
    isDisabled && "disabled-classes"
  )}
/>
```

### Integração com API

#### Crie Funções de Serviço de API
```typescript
// Em __api__/stockApi.ts

/**
 * Busca dados de ações para o símbolo fornecido
 * @param symbol - Símbolo ticker da ação (ex: 'PETR4')
 * @returns Promise<StockData>
 */
export const fetchStockData = async (symbol: string): Promise<StockData> => {
  try {
    const response = await apiService.get(`/stocks/${symbol}`);
    return response.data;
  } catch (error) {
    throw formatApiError(error);
  }
};
```

#### Use nos Componentes
```typescript
const [data, setData] = useState<StockData | null>(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState<string | null>(null);

useEffect(() => {
  fetchStockData('PETR4')
    .then(setData)
    .catch(err => setError(err.message))
    .finally(() => setLoading(false));
}, []);

if (loading) return <LoadingSpinner />;
if (error) return <ErrorMessage message={error} />;
if (!data) return null;
```

### Gerenciamento de Estado

#### Estado Local (useState)
Use para:
- Estado de UI (modais, dropdowns, toggles)
- Inputs de formulário
- Dados específicos do componente

```typescript
const [isOpen, setIsOpen] = useState(false);
const [searchTerm, setSearchTerm] = useState('');
```

#### Context (useContext)
Use para:
- Estado de autenticação
- Preferências de tema
- Estado global de UI

#### Alternativa ao Props Drilling
Para 2-3 níveis, props são suficientes. Além disso, considere:
1. Composição (children props)
2. Context API
3. Biblioteca de gerenciamento de estado (futuro: React Query, Zustand)

### Tratamento de Erros

#### Erros de API
```typescript
try {
  const data = await fetchData();
  setData(data);
} catch (error) {
  const message = formatApiError(error);
  toast.error(message);
  console.error('Falha ao buscar dados:', error);
}
```

#### Error Boundaries de Componente (TODO)
```typescript
// Implementação futura
<ErrorBoundary fallback={<ErrorFallback />}>
  <YourComponent />
</ErrorBoundary>
```

### Comentários & Documentação

#### Quando Comentar
✅ **Comente:**
- Lógica de negócio complexa
- Workarounds não óbvios
- Integrações com API
- Explicações de algoritmos
- Funções/componentes públicos

❌ **Não comente:**
- Código óbvio (`// incrementa contador`)
- Informação redundante
- Código comentado (delete, use histórico do git)

#### JSDoc para APIs Públicas
```typescript
/**
 * Calcula a data de aposentadoria baseada em contribuições
 * 
 * @param currentAge - Idade atual em anos
 * @param monthlyContribution - Contribuição mensal em BRL
 * @param targetAmount - Valor alvo de aposentadoria em BRL
 * @returns Data estimada de aposentadoria
 * 
 * @example
 * const retirementDate = calculateRetirement(30, 1000, 1000000);
 */
export function calculateRetirement(
  currentAge: number,
  monthlyContribution: number,
  targetAmount: number
): Date {
  // Implementação
}
```

### Testes (Futuro)

#### Testes Unitários
```typescript
// Component.test.tsx
import { render, screen } from '@testing-library/react';
import StockTable from './StockTable';

describe('StockTable', () => {
  it('renderiza dados de ações corretamente', () => {
    const mockData = [{ symbol: 'PETR4', price: 30.50 }];
    render(<StockTable data={mockData} />);
    expect(screen.getByText('PETR4')).toBeInTheDocument();
  });
});
```

### Fluxo Git

#### Nomenclatura de Branches
```
feature/add-stock-screener
fix/volatility-calculation
refactor/api-layer
docs/update-architecture
```

#### Mensagens de Commit
```
feat: adiciona dashboard de pairs trading
fix: corrige cálculo de quadrante RRG
refactor: simplifica tratamento de erros de API
docs: atualiza guia de contribuição
style: formata com prettier
```

#### Antes de Fazer Commit
1. ✅ Teste suas mudanças localmente
2. ✅ Execute `npm run lint` (se configurado)
3. ✅ Verifique erros no console
4. ✅ Remova código de debug e console.logs
5. ✅ Atualize documentação relevante

### Melhores Práticas de Performance

#### Imagens
```typescript
// ✅ BOM: Use Next.js Image
import Image from 'next/image';

<Image 
  src="/logo.png" 
  alt="Logo"
  width={200}
  height={50}
  priority // Para imagens above-the-fold
/>

// ❌ RUIM: Tag img regular
<img src="/logo.png" alt="Logo" />
```

#### Lazy Loading
```typescript
// Para componentes pesados
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/charts/HeavyChart'), {
  loading: () => <LoadingSpinner />,
  ssr: false // Se usar APIs apenas de browser
});
```

#### Memoização
```typescript
// Para cálculos caros
const sortedData = useMemo(() => 
  data.sort((a, b) => b.price - a.price),
  [data]
);

// Para callbacks passados a filhos
const handleClick = useCallback(() => {
  // Lógica do handler
}, [dependencies]);
```

### Acessibilidade

#### Sempre Inclua ARIA Labels
```typescript
<button aria-label="Fechar modal" onClick={onClose}>
  <X className="h-4 w-4" />
</button>
```

#### Navegação por Teclado
Garanta que todos os elementos interativos sejam acessíveis por teclado:
```typescript
<div 
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  Clique em mim
</div>
```

#### Use HTML Semântico
```typescript
// ✅ BOM
<nav>
  <ul>
    <li><a href="/dashboard">Dashboard</a></li>
  </ul>
</nav>

// ❌ RUIM
<div>
  <div>
    <div onClick={navigate}>Dashboard</div>
  </div>
</div>
```

## Armadilhas Comuns

### ❌ Não: Use `index.page.tsx`
Next.js 13 App Router usa `page.tsx`, não `index.page.tsx`

### ❌ Não: Instale node_modules Duplicados
Nunca crie pastas `node_modules` aninhadas. Use a da raiz.

### ❌ Não: Use Importações Relativas
```typescript
// ❌ RUIM
import { Button } from '../../../components/ui/button';

// ✅ BOM
import { Button } from '@/components/ui/button';
```

### ❌ Não: Modifique components.json Manualmente
Este arquivo é gerenciado pelo CLI shadcn. Não edite a menos que saiba o que está fazendo.

### ❌ Não: Misture Abordagens de Estilização
Fique com Tailwind. Não misture CSS modules, styled-components, etc.

## Precisa de Ajuda?

- Verifique `/docs/frontend/ARCHITECTURE.pt-BR.md` para visão geral da arquitetura
- Revise componentes existentes para padrões
- Pergunte à equipe no Slack/Discord
- Crie uma issue se encontrar um bug

## Checklist de Code Review

Antes de submeter um PR:
- [ ] Código segue convenções de nomenclatura
- [ ] Usa aliases de caminho @, não importações relativas
- [ ] Tipos TypeScript estão definidos
- [ ] Componentes têm comentários JSDoc
- [ ] Sem console.logs ou código de debug
- [ ] Tratamento de erros implementado
- [ ] Estados de carregamento tratados
- [ ] Acessibilidade considerada
- [ ] Testado localmente
- [ ] Sem erros de linter

## Recursos

- [Docs Next.js App Router](https://nextjs.org/docs/app)
- [Manual TypeScript](https://www.typescriptlang.org/docs/)
- [Docs Tailwind CSS](https://tailwindcss.com/docs)
- [Docs shadcn/ui](https://ui.shadcn.com)
- [Referência React Hooks](https://react.dev/reference/react)

---

**Dúvidas?** Entre em contato com a equipe ou crie uma issue!

