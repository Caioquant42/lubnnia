# Dashboard Improvement Suggestions

> **Context**  
> These ideas are based on the current implementation inside `frontend/app/(dashboard)` and the state of sibling components/services.  
> The list is intentionally long & aspirational – treat it as a backlog, *not* a single sprint.

---

## 1. UX & Visual Design

1. **Progressive Disclosure**  
   Collapse less–important widgets by default and surface key metrics first. Use accordions or tabs for secondary data to reduce initial cognitive load.
2. **KPI Hierarchy**  
   Emphasise the most–actionable metrics (P/L, risk, allocation drift) with larger font sizes & colour–coded trend chips.
3. **Contextual Tool-tips**  
   Add `Tooltip` components that explain niche terms (e.g. *IV*, *Z-Score*) on hover / long-press.
4. **Skeleton Loading States**  
   Replace spinners with skeleton placeholders to create a smoother perceived performance.
5. **Empty States**  
   For widgets with no data (e.g. empty portfolio), provide educational copy + CTA to import data.
6. **Theme Customisation**  
   Allow switching between light/dark & a high-contrast accessibility theme via `ThemeProvider`.
7. **Widget Re-ordering**  
   Enable drag-and-drop re-ordering and persistent layout (localStorage or Supabase `profiles` table).
8. **Global Search Shortcuts**  
   Use `cmd + k` / `ctrl + k` to open the market/symbol search bar anywhere in the dashboard.

## 2. Information Architecture

1. **Modular Routes**  
   Break gigantic pages (e.g. `/recommendations/brasil`) into sub-routes and lazy-loaded components to keep bundle size small.
2. **Dedicated Portfolio Route**  
   Move "Meu Portfólio" to `/portfolio` with summary cards in the dashboard that deep-link into the full view.
3. **Notification Center**  
   Add `/notifications` route with unread badges, leveraging Supabase real-time channel for push updates.

## 3. Performance Optimisation

1. **Code-Splitting**  
   Confirm that heavy charts (e.g. `SunburstChart`, `RRGChart`) are dynamically imported with `next/dynamic` and `ssr: false`.
2. **Memoisation**  
   Wrap expensive calculations in `useMemo` / `useCallback` (seen missing in `TradingOpportunitiesHub`).
3. **Virtualised Lists**  
   Replace long tables with `react-virtual` or `tanstack-virtual` to avoid DOM bloat.
4. **Image Optimisation**  
   Use `next/image` for any static logos/avatars.
5. **Bundle Analysis**  
   Run `next build --profile` + `webpack-bundle-analyser` to locate large vendor bundles.

## 4. Data Layer & API

1. **React-Query / TanStack Query**  
   Migrate manual `fetch` calls to a query cache for automatic retries, polling, pagination & optimistic updates.
2. **Infinite Scrolling**  
   Implement for news feeds / signal logs instead of pagination.
3. **WebSockets**  
   Adopt Supabase realtime or Socket.IO to stream market data & trade signals.
4. **Server Actions (Next 13+)**  
   Use server actions to move mutating logic away from the client, reducing bundle size and exposing a typed API.
5. **Error Boundary Strategy**  
   Wrap each widget in an error boundary to prevent a single failure from blanking the entire dashboard.

## 5. State Management

1. **Zustand / Jotai**  
   Centralise ephemeral UI state (sidebar collapse, theme, layout) away from prop-drilling.
2. **Persisted Settings**  
   Save user preferences (theme, widget order) via browser storage + Supabase sync when authenticated.

## 6. Accessibility (a11y)

1. **Keyboard Navigation**  
   Ensure focus rings are visible; verify every interactive element is reachable via `Tab`.
2. **ARIA Labels**  
   Provide descriptive labels for SVG icons imported from `lucide-react`.
3. **Colour Contrast**  
   Audit dark-theme colour tokens with WCAG AA – adjust if contrast < 4.5.
4. **Screen Reader Announcements**  
   Use `aria-live` regions for real-time alerts (e.g. "New trading signal received").

## 7. Testing & Quality

1. **Unit Tests**  
   Expand existing Jest tests to cover hooks (`useIsAdmin`, `useAuth`) and critical components.
2. **Component Storybook**  
   Document charts & widgets in isolation; supports design hand-off & visual regression tests.
3. **E2E Tests**  
   Integrate Playwright to test dashboard load, navigation, and crucial workflows (login → dashboard → trade).

## 8. Analytics & Telemetry

1. **User Behaviour Tracking**  
   Instrument click & dwell times on widgets to prioritise features.
2. **Performance Metrics**  
   Capture CLS/LCP/FID via Next.js `analytics` & export to Supabase / Google Analytics.
3. **Error Logging**  
   Add Sentry to surface runtime exceptions across both FE & BE.

## 9. Internationalisation (i18n)

1. **Locale Files**  
   Extract hard-coded Portuguese strings into JSON locale files using `next-intl`.
2. **Dynamic Date/Number Formatting**  
   Use `Intl.DateTimeFormat` & `Intl.NumberFormat` based on user locale.

## 10. Dev X & CI/CD

1. **Husky + Lint-Staged**  
   Enforce `eslint --fix` & `prettier` on commit.
2. **GitHub Actions**  
   Add workflow to run tests, build, and deploy preview to Vercel.
3. **Storybook Chromatic**  
   Automated visual regression checks on each PR.

---

### Prioritisation Cheat-Sheet

| Impact | Effort | Suggestion |
| ------ | ------ | ---------- |
| High   | Low    | Skeleton loading states, Tooltip glossary, TanStack Query migration |
| High   | Med    | Error boundaries, WebSocket live data, Code-splitting heavy charts |
| High   | High   | Widget re-ordering with persistence, Real portfolio route |
| Med    | Low    | ARIA labels & colour contrast fixes |
| Med    | Med    | Virtualised lists, Bundle analysis |
| Med    | High   | Drag-and-drop layout builder |
| Low    | Low    | Analytics instrumentation |
| Low    | Med    | i18n extraction |
| Low    | High   | Full Storybook & visual regression suite |

> 📌 **Tip:** Start with low-hanging fruits (skeletons, ARIA labels, query caching) before tackling structural changes like drag-and-drop layouts.
