"use client";

import { ArrowDown, ArrowUp, ChevronDown, ChevronUp, Plus, Share } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { PortfolioPosition } from "@/types";
import { cn } from "@/lib/utils";

type PortfolioTableProps = {
  positions: PortfolioPosition[];
  className?: string;
};

export default function PortfolioTable({ positions, className }: PortfolioTableProps) {
  return (
    <div className={cn("finance-card", className)}>
      <div className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-medium">Portfolio Positions</h3>
        <Button size="sm" className="bg-finance-secondary-400 text-finance-primary-800 hover:bg-finance-secondary-500">
          <Plus className="mr-1 h-4 w-4" />
          Add Position
        </Button>
      </div>
      
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="market-table-header">
              <TableHead>Symbol</TableHead>
              <TableHead>Name</TableHead>
              <TableHead className="text-right">Quantity</TableHead>
              <TableHead className="text-right">Avg. Price</TableHead>
              <TableHead className="text-right">Current Price</TableHead>
              <TableHead className="text-right">Value</TableHead>
              <TableHead className="text-right">P&L</TableHead>
              <TableHead className="text-right">P&L %</TableHead>
              <TableHead className="text-right">Allocation</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {positions.map((position) => (
              <TableRow key={position.id} className="market-table-row">
                <TableCell className="font-medium">{position.symbol}</TableCell>
                <TableCell>{position.name}</TableCell>
                <TableCell className="text-right">{position.quantity.toLocaleString()}</TableCell>
                <TableCell className="text-right">${position.averagePrice.toFixed(2)}</TableCell>
                <TableCell className="text-right">${position.currentPrice.toFixed(2)}</TableCell>
                <TableCell className="text-right">${position.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</TableCell>
                <TableCell className="text-right">
                  <span className={position.pnl >= 0 ? "text-finance-success-500" : "text-finance-danger-500"}>
                    ${Math.abs(position.pnl).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </TableCell>
                <TableCell className="text-right">
                  <div className={cn(
                    "flex items-center justify-end",
                    position.pnlPercent >= 0 ? "text-finance-success-500" : "text-finance-danger-500"
                  )}>
                    {position.pnlPercent >= 0 ? (
                      <ArrowUp className="mr-1 h-3 w-3" />
                    ) : (
                      <ArrowDown className="mr-1 h-3 w-3" />
                    )}
                    {Math.abs(position.pnlPercent).toFixed(2)}%
                  </div>
                </TableCell>
                <TableCell className="text-right">{position.allocation.toFixed(2)}%</TableCell>
                <TableCell>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <ChevronDown className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>
                        <Plus className="mr-2 h-4 w-4" />
                        Buy More
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Share className="mr-2 h-4 w-4" />
                        Sell
                      </DropdownMenuItem>
                      <DropdownMenuItem>View Details</DropdownMenuItem>
                      <DropdownMenuItem>Set Alert</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}