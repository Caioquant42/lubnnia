"use client";

import { useState, useEffect } from "react";
import { Calendar, CalendarDays, TrendingUp, Banknote } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { cn } from "@/lib/utils";
import Link from "next/link";
import { 
  fetchUpcomingDividends, 
  DividendData, 
  DividendResponse
} from "@/__api__/dividendApi";

interface DividendCalendarPopoverProps {
  className?: string;
}

export default function DividendCalendarPopover({ className }: DividendCalendarPopoverProps) {
  const [dividends, setDividends] = useState<DividendData[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isOpen, setIsOpen] = useState(false);

  // Helper functions for formatting and calculations
  const formatCurrency = (value: number): string => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6
    }).format(value);
  };

  const formatDate = (dateStr: string): string => {
    const [day, month, year] = dateStr.split('/');
    const date = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    return date.toLocaleDateString('pt-BR', { 
      day: '2-digit', 
      month: 'short',
      year: 'numeric'
    });
  };

  const getDaysUntilPayment = (paymentDate: string): number => {
    const [day, month, year] = paymentDate.split('/');
    const payment = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    const today = new Date();
    const diffTime = payment.getTime() - today.getTime();
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const isUpcoming = (paymentDate: string, days: number): boolean => {
    const daysUntil = getDaysUntilPayment(paymentDate);
    return daysUntil >= 0 && daysUntil <= days;
  };

  const upcomingCount = dividends.filter(d => isUpcoming(d.pagamento, 7)).length;

  useEffect(() => {
    if (isOpen) {
      fetchDividends();
    }
  }, [isOpen]);

  const fetchDividends = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response: DividendResponse = await fetchUpcomingDividends(30, true);
      
      if (response.error) {
        setError(response.error);
        return;
      }
      
      setDividends(response.data || []);
      setSummary(response.summary);
    } catch (err) {
      console.error('Error fetching dividends:', err);
      setError('Failed to load dividend calendar');
    } finally {
      setLoading(false);
    }
  };
  const getDividendsByDate = () => {
    const grouped: Record<string, DividendData[]> = {};
    
    dividends.forEach(dividend => {
      const date = dividend.pagamento;
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(dividend);
    });

    // Sort dates chronologically
    const sortedDates = Object.keys(grouped).sort((a, b) => {
      const dateA = new Date(a.split('/').reverse().join('-'));
      const dateB = new Date(b.split('/').reverse().join('-'));
      return dateA.getTime() - dateB.getTime();
    });

    return sortedDates.map(date => ({
      date,
      dividends: grouped[date].sort((a, b) => b.valor - a.valor),
      totalValue: grouped[date].reduce((sum, d) => sum + d.valor, 0)
    }));
  };

  const getStatusBadge = (paymentDate: string) => {
    const days = getDaysUntilPayment(paymentDate);
    
    if (days < 0) {
      return <Badge variant="secondary" className="text-xs">Pago</Badge>;
    } else if (days === 0) {
      return <Badge variant="default" className="text-xs bg-green-500">Hoje</Badge>;
    } else if (days <= 3) {
      return <Badge variant="destructive" className="text-xs">Em {days}d</Badge>;
    } else if (days <= 7) {
      return <Badge variant="secondary" className="text-xs bg-yellow-500">Em {days}d</Badge>;
    } else {
      return <Badge variant="outline" className="text-xs">Em {days}d</Badge>;
    }
  };

  const dividendsByDate = getDividendsByDate();

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button variant="ghost" size="icon" className={cn("relative size-9", className)}>
          <CalendarDays className="h-5 w-5" />
          {upcomingCount > 0 && (
            <Badge className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-finance-secondary-400 p-0 text-xs text-finance-primary-800">
              {upcomingCount}
            </Badge>
          )}
          <span className="sr-only">Dividend Calendar</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-96 p-0" align="end">
        <div className="flex items-center justify-between border-b px-4 py-3">
          <div className="flex items-center gap-2">
            <Calendar className="h-4 w-4" />
            <h4 className="font-medium">Calendário de Dividendos</h4>
          </div>
          <Badge variant="secondary" className="text-xs">
            {dividends.length} próximos
          </Badge>
        </div>

        {loading ? (
          <div className="flex items-center justify-center p-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        ) : error ? (
          <div className="p-4 text-center text-sm text-muted-foreground">
            {error}
          </div>
        ) : (
          <>
            {/* Summary Cards */}
            {summary && (
              <div className="grid grid-cols-2 gap-2 p-3 border-b">
                <Card className="p-2">
                  <CardContent className="p-0">                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-4 w-4 text-finance-secondary-500" />
                      <div>
                        <div className="text-sm font-semibold">{summary.companies_count}</div>
                        <div className="text-xs text-muted-foreground">Empresas</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                <Card className="p-2">
                  <CardContent className="p-0">
                    <div className="flex items-center gap-2">
                      <Banknote className="h-4 w-4 text-finance-success-500" />
                      <div>
                        <div className="text-sm font-semibold">
                          {summary.total_value_display?.replace('R$', '').trim() || formatCurrency(summary.total_value).replace('R$', '').trim()}
                        </div>
                        <div className="text-xs text-muted-foreground">Total</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}

            {/* Dividend List */}
            <ScrollArea className="max-h-80">
              {dividendsByDate.length > 0 ? (
                <div className="p-2">
                  {dividendsByDate.slice(0, 10).map(({ date, dividends: dateDividends, totalValue }) => (
                    <div key={date} className="mb-3 last:mb-0">
                      <div className="flex items-center justify-between mb-2 px-2">
                        <div className="text-sm font-medium">{formatDate(date)}</div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs text-muted-foreground">
                            {formatCurrency(totalValue)}
                          </span>
                          {getStatusBadge(date)}
                        </div>
                      </div>
                      
                      <div className="space-y-1">
                        {dateDividends.map((dividend, idx) => (
                          <div
                            key={`${dividend.codigo}-${idx}`}
                            className="flex items-center justify-between rounded-md bg-muted/50 px-3 py-2 text-sm hover:bg-muted/70 transition-colors"
                          >                            <div className="flex items-center gap-2">
                              <span className="font-medium">{dividend.codigo}</span>
                              <Badge 
                                variant={dividend.tipo === 'DIV' ? 'default' : 'secondary'} 
                                className="text-xs"
                              >
                                {dividend.tipo}
                              </Badge>
                            </div>
                            <div className="text-right">
                              <div className="font-medium">
                                {dividend.valor_display || formatCurrency(dividend.valor)}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      {date !== dividendsByDate[dividendsByDate.length - 1].date && (
                        <Separator className="mt-3" />
                      )}
                    </div>
                  ))}
                  
                  {dividendsByDate.length > 10 && (
                    <div className="text-center text-xs text-muted-foreground mt-2">
                      +{dividendsByDate.length - 10} mais datas...
                    </div>
                  )}
                </div>
              ) : (
                <div className="p-8 text-center text-sm text-muted-foreground">
                  <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
                  <p>Nenhum dividendo nos próximos 30 dias</p>
                </div>
              )}
            </ScrollArea>            {/* Footer */}
            <div className="border-t">
              <Link href="/dividend-calendar">
                <Button 
                  variant="ghost" 
                  size="sm" 
                  className="w-full h-8 text-xs"
                  onClick={() => setIsOpen(false)}
                >
                  Ver calendário completo
                </Button>
              </Link>
            </div>
          </>
        )}
      </PopoverContent>
    </Popover>
  );
}
