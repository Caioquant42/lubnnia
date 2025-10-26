'use client';

import {
  ArrowLeftRight,
  BarChart3,
  Calculator,
  ChevronDown,
  ChevronRight,
  Home,
  Menu,
  PanelLeftClose,
  PanelLeftOpen,
  ScanSearch,
  Share2,
  Star,
  TrendingUp,
} from 'lucide-react';
import Image from 'next/image';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';

import { cn } from '@/lib/utils';

import { Button } from '@/components/ui/button';
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from '@/components/ui/collapsible';

import { createClientBrowser } from '@/lib/supabaseClient';

import logoModified from '../../../../public/logoFiles/web/svg/logo_modified.svg';

type NavItem = {
  title: string;
  href: string;
  icon: React.ReactNode;
  submenu?: boolean;
  submenuItems?: {
    title: string;
    href: string;
  }[];
};

const supabase = createClientBrowser();

const mainNavItems: NavItem[] = [
  {
    title: 'Dashboard',
    href: '/dashboard',
    icon: <Home className='h-5 w-5' />,
  },
  {
    title: 'Recomendações',
    href: '/recommendations',
    icon: <TrendingUp className='h-5 w-5' />,
    submenu: true,
    submenuItems: [
      {
        title: 'Brasil',
        href: '/recommendations/brasil',
      },
    ],
  },
  {
    title: 'Volatilidade',
    href: '/volatility',
    icon: <BarChart3 className='h-5 w-5' />,
  },
  {
    title: 'Screener',
    href: '/screener',
    icon: <ScanSearch className='h-5 w-5' />,
    submenu: true,
    submenuItems: [
      {
        title: 'RSI',
        href: '/screener/RSI',
      },
    ],
  },
  {
    title: 'Long & Short',
    href: '/pairstrading/',
    icon: <ArrowLeftRight className='h-5 w-5' />,
  },
];

const otherNavItems: NavItem[] = [
  {
    title: 'Estratégias',
    href: '/strategies',
    icon: <Share2 className='h-5 w-5' />,
    submenu: true,
    submenuItems: [
      {
        title: 'Collar',
        href: '/options/collar',
      },
      {
        title: 'Financiamento Coberto',
        href: '/options/coveredcall',
      },
    ],
  },
  {
    title: 'Calculadoras',
    href: '/retirement',
    icon: <Calculator className='h-5 w-5' />,
    submenu: true,
    submenuItems: [
      {
        title: 'Aposentadoria',
        href: '/retirement',
      },
    ],
  },
];

