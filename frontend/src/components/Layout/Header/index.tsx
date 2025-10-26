'use client';

import { Bell, LogOut, Moon, Search, Sun, User } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';

import {
  notificationsService,
  RealTimeNotification,
} from '__api__/notificationsService';

import { cn } from '@/lib/utils';

import { DividendCalendarPopover } from '@/components/Header/DividendCalendarPopover';

import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Input } from '@/components/ui/input';
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover';

import { useAuth } from '@/hooks/useAuth';

import { createClientBrowser } from '@/lib/supabaseClient';

export function Header() {
  const { theme, setTheme } = useTheme();
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const { user, logout: handleLogout } = useAuth();
  const router = useRouter();

  const [notifications, setNotifications] = useState<RealTimeNotification[]>(
    []
  );
  const [loading, setLoading] = useState(false);

  const unreadNotifications = notifications.filter((n) => !n.read).length;

  const supabase = createClientBrowser();

  // Fetch real-time notifications
  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const realNotifications =
        await notificationsService.fetchRealTimeNotifications();
      setNotifications(realNotifications);
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  // Mark all notifications as read
  const markAllAsRead = () => {
    notificationsService.markAllAsRead();
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
  };

  // Mark single notification as read
  const markAsRead = (notificationId: string) => {
    notificationsService.markAsRead(notificationId);
    setNotifications((prev) =>
      prev.map((n) => (n.id === notificationId ? { ...n, read: true } : n))
    );
  };

  // Fetch notifications on component mount and set up refresh interval
  useEffect(() => {
    fetchNotifications();

    // Refresh notifications every 5 minutes
    const interval = setInterval(fetchNotifications, 5 * 60 * 1000);

    return () => clearInterval(interval);
  }, []);

  // Get notification type color
  const getNotificationTypeColor = (type: string) => {
    switch (type) {
      case 'recommendation':
        return 'bg-green-500';
      case 'variation':
        return 'bg-blue-500';
      case 'volatility':
        return 'bg-orange-500';
      case 'info':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  // Get notification severity color
  const getNotificationSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-l-4 border-l-red-500';
      case 'medium':
        return 'border-l-4 border-l-yellow-500';
      case 'low':
        return 'border-l-4 border-l-green-500';
      default:
        return '';
    }
  };

  return (
    <header className='sticky top-0 z-40 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60'>
      <div className='flex h-14 items-center px-4 sm:px-6'>
        {/* Logo for mobile (only shown on mobile when sidebar is hidden) */}
        <div className='md:hidden flex flex-1'>
          <div className='flex items-center'>
            <span className='text-lg font-bold'>QuantTrade</span>
          </div>
        </div>

        {/* Search bar */}
        <div
          className={cn(
            'hidden md:flex flex-1 items-center',
            isSearchOpen && 'flex'
          )}
        >
          <div className='w-full max-w-sm'>
            <div className='relative'>
              <Search className='absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground' />
              <Input
                type='search'
                placeholder='Search markets, symbols...'
                className='w-full appearance-none bg-background pl-8 md:w-[300px] lg:w-[400px]'
              />
            </div>
          </div>
        </div>

        {/* Right side actions */}
        <div className='flex items-center space-x-1'>
          {/* Mobile search button */}
          <Button
            variant='ghost'
            size='icon'
            className='md:hidden'
            onClick={() => setIsSearchOpen(!isSearchOpen)}
          >
            <Search className='h-5 w-5' />
            <span className='sr-only'>Search</span>
          </Button>

          {/* Theme toggle */}
          <Button
            variant='ghost'
            size='icon'
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className='size-9'
          >
            <Sun className='h-5 w-5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0' />
            <Moon className='absolute h-5 w-5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100' />
            <span className='sr-only'>Toggle theme</span>
          </Button>

          {/* Dividend Calendar */}
          <DividendCalendarPopover />

          {/* Notifications */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant='ghost' size='icon' className='relative size-9'>
                <Bell className='h-5 w-5' />
                {unreadNotifications > 0 && (
                  <Badge className='absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-finance-secondary-400 p-0 text-xs text-finance-primary-800'>
                    {unreadNotifications}
                  </Badge>
                )}
                <span className='sr-only'>Notifications</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className='w-80 p-0' align='end'>
              <div className='flex items-center justify-between border-b px-4 py-3'>
                <h4 className='font-medium'>Notificações</h4>
                <Button
                  variant='ghost'
                  size='sm'
                  className='h-auto text-xs'
                  onClick={markAllAsRead}
                  disabled={unreadNotifications === 0}
                >
                  Marcar todas como lidas
                </Button>
              </div>
              <div className='max-h-80 overflow-y-auto'>
                {loading ? (
                  <div className='flex items-center justify-center py-8 text-muted-foreground'>
                    <div className='text-center'>
                      <div className='animate-spin rounded-full h-6 w-6 border-b-2 border-primary mx-auto mb-2'></div>
                      <p className='text-sm'>Carregando notificações...</p>
                    </div>
                  </div>
                ) : notifications.length > 0 ? (
                  notifications.map((notification) => (
                    <button
                      key={notification.id}
                      className={cn(
                        'flex items-start gap-3 border-b px-4 py-3 last:border-0 cursor-pointer hover:bg-muted/50 transition-colors',
                        !notification.read && 'bg-muted/50',
                        getNotificationSeverityColor(notification.severity)
                      )}
                      onClick={() => markAsRead(notification.id)}
                    >
                      <div
                        className={cn(
                          'mt-1 flex h-2 w-2 rounded-full',
                          getNotificationTypeColor(notification.type)
                        )}
                      />
                      <div className='flex-1'>
                        <div className='flex items-center justify-between gap-2'>
                          <p className='font-medium'>{notification.title}</p>
                          <p className='whitespace-nowrap text-xs text-muted-foreground'>
                            {new Date(
                              notification.timestamp
                            ).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit',
                            })}
                          </p>
                        </div>
                        <p className='text-sm text-muted-foreground'>
                          {notification.message}
                        </p>
                        {notification.symbol && (
                          <div className='flex items-center gap-2 mt-2'>
                            <Badge variant='outline' className='text-xs'>
                              {notification.symbol}
                            </Badge>
                            {notification.change !== undefined && (
                              <Badge
                                variant={
                                  notification.change >= 0
                                    ? 'default'
                                    : 'destructive'
                                }
                                className='text-xs'
                              >
                                {notification.change >= 0 ? '+' : ''}
                                {notification.change.toFixed(2)}
                                {notification.type === 'variation'
                                  ? '%'
                                  : notification.type === 'volatility'
                                    ? ' IV'
                                    : ''}
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>
                    </button>
                  ))
                ) : (
                  <div className='flex items-center justify-center py-8 text-muted-foreground'>
                    <div className='text-center'>
                      <Bell className='h-8 w-8 mx-auto mb-2 opacity-50' />
                      <p className='text-sm'>Nenhuma notificação disponível</p>
                    </div>
                  </div>
                )}
              </div>
              <div className='flex items-center justify-center border-t py-2'>
                <Button variant='ghost' size='sm' className='w-full'>
                  Ver todas as notificações
                </Button>
              </div>
            </PopoverContent>
          </Popover>

          {/* User menu */}
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant='ghost' size='icon' className='relative h-9 w-9'>
                <Avatar className='h-8 w-8'>
                  <AvatarImage
                    src={user?.user_metadata?.avatar_url || ''}
                    alt={user?.email || 'User'}
                  />
                  <AvatarFallback className='bg-finance-primary-800 text-white'>
                    {user?.email ? user.email[0].toUpperCase() : 'U'}
                  </AvatarFallback>
                </Avatar>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align='end' className='w-56'>
              <div className='flex items-center justify-start gap-2 p-2'>
                <div className='flex flex-col space-y-0.5'>
                  <p className='text-sm font-medium'>
                    {user?.user_metadata?.full_name ||
                      user?.email?.split('@')[0] ||
                      'Usuário'}
                  </p>
                  <p className='text-xs text-muted-foreground'>
                    {user?.email || ''}
                  </p>
                </div>
              </div>
              <DropdownMenuItem onClick={() => router.push('/perfil')}>
                <User className='mr-2 h-4 w-4' />
                <span>Perfil</span>
              </DropdownMenuItem>
              <DropdownMenuItem
                className='text-finance-danger-500 cursor-pointer'
                onClick={handleLogout}
              >
                <LogOut className='mr-2 h-4 w-4' />
                <span>Sair</span>
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
    </header>
  );
}
