'use client';

import { ArrowDown, ArrowUp, ArrowUpDown, ChevronRight } from 'lucide-react';
import { useState } from 'react';

import { PairsResponse } from '__api__/pairstrading';

import { formatNumber } from '@/lib/utils';

import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface CointegrationTableProps {
  data: PairsResponse | null;
  onPairSelect?: (asset1: string, asset2: string) => void;
}

export function CointegrationTable({
  data,
  onPairSelect,
}: CointegrationTableProps) {
  // State for sorting
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  if (
    !data ||
    !data.cointegration?.results ||
    data.cointegration.results.length === 0
  ) {
    return (
      <div className='text-center py-8'>
        <p className='text-muted-foreground'>
          Nenhum par cointegrado encontrado.
        </p>
      </div>
    );
  }

  // Function to handle sorting
  const handleSort = (column: string) => {
    if (sortColumn === column) {
      // Toggle direction if same column is clicked again
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new column and default to ascending
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  // Get sorted pairs
  const pairs = [...data.cointegration.results].sort((a, b) => {
    if (!sortColumn) return 0;

    let valueA: any;
    let valueB: any;

    // Determine which property to sort by
    switch (sortColumn) {
      case 'pair':
        valueA = `${a.asset1}/${a.asset2}`;
        valueB = `${b.asset1}/${b.asset2}`;
        break;
      case 'status':
        valueA = a.cointegrated ? 1 : 0;
        valueB = b.cointegrated ? 1 : 0;
        break;
      case 'p_value':
        valueA = a.p_value ?? Number.MAX_VALUE;
        valueB = b.p_value ?? Number.MAX_VALUE;
        break;
      default:
        return 0;
    }

    // Compare the values
    if (valueA < valueB) {
      return sortDirection === 'asc' ? -1 : 1;
    }
    if (valueA > valueB) {
      return sortDirection === 'asc' ? 1 : -1;
    }
    return 0;
  });

  // Helper function to render sort indicator
  const renderSortIndicator = (column: string) => {
    if (sortColumn !== column) {
      return <ArrowUpDown className='ml-2 h-4 w-4' />;
    }

    return sortDirection === 'asc' ? (
      <ArrowUp className='ml-2 h-4 w-4' />
    ) : (
      <ArrowDown className='ml-2 h-4 w-4' />
    );
  };

  return (
    <div className='rounded-md border'>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('pair')}
            >
              <div className='flex items-center'>
                Par de Ativos
                {renderSortIndicator('pair')}
              </div>
            </TableHead>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('status')}
            >
              <div className='flex items-center'>
                Status
                {renderSortIndicator('status')}
              </div>
            </TableHead>
            <TableHead
              className='cursor-pointer'
              onClick={() => handleSort('p_value')}
            >
              <div className='flex items-center'>
                Valor P{renderSortIndicator('p_value')}
              </div>
            </TableHead>
            <TableHead className='text-right'>Detalhes</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {pairs.map((pair, index) => (
            <TableRow key={index}>
              <TableCell className='font-medium'>
                {pair.asset1}/{pair.asset2}
              </TableCell>
              <TableCell>
                {pair.cointegrated ? (
                  <Badge variant='default'>Cointegrado</Badge>
                ) : (
                  <Badge variant='secondary'>Não Cointegrado</Badge>
                )}
              </TableCell>
              <TableCell>
                {pair.p_value !== undefined
                  ? formatNumber(pair.p_value, 4)
                  : 'N/A'}
              </TableCell>
              <TableCell className='text-right'>
                {onPairSelect &&
                  pair.asset1 &&
                  pair.asset2 &&
                  pair.cointegrated && (
                    <Button
                      onClick={() => onPairSelect(pair.asset1, pair.asset2)}
                      variant='ghost'
                      size='sm'
                    >
                      <ChevronRight className='h-4 w-4' />
                    </Button>
                  )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
