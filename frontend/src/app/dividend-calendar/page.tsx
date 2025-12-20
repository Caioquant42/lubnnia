'use client';

import {
  Building2,
  Calendar,
  DollarSign,
  Download,
  Filter,
  Search,
  TrendingUp,
} from 'lucide-react';
import { useEffect, useMemo, useState } from 'react';

import {
  DividendData,
  DividendFilters,
  fetchDividendCalendar,
} from '@/api/dividendApi';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const DividendCalendarPage = () => {
  const [dividends, setDividends] = useState<DividendData[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<DividendFilters>({
    upcoming_days: 365, // Show full year by default
    sort_order: 'asc',
  });
  const [searchTerm, setSearchTerm] = useState('');

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetchDividendCalendar(filters);
      setDividends(response.data);
      setSummary(response.summary);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : 'Failed to load dividend data'
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filters]);

  // Filter dividends based on search term
  const filteredDividends = useMemo(() => {
    if (!searchTerm) return dividends;

    const term = searchTerm.toLowerCase();
    return dividends.filter(
      (dividend) =>
        dividend.codigo.toLowerCase().includes(term) ||
        dividend.tipo.toLowerCase().includes(term)
    );
  }, [dividends, searchTerm]);

  // Group dividends by status
  const groupedDividends = useMemo(() => {
    const groups = {
      today: [] as DividendData[],
      upcoming: [] as DividendData[],
      paid: [] as DividendData[],
    };

    filteredDividends.forEach((dividend) => {
      if (dividend.status === 'today') {
        groups.today.push(dividend);
      } else if (dividend.status === 'upcoming') {
        groups.upcoming.push(dividend);
      } else {
        groups.paid.push(dividend);
      }
    });

    return groups;
  }, [filteredDividends]);

  // Group dividends by date for calendar view
  const dividendsByDate = useMemo(() => {
    const dateGroups: { [key: string]: DividendData[] } = {};

    filteredDividends.forEach((dividend) => {
      const date = dividend.pagamento;
      if (!dateGroups[date]) {
        dateGroups[date] = [];
      }
      dateGroups[date].push(dividend);
    });

    return Object.entries(dateGroups).sort(([a], [b]) => {
      const dateA = a.split('/').reverse().join('-');
      const dateB = b.split('/').reverse().join('-');
      return dateA.localeCompare(dateB);
    });
  }, [filteredDividends]);

  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'today':
        return 'default';
      case 'upcoming':
        return 'secondary';
      case 'paid':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'today':
        return 'Hoje';
      case 'upcoming':
        return 'Próximo';
      case 'paid':
        return 'Pago';
      default:
        return status;
    }
  };

  const getTypeBadgeColor = (tipo: string) => {
    switch (tipo.toUpperCase()) {
      case 'JCP':
        return 'bg-blue-100 text-blue-800';
      case 'DIV':
        return 'bg-green-100 text-green-800';
      case 'JSCP':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const exportToCsv = () => {
    const headers = [
      'Código',
      'Tipo',
      'Valor',
      'Pagamento',
      'Registro',
      'Ex',
      'Status',
    ];
    const csvContent = [
      headers.join(','),
      ...filteredDividends.map((dividend) =>
        [
          dividend.codigo,
          dividend.tipo,
          dividend.valor_display,
          dividend.pagamento,
          dividend.registro,
          dividend.ex,
          getStatusLabel(dividend.status),
        ].join(',')
      ),
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute(
      'download',
      `dividendos_${new Date().toISOString().split('T')[0]}.csv`
    );
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) {
    return (
      <div className='container mx-auto p-6'>
        <div className='flex items-center justify-center h-64'>
          <div className='text-center'>
            <div className='animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto mb-4'></div>
            <p className='text-muted-foreground'>
              Carregando calendário de dividendos...
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className='container mx-auto p-6'>
        <Card>
          <CardContent className='pt-6'>
            <div className='text-center text-red-600'>
              <p className='font-semibold'>Erro ao carregar dados</p>
              <p className='text-sm'>{error}</p>
              <Button onClick={fetchData} className='mt-4'>
                Tentar novamente
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className='container mx-auto p-6 space-y-6'>
      {/* Header */}
      <div className='flex flex-col md:flex-row md:items-center md:justify-between gap-4'>
        <div>
          <h1 className='text-3xl font-bold flex items-center gap-2'>
            <Calendar className='h-8 w-8' />
            Calendário de Dividendos
          </h1>
          <p className='text-muted-foreground'>
            Acompanhe os pagamentos de dividendos e JCP das empresas
          </p>
        </div>
        <div className='flex gap-2'>
          <Button onClick={fetchData} variant='outline' size='sm'>
            Atualizar
          </Button>
          <Button onClick={exportToCsv} variant='outline' size='sm'>
            <Download className='h-4 w-4 mr-2' />
            Exportar CSV
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className='grid grid-cols-1 md:grid-cols-4 gap-4'>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center'>
                <Building2 className='h-4 w-4 text-muted-foreground' />
                <div className='ml-2'>
                  <p className='text-sm font-medium text-muted-foreground'>
                    Empresas
                  </p>
                  <p className='text-2xl font-bold'>
                    {summary.companies_count}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center'>
                <DollarSign className='h-4 w-4 text-muted-foreground' />
                <div className='ml-2'>
                  <p className='text-sm font-medium text-muted-foreground'>
                    Total
                  </p>
                  <p className='text-2xl font-bold'>
                    {summary.total_value_display}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center'>
                <Calendar className='h-4 w-4 text-muted-foreground' />
                <div className='ml-2'>
                  <p className='text-sm font-medium text-muted-foreground'>
                    Datas
                  </p>
                  <p className='text-2xl font-bold'>{summary.unique_dates}</p>
                </div>
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardContent className='pt-6'>
              <div className='flex items-center'>
                <TrendingUp className='h-4 w-4 text-muted-foreground' />
                <div className='ml-2'>
                  <p className='text-sm font-medium text-muted-foreground'>
                    Próximos
                  </p>
                  <p className='text-2xl font-bold'>
                    {summary.status_breakdown?.upcoming || 0}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Filters */}
      <Card>
        <CardHeader>
          <CardTitle className='flex items-center gap-2'>
            <Filter className='h-5 w-5' />
            Filtros
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className='grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4'>
            <div>
              <Label htmlFor='search'>Buscar</Label>
              <div className='relative'>
                <Search className='absolute left-2 top-2.5 h-4 w-4 text-muted-foreground' />
                <Input
                  id='search'
                  placeholder='Código ou tipo...'
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className='pl-8'
                />
              </div>
            </div>
            <div>
              <Label htmlFor='days'>Próximos Dias</Label>
              <Input
                id='days'
                type='number'
                value={filters.upcoming_days}
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    upcoming_days: parseInt(e.target.value) || 365,
                  }))
                }
              />
            </div>
            <div>
              <Label htmlFor='tipo'>Tipo</Label>{' '}
              <Select
                value={filters.tipo || 'all'}
                onValueChange={(value) =>
                  setFilters((prev) => ({
                    ...prev,
                    tipo:
                      value === 'all'
                        ? undefined
                        : (value as 'Dividendo' | 'JCP'),
                  }))
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder='Todos' />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='all'>Todos</SelectItem>
                  <SelectItem value='JCP'>JCP</SelectItem>
                  <SelectItem value='Dividendo'>Dividendo</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label htmlFor='minValue'>Valor Mín.</Label>
              <Input
                id='minValue'
                type='number'
                step='0.000001'
                placeholder='0.000000'
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    min_value: parseFloat(e.target.value) || undefined,
                  }))
                }
              />
            </div>
            <div>
              <Label htmlFor='maxValue'>Valor Máx.</Label>
              <Input
                id='maxValue'
                type='number'
                step='0.000001'
                placeholder='1.000000'
                onChange={(e) =>
                  setFilters((prev) => ({
                    ...prev,
                    max_value: parseFloat(e.target.value) || undefined,
                  }))
                }
              />
            </div>
            <div>
              <Label htmlFor='sort'>Ordenação</Label>
              <Select
                value={filters.sort_order}
                onValueChange={(value: 'asc' | 'desc') =>
                  setFilters((prev) => ({ ...prev, sort_order: value }))
                }
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value='asc'>Crescente</SelectItem>
                  <SelectItem value='desc'>Decrescente</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Content Tabs */}
      <Tabs defaultValue='timeline' className='space-y-4'>
        <TabsList>
          <TabsTrigger value='timeline'>Timeline</TabsTrigger>
          <TabsTrigger value='status'>Por Status</TabsTrigger>
          <TabsTrigger value='table'>Tabela</TabsTrigger>
        </TabsList>

        {/* Timeline View */}
        <TabsContent value='timeline' className='space-y-4'>
          {dividendsByDate.map(([date, dateDividends]) => (
            <Card key={date}>
              <CardHeader className='pb-3'>
                <CardTitle className='text-lg'>{date}</CardTitle>
                <CardDescription>
                  {dateDividends.length} pagamento
                  {dateDividends.length !== 1 ? 's' : ''}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3'>
                  {dateDividends.map((dividend, index) => (
                    <div
                      key={index}
                      className='flex items-center justify-between p-3 border rounded-lg'
                    >
                      <div className='flex items-center gap-3'>
                        <div>
                          <p className='font-semibold'>{dividend.codigo}</p>
                          <div className='flex gap-2 mt-1'>
                            <Badge
                              variant='outline'
                              className={getTypeBadgeColor(dividend.tipo)}
                            >
                              {dividend.tipo}
                            </Badge>
                            <Badge
                              variant={getStatusBadgeVariant(dividend.status)}
                            >
                              {getStatusLabel(dividend.status)}
                            </Badge>
                          </div>
                        </div>
                      </div>
                      <div className='text-right'>
                        <p className='font-bold text-green-600'>
                          {dividend.valor_display}
                        </p>
                        <p className='text-xs text-muted-foreground'>
                          {dividend.days_until_payment >= 0
                            ? `${dividend.days_until_payment} dias`
                            : `${Math.abs(dividend.days_until_payment)} dias atrás`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </TabsContent>

        {/* Status View */}
        <TabsContent value='status' className='space-y-4'>
          {/* Today */}
          {groupedDividends.today.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className='text-blue-600'>
                  Hoje ({groupedDividends.today.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3'>
                  {groupedDividends.today.map((dividend, index) => (
                    <DividendCard key={index} dividend={dividend} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Upcoming */}
          {groupedDividends.upcoming.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className='text-green-600'>
                  Próximos ({groupedDividends.upcoming.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3'>
                  {groupedDividends.upcoming.map((dividend, index) => (
                    <DividendCard key={index} dividend={dividend} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Paid */}
          {groupedDividends.paid.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className='text-gray-600'>
                  Pagos ({groupedDividends.paid.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3'>
                  {groupedDividends.paid.map((dividend, index) => (
                    <DividendCard key={index} dividend={dividend} />
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Table View */}
        <TabsContent value='table'>
          <Card>
            <CardContent className='pt-6'>
              <div className='overflow-x-auto'>
                <table className='w-full border-collapse'>
                  <thead>
                    <tr className='border-b'>
                      <th className='text-left p-2'>Código</th>
                      <th className='text-left p-2'>Tipo</th>
                      <th className='text-right p-2'>Valor</th>
                      <th className='text-left p-2'>Pagamento</th>
                      <th className='text-left p-2'>Registro</th>
                      <th className='text-left p-2'>Ex</th>
                      <th className='text-left p-2'>Status</th>
                      <th className='text-right p-2'>Dias</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDividends.map((dividend, index) => (
                      <tr key={index} className='border-b hover:bg-muted/50'>
                        <td className='p-2 font-semibold'>{dividend.codigo}</td>
                        <td className='p-2'>
                          <Badge
                            variant='outline'
                            className={getTypeBadgeColor(dividend.tipo)}
                          >
                            {dividend.tipo}
                          </Badge>
                        </td>
                        <td className='p-2 text-right font-mono text-green-600'>
                          {dividend.valor_display}
                        </td>
                        <td className='p-2'>{dividend.pagamento}</td>
                        <td className='p-2'>{dividend.registro}</td>
                        <td className='p-2'>{dividend.ex}</td>
                        <td className='p-2'>
                          <Badge
                            variant={getStatusBadgeVariant(dividend.status)}
                          >
                            {getStatusLabel(dividend.status)}
                          </Badge>
                        </td>
                        <td className='p-2 text-right'>
                          {dividend.days_until_payment >= 0
                            ? `+${dividend.days_until_payment}`
                            : dividend.days_until_payment}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

// Component for individual dividend cards
const DividendCard = ({ dividend }: { dividend: DividendData }) => {
  const getStatusBadgeVariant = (status: string) => {
    switch (status) {
      case 'today':
        return 'default';
      case 'upcoming':
        return 'secondary';
      case 'paid':
        return 'outline';
      default:
        return 'outline';
    }
  };

  const getStatusLabel = (status: string) => {
    switch (status) {
      case 'today':
        return 'Hoje';
      case 'upcoming':
        return 'Próximo';
      case 'paid':
        return 'Pago';
      default:
        return status;
    }
  };

  const getTypeBadgeColor = (tipo: string) => {
    switch (tipo.toUpperCase()) {
      case 'JCP':
        return 'bg-blue-100 text-blue-800';
      case 'DIV':
        return 'bg-green-100 text-green-800';
      case 'JSCP':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className='border rounded-lg p-4 space-y-3'>
      <div className='flex items-center justify-between'>
        <h4 className='font-semibold text-lg'>{dividend.codigo}</h4>
        <Badge variant={getStatusBadgeVariant(dividend.status)}>
          {getStatusLabel(dividend.status)}
        </Badge>
      </div>

      <div className='space-y-2'>
        <div className='flex justify-between items-center'>
          <Badge variant='outline' className={getTypeBadgeColor(dividend.tipo)}>
            {dividend.tipo}
          </Badge>
          <span className='font-bold text-green-600'>
            {dividend.valor_display}
          </span>
        </div>

        <div className='text-sm text-muted-foreground space-y-1'>
          <div className='flex justify-between'>
            <span>Pagamento:</span>
            <span>{dividend.pagamento}</span>
          </div>
          <div className='flex justify-between'>
            <span>Registro:</span>
            <span>{dividend.registro}</span>
          </div>
          <div className='flex justify-between'>
            <span>Ex:</span>
            <span>{dividend.ex}</span>
          </div>
          <div className='flex justify-between'>
            <span>Dias:</span>
            <span>
              {dividend.days_until_payment >= 0
                ? `${dividend.days_until_payment} dias`
                : `${Math.abs(dividend.days_until_payment)} dias atrás`}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DividendCalendarPage;
