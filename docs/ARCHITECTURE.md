# Frontend Architecture Guide

## Overview

This document provides a comprehensive overview of the Zomma Quant frontend architecture, explaining design decisions, folder organization, and technical rationale.

## Technology Stack

### Core Framework
- **Next.js 13.5.1** with App Router
  - Modern React framework with server-side rendering
  - App Router uses file-based routing with `page.tsx` convention
  - NOT `index.page.tsx` - that's an older Next.js pattern

### UI Components
- **Radix UI** via **shadcn/ui**
  - Industry-standard accessible component primitives
  - Pre-built components optimized for customization
  - **Why Radix UI?**
    - Accessible by default (WCAG compliant)
    - Unstyled primitives allow full design control
    - Maintained by professional team
    - Used by companies like Vercel, Linear, and GitHub
  - Components are copied into the project (not npm package)
  - Configured via `components.json` (separate from tsconfig)

### Styling
- **Tailwind CSS 3.3.3**
  - Utility-first CSS framework
  - Configured in `tailwind.config.ts`
  - Custom theme variables in `app/globals.css`

### State & Data
- **React Hooks** for local state management
- **Axios** for API communication
- **Supabase** for authentication and database

## Project Structure

```
frontend/
├── __api__/                    # API service layer
│   ├── config.ts              # API configuration and endpoints
│   ├── apiService.ts          # Base axios instance with interceptors
│   ├── collarApi.ts           # Collar strategy API
│   ├── coveredcallApi.ts      # Covered call API
│   ├── pairstrading.ts        # Pairs trading API
│   ├── recommendationsApi.ts  # Analyst recommendations API
│   ├── rrgApi.ts             # Relative Rotation Graph API
│   ├── screenerApi.ts        # Stock screener API
│   ├── volatilityApi.ts      # Volatility analysis API
│   └── utils.ts              # API utility functions
│
├── app/                       # Next.js 13 App Router
│   ├── (dashboard)/          # Grouped route (doesn't affect URL)
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
│   │   └── layout.tsx        # Dashboard layout wrapper
│   ├── auth/                 # Authentication pages
│   ├── checkout/             # Payment flows
│   ├── pricing/              # Pricing page
│   ├── layout.tsx            # Root layout
│   ├── page.tsx              # Landing page
│   └── globals.css           # Global styles
│
├── components/               # React components
│   ├── ui/                  # shadcn/ui components (50 files)
│   ├── charts/              # Chart components (RRG, Sunburst)
│   ├── dashboard/           # Dashboard-specific widgets
│   ├── finance/             # Financial components (tables, charts)
│   ├── header/              # Header components
│   ├── layout/              # Layout components (Header, Sidebar, Footer)
│   ├── pairstrading/        # Pairs trading components
│   ├── recommendations/     # Recommendations components
│   ├── variation/           # Stock variation components
│   └── volatility/          # Volatility analysis components
│
├── hooks/                   # Custom React hooks
│   ├── useAuth.ts          # Authentication hook
│   ├── useIsAdmin.ts       # Admin role check
│   ├── use-debounce.ts     # Debounce utility
│   └── use-toast.ts        # Toast notifications
│
├── types/                   # TypeScript type definitions
│   ├── index.ts            # Common types
│   └── retirement.ts       # Retirement calculator types
│
├── utils/                   # Utility functions
│   ├── retirementCalculator.ts
│   └── sectorMapping.ts
│
├── public/                  # Static assets
│   └── Logofiles/          # Brand assets
│       └── For Web/
│           ├── Favicons/   # Browser icons
│           ├── png/        # PNG logos
│           └── svg/        # SVG logos
│
├── components.json          # shadcn/ui configuration
├── tsconfig.json           # TypeScript configuration
├── tailwind.config.ts      # Tailwind CSS configuration
├── next.config.js          # Next.js configuration
└── package.json            # Dependencies
```

## Configuration Files Explained

### tsconfig.json
- **Purpose**: TypeScript compiler configuration for Next.js
- **Path Aliases**: `@/*` maps to `frontend/*` for cleaner imports
- **Example**: `import { Button } from '@/components/ui/button'`

