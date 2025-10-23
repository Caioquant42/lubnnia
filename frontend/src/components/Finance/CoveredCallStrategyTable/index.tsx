'use client';

import { ArrowUpDown, EyeIcon } from 'lucide-react';
import { useState } from 'react';

import { CoveredCallOption } from '__api__/coveredcallApi';

import { Button } from '../../ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '../../ui/table';

interface CoveredCallStrategyTableProps {
  options: CoveredCallOption[];
  formatMaturityDate: (blockDate?: string, daysToMaturity?: number) => string;
  onSelectStrategy: (option: CoveredCallOption) => void;
}

export function CoveredCallStrategyTable({
  options,
  formatMaturityDate,
  onSelectStrategy,
}: CoveredCallStrategyTableProps) {
  // Filter out options with very low premiums
  const validOptions = options.filter((option) => (option.bid || 0) >= 0.01);

  const [sortConfig, setSortConfig] = useState<{
    key: keyof CoveredCallOption;
    direction: 'asc' | 'desc';
  }>({ key: 'cdi_relative_return', direction: 'desc' });

  const handleSort = (key: keyof CoveredCallOption) => {
    setSortConfig((prevConfig) => ({
      key,
      direction:
        prevConfig.key === key && prevConfig.direction === 'desc'
          ? 'asc'
          : 'desc',
    }));
  };

  const sortedOptions = [...validOptions].sort((a, b) => {
    if (a[sortConfig.key] === undefined || b[sortConfig.key] === undefined) {
      return 0;
    }

    // Handle special case for numeric values that might be strings
    const aValue = a[sortConfig.key];
    const bValue = b[sortConfig.key];

    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortConfig.direction === 'asc' ? aValue - bValue : bValue - aValue;
    }

    // Convert to strings for comparison
    const aString = String(aValue).toLowerCase();
    const bString = String(bValue).toLowerCase();

    return sortConfig.direction === 'asc'
      ? aString.localeCompare(bString)
      : bString.localeCompare(aString);
  });
  const formatPercent = (value: number | undefined) => {
    if (value === undefined || isNaN(value)) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  const handleViewStrategy = (option: CoveredCallOption) => {
    onSelectStrategy(option);
  };
  return (
    <div className='rounded-md border'>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className='w-[100px]'>
              {/* Aqui a DIV não é um elemento interativo, então o navegador e leitores de 
              tela não os tratam como botões ou links, por isso foi substituído por 
              um botão */}
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('parent_symbol')}
              >
                Símbolo
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('spot_price')}
              >
                Preço Atual
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('strike')}
              >
                Strike
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('bid')}
              >
                Prêmio
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('days_to_maturity')}
              >
                Vencimento
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('cdi_relative_return')}
              >
                Ret. Rel. CDI
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('spot_variation_to_max_return')}
              >
                Var. Spot p/ Máx
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('pm_distance_to_profit')}
              >
                Dist. PM p/ Lucro
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>
              <button
                className='flex items-center gap-1 cursor-pointer'
                onClick={() => handleSort('score')}
              >
                Pontuação
                <ArrowUpDown className='h-4 w-4' />
              </button>
            </TableHead>
            <TableHead>Ação</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {sortedOptions.map((option) => (
            <TableRow key={option.symbol}>
              <TableCell className='font-medium'>
                {option.parent_symbol}
              </TableCell>
              <TableCell>R$ {option.spot_price?.toFixed(2)}</TableCell>
              <TableCell>R$ {option.strike?.toFixed(2)}</TableCell>
              <TableCell>R$ {option.bid?.toFixed(2)}</TableCell>
              <TableCell>
                {formatMaturityDate(option.block_date, option.days_to_maturity)}
              </TableCell>
              <TableCell>{formatPercent(option.cdi_relative_return)}</TableCell>
              <TableCell>
                {formatPercent(option.spot_variation_to_max_return)}
              </TableCell>
              <TableCell>
                {formatPercent(option.pm_distance_to_profit)}
              </TableCell>
              <TableCell>{option.score?.toFixed(2)}</TableCell>{' '}
              <TableCell>
                <Button
                  variant='ghost'
                  size='icon'
                  onClick={() => handleViewStrategy(option)}
                >
                  <EyeIcon className='h-4 w-4' />
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
