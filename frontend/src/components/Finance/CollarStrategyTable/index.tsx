'use client';

import { ChevronDown, Eye, Filter } from 'lucide-react';
import * as React from 'react';

import { CollarStrategy } from '__api__/collarApi';

import { Badge } from '../../ui/badge';
import { Button } from '../../ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '../../ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../ui/table';

interface CollarStrategyTableProps {
  data: CollarStrategy[];
  onSelectStrategy: (strategy: CollarStrategy) => void;
}

export function CollarStrategyTable({
  data,
  onSelectStrategy,
}: CollarStrategyTableProps) {
  const [sortColumn, setSortColumn] =
    React.useState<string>('gain_to_risk_ratio');
  const [sortDirection, setSortDirection] = React.useState<'asc' | 'desc'>(
    'desc'
  );

  // Filter out strategies with low premiums
  const validStrategies = data.filter((strategy) => {
    const callPremium = strategy.call.close || 0;
    const putPremium = strategy.put.close || 0;
    return callPremium >= 0.01 && putPremium >= 0.01;
  });

  // Format date from ISO string
  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString();
  };

  // Format percent
  const formatPercent = (value: number) => {
    return `${(value * 100).toFixed(2)}%`;
  };

  // Handle sort click
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('desc'); // Default to descending for new column
    }
  };

  // Sort data based on current sort settings
  const sortedData = React.useMemo(() => {
    return [...validStrategies].sort((a, b) => {
      let valueA: any;
      let valueB: any;

      if (sortColumn === 'parent_symbol') {
        valueA = a.strategy.parent_symbol;
        valueB = b.strategy.parent_symbol;
      } else if (sortColumn === 'days_to_maturity') {
        valueA = a.strategy.days_to_maturity;
        valueB = b.strategy.days_to_maturity;
      } else if (sortColumn === 'gain_to_risk_ratio') {
        valueA = a.strategy.gain_to_risk_ratio || 0;
        valueB = b.strategy.gain_to_risk_ratio || 0;
      } else if (sortColumn === 'cdi_relative_return') {
        valueA = a.strategy.cdi_relative_return || 0;
        valueB = b.strategy.cdi_relative_return || 0;
      } else if (sortColumn === 'combined_score') {
        valueA = a.strategy.combined_score || 0;
        valueB = b.strategy.combined_score || 0;
      } else if (sortColumn === 'call_strike') {
        valueA = a.strategy.call_strike;
        valueB = b.strategy.call_strike;
      } else if (sortColumn === 'put_strike') {
        valueA = a.strategy.put_strike;
        valueB = b.strategy.put_strike;
      } else {
        // Default sort by gain/risk ratio
        valueA = a.strategy.gain_to_risk_ratio || 0;
        valueB = b.strategy.gain_to_risk_ratio || 0;
      }

      if (valueA === valueB) return 0;

      const compareResult = valueA < valueB ? -1 : 1;
      return sortDirection === 'asc' ? compareResult : -compareResult;
    });
  }, [validStrategies, sortColumn, sortDirection]);

  // Render sort indicator
  const renderSortIndicator = (column: string) => {
    if (sortColumn !== column) return null;
    return <span className='ml-1'>{sortDirection === 'asc' ? '↑' : '↓'}</span>;
  };

  return (
    <div className='rounded-md border'>
      <div className='flex items-center p-4 justify-between'>
        <div>
          <h3 className='text-lg font-medium'>Estratégias de Collar</h3>
          <p className='text-sm text-muted-foreground'>
            {validStrategies.length} estratégias válidas de {data.length} total
          </p>
        </div>
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button
              variant='outline'
              size='sm'
              className='flex items-center gap-1'
            >
              <Filter className='h-4 w-4' />
              <span>Filtrar</span>
              <ChevronDown className='h-4 w-4' />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align='end'>
            <DropdownMenuItem
              onClick={() => setSortColumn('gain_to_risk_ratio')}
            >
              Ordenar por Relação Ganho/Risco
            </DropdownMenuItem>
            <DropdownMenuItem
              onClick={() => setSortColumn('cdi_relative_return')}
            >
              Ordenar por Retorno CDI
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortColumn('combined_score')}>
              Ordenar por Pontuação Combinada
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortColumn('days_to_maturity')}>
              Ordenar por Dias para Vencimento
            </DropdownMenuItem>
            <DropdownMenuItem onClick={() => setSortColumn('parent_symbol')}>
              Ordenar por Símbolo
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('parent_symbol')}
            >
              Ação{renderSortIndicator('parent_symbol')}
            </TableHead>
            <TableHead>
              {/* Aqui a DIV não é um elemento interativo, então o navegador e leitores 
              de tela não os tratam como botões ou links, por isso foi substituído por 
              um botão */}
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('put_strike')}
              >
                Strike Put
                {renderSortIndicator('put_strike')}
              </button>
            </TableHead>
            <TableHead>
              {/* Aqui a DIV não é um elemento interativo, então o navegador e leitores 
              de tela não os tratam como botões ou links, por isso foi substituído por 
              um botão */}
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('call_premium')}
              >
                Prêmio Call
                {renderSortIndicator('call_premium')}
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('put_premium')}
              >
                Prêmio Put
                {renderSortIndicator('put_premium')}
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('days_to_maturity')}
              >
                Vencimento
                {renderSortIndicator('days_to_maturity')}
              </button>
            </TableHead>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('call_strike')}
            >
              Strike Call{renderSortIndicator('call_strike')}
            </TableHead>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('gain_to_risk_ratio')}
            >
              Ganho/Risco{renderSortIndicator('gain_to_risk_ratio')}
            </TableHead>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('cdi_relative_return')}
            >
              Retorno CDI{renderSortIndicator('cdi_relative_return')}
            </TableHead>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('combined_score')}
            >
              Pontuação{renderSortIndicator('combined_score')}
            </TableHead>
            <TableHead>Proteção</TableHead>
            <TableHead>Ação</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedData.map((strategy, index) => (
            <TableRow key={index}>
              <TableCell className='font-medium'>
                {strategy.strategy.parent_symbol}
              </TableCell>
              <TableCell>
                <div className='flex flex-col'>
                  <span>R$ {strategy.strategy.put_strike.toFixed(2)}</span>
                  <span className='text-xs text-muted-foreground'>
                    {strategy.strategy.put_symbol}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className='flex flex-col'>
                  <span>R$ {(strategy.call.close || 0).toFixed(2)}</span>
                  <span className='text-xs text-muted-foreground'>
                    {strategy.strategy.call_symbol}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className='flex flex-col'>
                  <span>R$ {(strategy.put.close || 0).toFixed(2)}</span>
                  <span className='text-xs text-muted-foreground'>
                    {strategy.strategy.put_symbol}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className='flex flex-col'>
                  <span>{strategy.strategy.days_to_maturity} dias</span>
                  <span className='text-xs text-muted-foreground'>
                    {formatDate(strategy.call.due_date)}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <div className='flex flex-col'>
                  <span>R$ {strategy.strategy.call_strike.toFixed(2)}</span>
                  <span className='text-xs text-muted-foreground'>
                    {strategy.strategy.call_symbol}
                  </span>
                </div>
              </TableCell>
              <TableCell>
                <span className='font-medium'>
                  {strategy.strategy.gain_to_risk_ratio?.toFixed(2) || 'N/A'}
                </span>
              </TableCell>
              <TableCell>
                <span className='font-medium'>
                  {strategy.strategy.cdi_relative_return
                    ? formatPercent(strategy.strategy.cdi_relative_return)
                    : 'N/A'}
                </span>
              </TableCell>
              <TableCell>
                <span className='font-medium'>
                  {strategy.strategy.combined_score?.toFixed(2) || 'N/A'}
                </span>
              </TableCell>
              <TableCell>
                <div className='flex gap-1 flex-wrap'>
                  {strategy.strategy.intrinsic_protection && (
                    <Badge className='bg-finance-success-500'>Intrínseca</Badge>
                  )}
                  {strategy.strategy.zero_risk && <Badge>Risco Zero</Badge>}
                </div>
              </TableCell>
              <TableCell>
                <Button
                  size='sm'
                  variant='ghost'
                  onClick={() => {
                    if (typeof onSelectStrategy === 'function') {
                      onSelectStrategy(strategy);
                    } else {
                      console.warn('onSelectStrategy is not a function');
                    }
                  }}
                  className='flex items-center gap-1'
                >
                  <Eye className='h-4 w-4' />
                  <span className='sr-only md:not-sr-only md:inline-flex'>
                    Ver
                  </span>
                </Button>
              </TableCell>
            </TableRow>
          ))}
          {sortedData.length === 0 && (
            <TableRow>
              <TableCell colSpan={9} className='h-24 text-center'>
                <div className='text-center py-8'>
                  <p className='text-muted-foreground'>
                    Nenhuma estratégia de collar encontrada.
                  </p>
                </div>
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>
    </div>
  );
}
