# Frontend Contributing Guide

## Welcome!

Thank you for contributing to Zomma Quant's frontend! This guide will help you understand our code standards, conventions, and best practices.

## Getting Started

### Prerequisites
- Node.js 18+ and npm/yarn
- Basic understanding of React, TypeScript, and Next.js
- Familiarity with Tailwind CSS

### Setup
```bash
cd frontend
npm install
npm run dev
```

The app will run on `http://localhost:3000`

## Code Standards

### File Naming Conventions

#### Next.js App Router (✅ Correct)
```
app/
├── page.tsx           # ✅ Root page
├── layout.tsx         # ✅ Root layout
└── dashboard/
    └── page.tsx       # ✅ Dashboard page
```

#### NOT These Patterns (❌ Incorrect)
```
app/
├── index.page.tsx     # ❌ Old Next.js Pages Router
├── Dashboard.tsx      # ❌ Not a page file
└── dashboard.tsx      # ❌ Lowercase for routes
```

#### Components
```
components/
├── ui/
│   └── button.tsx          # ✅ kebab-case for UI primitives
└── finance/
    └── StockTable.tsx      # ✅ PascalCase for feature components
```

#### Hooks
```
hooks/
├── useAuth.ts              # ✅ camelCase with 'use' prefix
└── useIsAdmin.ts           # ✅ camelCase
```

### Import Order & Conventions

#### Always Use Path Aliases
```typescript
// ✅ GOOD: Use @ alias
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import apiService from '@/__api__/apiService';

// ❌ BAD: Relative paths
import { Button } from '../../../components/ui/button';
import { useAuth } from '../../hooks/useAuth';
```

#### Import Order
1. React & Next.js imports
2. External libraries
3. Internal components (@ alias)
4. Types & interfaces
5. Utilities & helpers
6. Styles (if any)

```typescript
// 1. React/Next
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// 2. External libraries
import axios from 'axios';
import { format } from 'date-fns';

// 3. Internal components
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import StockTable from '@/components/finance/StockTable';

// 4. Types
import type { StockData } from '@/types';

// 5. Utilities
import { formatCurrency } from '@/utils/format';
```

### TypeScript Guidelines

#### Always Define Types
```typescript
// ✅ GOOD: Explicit types
interface ComponentProps {
  title: string;
  data: StockData[];
  onSelect?: (id: string) => void;
}

export default function Component({ title, data, onSelect }: ComponentProps) {
  // ...
}

// ❌ BAD: No types
export default function Component({ title, data, onSelect }) {
  // TypeScript can't help you here
}
```

#### Use Type Imports When Possible
```typescript
// ✅ GOOD
import type { User } from '@/types';

// ✅ Also acceptable
import { type User } from '@/types';
```

### Component Structure

#### Functional Components Template
```typescript
/**
 * Brief description of what this component does
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
  
  // 2. Derived state
  const sortedData = data.sort((a, b) => b.volume - a.volume);
  
  // 3. Event handlers
  const handleRowClick = (symbol: string) => {
    setSelectedSymbol(symbol);
    onSelect?.(symbol);
  };
  
  // 4. Effects (if needed)
  useEffect(() => {
    // ...
  }, [data]);
  
  // 5. Render helpers (if complex)
  const renderRow = (stock: Stock) => (
    <tr key={stock.symbol} onClick={() => handleRowClick(stock.symbol)}>
      {/* ... */}
    </tr>
  );
  
  // 6. Main render
  return (
    <table>
      <tbody>
        {sortedData.map(renderRow)}
      </tbody>
    </table>
  );
}
```

### Styling with Tailwind

#### Class Name Organization
```typescript
// ✅ GOOD: Logical grouping
<div className="
  flex items-center justify-between gap-4
  p-4 rounded-lg
  bg-slate-800 hover:bg-slate-700
  transition-colors duration-200
">
```

#### Use `cn()` for Conditional Classes
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

### API Integration

#### Create API Service Functions
```typescript
// In __api__/stockApi.ts

/**
 * Fetches stock data for the given symbol
 * @param symbol - Stock ticker symbol (e.g., 'PETR4')
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

#### Use in Components
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

### State Management

#### Local State (useState)
Use for:
- UI state (modals, dropdowns, toggles)
- Form inputs
- Component-specific data

```typescript
const [isOpen, setIsOpen] = useState(false);
const [searchTerm, setSearchTerm] = useState('');
```

#### Context (useContext)
Use for:
- Auth state
- Theme preferences
- Global UI state

#### Props Drilling Alternative
For 2-3 levels, props are fine. Beyond that, consider:
1. Composition (children props)
2. Context API
3. State management library (future: React Query, Zustand)

### Error Handling

#### API Errors
```typescript
try {
  const data = await fetchData();
  setData(data);
} catch (error) {
  const message = formatApiError(error);
  toast.error(message);
  console.error('Failed to fetch data:', error);
}
```

#### Component Error Boundaries (TODO)
```typescript
// Future implementation
<ErrorBoundary fallback={<ErrorFallback />}>
  <YourComponent />
