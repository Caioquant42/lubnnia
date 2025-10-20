"use client";

import { useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { PairsResponse } from "@/__api__/pairstrading";
import { ChevronRight, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";
import { formatNumber } from "@/lib/utils";

interface RecentSignalsTableProps {
  data: PairsResponse | null;
  onPairSelect?: (asset1: string, asset2: string) => void;
}

export default function RecentSignalsTable({ data, onPairSelect }: RecentSignalsTableProps) {
  // State for sorting
  const [sortColumn, setSortColumn] = useState<string | null>(null);
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');
  
  if (!data || !data.signals?.signals || data.signals.signals.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Nenhum sinal de trading encontrado.</p>
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

  // Get sorted signals
  const signals = [...data.signals.signals].sort((a, b) => {
    if (!sortColumn) return 0;

    let valueA: any;
    let valueB: any;

    // Determine which property to sort by
    switch (sortColumn) {
      case 'pair':
        valueA = `${a.asset1}/${a.asset2}`;
        valueB = `${b.asset1}/${b.asset2}`;
        break;
      case 'signal_type':
        valueA = a.signal_type;
        valueB = b.signal_type;
        break;
      case 'zscore':
        valueA = a.current_zscore ?? Number.MAX_VALUE;
        valueB = b.current_zscore ?? Number.MAX_VALUE;
        break;
      case 'beta':
        valueA = a.beta ?? Number.MAX_VALUE;
        valueB = b.beta ?? Number.MAX_VALUE;
        break;
      case 'half_life':
        valueA = a.half_life ?? Number.MAX_VALUE;
        valueB = b.half_life ?? Number.MAX_VALUE;
        break;
      case 'date':
        valueA = new Date(a.signal_date).getTime();
        valueB = new Date(b.signal_date).getTime();
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
      return <ArrowUpDown className="ml-2 h-4 w-4" />;
    }
    
    return sortDirection === 'asc' ? <ArrowUp className="ml-2 h-4 w-4" /> : <ArrowDown className="ml-2 h-4 w-4" />;
  };

  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead className="cursor-pointer" onClick={() => handleSort('pair')}>
              <div className="flex items-center">
                Par de Ativos
                {renderSortIndicator('pair')}
              </div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort('signal_type')}>
              <div className="flex items-center">
                Sinal
                {renderSortIndicator('signal_type')}
              </div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort('zscore')}>
              <div className="flex items-center">
                Z-Score
                {renderSortIndicator('zscore')}
              </div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort('beta')}>
              <div className="flex items-center">
                Beta (Razão de Hedge)
                {renderSortIndicator('beta')}
              </div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort('half_life')}>
              <div className="flex items-center">
                Meia-Vida (Dias)
                {renderSortIndicator('half_life')}
              </div>
            </TableHead>
            <TableHead className="cursor-pointer" onClick={() => handleSort('date')}>
              <div className="flex items-center">
                Data do Sinal
                {renderSortIndicator('date')}
              </div>
            </TableHead>
            <TableHead className="text-right">Detalhes</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {signals.map((signal, index) => (
            <TableRow key={index}>
              <TableCell className="font-medium">
                {signal.asset1}/{signal.asset2}
              </TableCell>
              <TableCell>
                <Badge variant={signal.signal_type === 'buy' ? 'default' : 'destructive'}>
                  {signal.signal_type === 'buy' ? 'COMPRA' : 'VENDA'}
                </Badge>
              </TableCell>
              <TableCell>
                {formatNumber(signal.current_zscore, 2)}
              </TableCell>
              <TableCell>
                {signal.beta !== undefined ? formatNumber(signal.beta, 3) : 'N/A'}
              </TableCell>
              <TableCell>
                {signal.half_life !== undefined && signal.half_life !== null 
                  ? formatNumber(signal.half_life, 1) 
                  : 'N/A'}
              </TableCell>
              <TableCell>
                {new Date(signal.signal_date).toLocaleDateString('pt-BR')}
              </TableCell>
              <TableCell className="text-right">
                {onPairSelect && (
                  <Button 
                    onClick={() => onPairSelect(signal.asset1, signal.asset2)}
                    variant="ghost"
                    size="sm"
                  >
                    <ChevronRight className="h-4 w-4" />
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