type SidebarProps = {
  className?: string;
};

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const [expanded, setExpanded] = useState<Record<string, boolean>>({});
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isHovering, setIsHovering] = useState(false);

  // Auto-collapse when user navigates to a new page (except on mobile)
  useEffect(() => {
    const handleRouteChange = () => {
      if (window.innerWidth >= 768) {
        // md breakpoint
        setIsCollapsed(true);
        setSidebarOpen(false);
      }
    };

    handleRouteChange();
  }, [pathname]);

  const toggleExpanded = (title: string) => {
    setExpanded((prev) => ({
      ...prev,
      [title]: !prev[title],
    }));
  };

  const toggleSidebarCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  const handleNavItemClick = () => {
    // Close mobile sidebar
    setSidebarOpen(false);
    // Auto-collapse on desktop
    if (window.innerWidth >= 768) {
      setIsCollapsed(true);
    }
  };

  const isActive = (href: string) => {
    return pathname === href || pathname?.startsWith(`${href}/`);
  };

  // Determine if sidebar should be shown as expanded
  const shouldShowExpanded = !isCollapsed || isHovering;

  return (
    <>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <button
          className='fixed inset-0 z-40 bg-background/80 backdrop-blur-sm md:hidden'
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile sidebar toggle button */}
      <Button
        variant='outline'
        size='icon'
        className='fixed left-4 top-4 z-50 md:hidden'
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        <Menu className='h-5 w-5' />
      </Button>
      {/* Sidebar */}
      <aside
        className={cn(
          'fixed inset-y-0 left-0 z-40 flex flex-col border-r bg-card transition-all duration-300 md:translate-x-0 overflow-hidden',
          // Mobile behavior
          sidebarOpen ? 'translate-x-0' : '-translate-x-full',
          // Desktop behavior - width changes based on collapsed state
          shouldShowExpanded ? 'w-64' : 'w-20 md:translate-x-0',
          className
        )}
        onMouseEnter={() => setIsHovering(true)}
        onMouseLeave={() => setIsHovering(false)}
      >
        {' '}
        {/* Sidebar header */}
        <div className='sticky top-0 z-10 flex h-14 items-center border-b px-2 md:h-[60px]'>
          <Link href='/' className='flex items-center gap-2'>
            <Image
              src={logoModified}
              alt='Zomma Quant Logo'
              width={40}
              height={40}
              className='h-10 w-10 flex-shrink-0'
            />
          </Link>

          {/* Desktop collapse toggle */}
          <Button
            variant='ghost'
            size='icon'
            onClick={toggleSidebarCollapse}
            className='ml-auto hidden md:flex'
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? (
              <PanelLeftOpen className='h-5 w-5' />
            ) : (
              <PanelLeftClose className='h-5 w-5' />
            )}
          </Button>

          {/* Mobile close button */}
          <Button
            variant='ghost'
            size='icon'
            onClick={() => setSidebarOpen(false)}
            className='ml-auto md:hidden'
          >
            <ChevronRight className='h-5 w-5' />
          </Button>
        </div>
        {/* Sidebar content */}
        <div className='flex-1 overflow-y-auto overflow-x-hidden py-4'>
          <nav className='grid items-start px-2 text-sm w-full'>
            {/* Main navigation items */}
            <div className='mb-4'>
              {shouldShowExpanded && (
                <div className='px-3 pb-2 text-xs font-medium text-muted-foreground transition-opacity duration-200'>
                  Main
                </div>
              )}
              <div className='grid gap-1'>
                {mainNavItems.map((item) => (
                  <Link
                    key={item.title}
                    href={item.href}
                    onClick={handleNavItemClick}
                    className={cn(
                      'sidebar-item group relative',
                      isActive(item.href) && 'sidebar-item-active',
                      !shouldShowExpanded && 'justify-center px-2'
                    )}
                    title={!shouldShowExpanded ? item.title : undefined}
                  >
                    <div className='flex items-center gap-3 w-full min-w-0'>
                      <div className='flex-shrink-0'>{item.icon}</div>
                      {shouldShowExpanded && (
                        <span className='transition-opacity duration-200 truncate'>
                          {item.title}
                        </span>
                      )}
                    </div>

                    {/* Tooltip for collapsed state */}
                    {!shouldShowExpanded && (
                      <div className='absolute left-full ml-2 px-2 py-1 bg-popover text-popover-foreground text-sm rounded-md shadow-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50'>
                        {item.title}
                      </div>
                    )}
                  </Link>
                ))}
              </div>
            </div>
            {/* Other navigation items */}
            <div className='mb-4'>
              {shouldShowExpanded && (
                <div className='px-3 pb-2 text-xs font-medium text-muted-foreground transition-opacity duration-200'>
                  Other
                </div>
              )}
              <div className='grid gap-1'>
                {otherNavItems.map((item) =>
                  item.submenu && shouldShowExpanded ? (
                    <Collapsible
                      key={item.title}
                      open={expanded[item.title]}
                      onOpenChange={() => toggleExpanded(item.title)}
                    >
                      <CollapsibleTrigger asChild>
                        <div
                          className={cn(
                            'sidebar-item cursor-pointer',
                            isActive(item.href) && 'sidebar-item-active'
                          )}
                        >
                          <div className='flex items-center gap-3 w-full min-w-0'>
                            <div className='flex-shrink-0'>{item.icon}</div>
                            <span className='flex-1 truncate'>
                              {item.title}
                            </span>
                            <ChevronDown
                              className={cn(
                                'h-4 w-4 transition-transform flex-shrink-0',
                                expanded[item.title] && 'rotate-180'
                              )}
                            />
                          </div>
                        </div>
                      </CollapsibleTrigger>
                      <CollapsibleContent>
                        <div className='ml-9 mt-1 grid gap-1'>
                          {item.submenuItems?.map((subItem) => (
                            <Link
                              key={subItem.title}
                              href={subItem.href}
                              onClick={handleNavItemClick}
                              className={cn(
                                'text-sm text-muted-foreground transition-colors hover:text-foreground',
                                'py-1',
                                isActive(subItem.href) &&
                                  'font-medium text-foreground'
                              )}
                            >
                              {subItem.title}
                            </Link>
                          ))}
                        </div>
                      </CollapsibleContent>
                    </Collapsible>
                  ) : (
                    <Link
                      key={item.title}
                      href={item.href}
                      onClick={handleNavItemClick}
                      className={cn(
                        'sidebar-item group relative',
                        isActive(item.href) && 'sidebar-item-active',
                        !shouldShowExpanded && 'justify-center px-2'
                      )}
                      title={!shouldShowExpanded ? item.title : undefined}
                    >
                      <div className='flex items-center gap-3 w-full min-w-0'>
                        <div className='flex-shrink-0'>{item.icon}</div>
                        {shouldShowExpanded && (
                          <span className='transition-opacity duration-200 truncate'>
                            {item.title}
                          </span>
                        )}
                      </div>

                      {/* Tooltip for collapsed state */}
                      {!shouldShowExpanded && (
                        <div className='absolute left-full ml-2 px-2 py-1 bg-popover text-popover-foreground text-sm rounded-md shadow-md opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none whitespace-nowrap z-50'>
                          {item.title}
                        </div>
                      )}
                    </Link>
                  )
                )}
              </div>
            </div>
          </nav>
        </div>
        {/* Pro upgrade card */}
        {shouldShowExpanded && (
          <div className='mb-4 mt-auto px-4'>
            <div className='rounded-lg border bg-card/50 p-3'>
              <div className='flex items-center justify-between'>
                <p className='text-sm font-medium'>Zomma Quant Pro</p>
                <Star className='h-4 w-4 text-finance-secondary-400' />
              </div>
              <p className='mt-1 text-xs text-muted-foreground'>
                Upgrade for advanced analytics and real-time data
              </p>
              <Button
                className='mt-2 w-full bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500'
                size='sm'
              >
                Upgrade
              </Button>
            </div>
          </div>
        )}
      </aside>
    </>
  );
}