### components.json
- **Purpose**: shadcn/ui component library configuration
- **NOT redundant with tsconfig**: This defines UI component paths and styling
- **Defines**: Component location, style preferences, CSS variables

### Two tsconfig Files?
- `frontend/tsconfig.json` - Main Next.js frontend
- `supabase/functions/tsconfig.json` - Deno/Supabase Edge Functions (different runtime)

## Import Path Conventions

### Correct Pattern
```typescript
// Use @ alias for all imports
import { Button } from '@/components/ui/button';
import { useAuth } from '@/hooks/useAuth';
import apiService from '@/__api__/apiService';
import { STRIPE_PRODUCTS } from '@/stripe-config';
```

### Avoid Relative Paths
```typescript
// ❌ DON'T: Relative paths
import { Button } from '../../../components/ui/button';

// ✅ DO: Use @ alias
import { Button } from '@/components/ui/button';
```

## API Architecture

### Centralized API Layer
All API calls go through the `__api__/` directory:

1. **config.ts** - Base URLs, endpoints, error messages
2. **apiService.ts** - Axios instance with interceptors
3. **Feature APIs** - Domain-specific API functions

### Example API Flow
```typescript
// 1. Define types
export interface StockData {
  symbol: string;
  price: number;
}

// 2. Create API function
export const fetchStockData = async (): Promise<StockData[]> => {
  const response = await apiService.get('/stocks');
  return response.data;
};

// 3. Use in component
const { data } = await fetchStockData();
```

## Component Patterns

### Naming Conventions
- **Pages**: `page.tsx` (Next.js 13 App Router convention)
- **Layouts**: `layout.tsx`
- **Components**: PascalCase (e.g., `StockTable.tsx`)
- **Hooks**: camelCase with 'use' prefix (e.g., `useAuth.ts`)

### Component Structure
```typescript
/**
 * Component description
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

## Authentication Flow

1. User logs in via `/auth/login`
2. Credentials verified by Supabase
3. User data stored in localStorage
4. `useAuth` hook manages session
5. Protected routes check authentication status

## Deployment Structure

- **Frontend**: Next.js app (this directory)
- **Backend**: Python/Flask API (../backend/)
- **Database**: Supabase PostgreSQL
- **Supabase Functions**: Edge functions (../supabase/functions/)

## Key Design Decisions

### Why Radix UI / shadcn/ui?
- **Accessibility**: WCAG compliant out of the box
- **Customization**: Full control over styling
- **Quality**: Industry-standard components
- **Not bloat**: Only import what you use
- **Maintenance**: Professional team, regular updates

### Why Next.js App Router?
- **Modern**: Latest Next.js architecture
- **Performance**: Server components, streaming
- **SEO**: Built-in SSR and metadata
- **File-based routing**: Intuitive structure

### Why Tailwind CSS?
- **Productivity**: Write styles directly in JSX
- **Consistency**: Design system via config
- **Performance**: Purges unused CSS
- **Maintainability**: No separate CSS files

## Common Patterns

### Protected Routes
```typescript
// In component
const { isAuthenticated } = useAuth();

if (!isAuthenticated) {
  router.push('/auth/login');
  return null;
}
```

### API Error Handling
```typescript
try {
  const data = await fetchData();
} catch (error) {
  const message = formatApiError(error);
  toast.error(message);
}
```

### Loading States
```typescript
const [loading, setLoading] = useState(true);

useEffect(() => {
  fetchData()
    .then(setData)
    .finally(() => setLoading(false));
}, []);

if (loading) return <LoadingSpinner />;
```

## Performance Considerations

- **Code Splitting**: Next.js automatic by route
- **Image Optimization**: Use Next.js `<Image>` component
- **API Caching**: Consider React Query or SWR for future
- **Bundle Size**: Tree-shaking enabled

## Future Improvements

- [ ] Add React Query for better data fetching
- [ ] Implement error boundaries
- [ ] Add E2E tests (Playwright/Cypress)
- [ ] Set up Storybook for component development
- [ ] Add performance monitoring

## Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [shadcn/ui Documentation](https://ui.shadcn.com)
- [Radix UI Documentation](https://www.radix-ui.com)
- [Tailwind CSS Documentation](https://tailwindcss.com)

---

**Last Updated**: October 2024  
**Maintainers**: Zomma Quant Team