</ErrorBoundary>
```

### Comments & Documentation

#### When to Comment
✅ **Do comment:**
- Complex business logic
- Non-obvious workarounds
- API integrations
- Algorithm explanations
- Public functions/components

❌ **Don't comment:**
- Obvious code (`// increment counter`)
- Redundant information
- Commented-out code (delete it, use git history)

#### JSDoc for Public APIs
```typescript
/**
 * Calculates the retirement date based on contributions
 * 
 * @param currentAge - Current age in years
 * @param monthlyContribution - Monthly contribution in BRL
 * @param targetAmount - Target retirement amount in BRL
 * @returns Estimated retirement date
 * 
 * @example
 * const retirementDate = calculateRetirement(30, 1000, 1000000);
 */
export function calculateRetirement(
  currentAge: number,
  monthlyContribution: number,
  targetAmount: number
): Date {
  // Implementation
}
```

### Testing (Future)

#### Unit Tests
```typescript
// Component.test.tsx
import { render, screen } from '@testing-library/react';
import StockTable from './StockTable';

describe('StockTable', () => {
  it('renders stock data correctly', () => {
    const mockData = [{ symbol: 'PETR4', price: 30.50 }];
    render(<StockTable data={mockData} />);
    expect(screen.getByText('PETR4')).toBeInTheDocument();
  });
});
```

### Git Workflow

#### Branch Naming
```
feature/add-stock-screener
fix/volatility-calculation
refactor/api-layer
docs/update-architecture
```

#### Commit Messages
```
feat: add pairs trading dashboard
fix: correct RRG quadrant calculation
refactor: simplify API error handling
docs: update contributing guide
style: format with prettier
```

#### Before Committing
1. ✅ Test your changes locally
2. ✅ Run `npm run lint` (if configured)
3. ✅ Check for console errors
4. ✅ Remove debug code and console.logs
5. ✅ Update relevant documentation

### Performance Best Practices

#### Images
```typescript
// ✅ GOOD: Use Next.js Image
import Image from 'next/image';

<Image 
  src="/logo.png" 
  alt="Logo"
  width={200}
  height={50}
  priority // For above-the-fold images
/>

// ❌ BAD: Regular img tag
<img src="/logo.png" alt="Logo" />
```

#### Lazy Loading
```typescript
// For heavy components
import dynamic from 'next/dynamic';

const HeavyChart = dynamic(() => import('@/components/charts/HeavyChart'), {
  loading: () => <LoadingSpinner />,
  ssr: false // If it uses browser-only APIs
});
```

#### Memoization
```typescript
// For expensive calculations
const sortedData = useMemo(() => 
  data.sort((a, b) => b.price - a.price),
  [data]
);

// For callbacks passed to children
const handleClick = useCallback(() => {
  // Handler logic
}, [dependencies]);
```

### Accessibility

#### Always Include ARIA Labels
```typescript
<button aria-label="Close modal" onClick={onClose}>
  <X className="h-4 w-4" />
</button>
```

#### Keyboard Navigation
Ensure all interactive elements are keyboard accessible:
```typescript
<div 
  role="button"
  tabIndex={0}
  onClick={handleClick}
  onKeyDown={(e) => e.key === 'Enter' && handleClick()}
>
  Click me
</div>
```

#### Use Semantic HTML
```typescript
// ✅ GOOD
<nav>
  <ul>
    <li><a href="/dashboard">Dashboard</a></li>
  </ul>
</nav>

// ❌ BAD
<div>
  <div>
    <div onClick={navigate}>Dashboard</div>
  </div>
</div>
```

## Common Pitfalls

### ❌ Don't: Use `index.page.tsx`
Next.js 13 App Router uses `page.tsx`, not `index.page.tsx`

### ❌ Don't: Install Duplicate node_modules
Never create nested `node_modules` folders. Use the root one.

### ❌ Don't: Use Relative Imports
```typescript
// ❌ BAD
import { Button } from '../../../components/ui/button';

// ✅ GOOD
import { Button } from '@/components/ui/button';
```

### ❌ Don't: Modify components.json Manually
This file is managed by shadcn CLI. Don't edit unless you know what you're doing.

### ❌ Don't: Mix Styling Approaches
Stick with Tailwind. Don't mix CSS modules, styled-components, etc.

## Need Help?

- Check `/docs/frontend/ARCHITECTURE.md` for architecture overview
- Review existing components for patterns
- Ask the team in Slack/Discord
- Create an issue if you find a bug

## Code Review Checklist

Before submitting a PR:
- [ ] Code follows naming conventions
- [ ] Uses @ path aliases, not relative imports
- [ ] TypeScript types are defined
- [ ] Components have JSDoc comments
- [ ] No console.logs or debug code
- [ ] Error handling is implemented
- [ ] Loading states are handled
- [ ] Accessibility considered
- [ ] Tested locally
- [ ] No linter errors

## Resources

- [Next.js App Router Docs](https://nextjs.org/docs/app)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [shadcn/ui Docs](https://ui.shadcn.com)
- [React Hooks Reference](https://react.dev/reference/react)

---

**Questions?** Reach out to the team or create an issue!

