"use client";

import { useState } from "react";
import { ArrowDown, ArrowDownUp, ArrowUp, ChevronDown, ChevronUp, SlidersHorizontal } from "lucide-react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Asset } from "@/types";
import { cn } from "@/lib/utils";

type SortDirection = "asc" | "desc";

type MarketDataTableProps = {
  data: Asset[];
  title?: string;
  className?: string;
};

export default function MarketDataTable({ data, title, className }: MarketDataTableProps) {
  const [sortBy, setSortBy] = useState<keyof Asset>("symbol");
  const [sortDirection, setSortDirection] = useState<SortDirection>("asc");
  const [searchTerm, setSearchTerm] = useState("");
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [currentPage, setCurrentPage] = useState(1);
  const [assetTypeFilter, setAssetTypeFilter] = useState<string>("all");
  
  // Handle sort
  const handleSort = (column: keyof Asset) => {
    if (sortBy === column) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortDirection("asc");
    }
  };
  
  // Filter data based on search term and asset type
  const filteredData = data.filter((item) => {
    const matchesSearch = 
      item.symbol.toLowerCase().includes(searchTerm.toLowerCase()) || 
      item.name.toLowerCase().includes(searchTerm.toLowerCase());
      
    const matchesType = assetTypeFilter === "all" || item.type === assetTypeFilter;
    
    return matchesSearch && matchesType;
  });
  
  // Sort filtered data
  const sortedData = [...filteredData].sort((a, b) => {
    const aValue = a[sortBy];
    const bValue = b[sortBy];
    
    if (typeof aValue === 'number' && typeof bValue === 'number') {
      return sortDirection === "asc" ? aValue - bValue : bValue - aValue;
    }
    
    if (aValue instanceof Date && bValue instanceof Date) {
      return sortDirection === "asc" 
        ? aValue.getTime() - bValue.getTime() 
        : bValue.getTime() - aValue.getTime();
    }
    
    // Convert to string and compare
    const aString = String(aValue).toLowerCase();
    const bString = String(bValue).toLowerCase();
    
    return sortDirection === "asc" 
      ? aString.localeCompare(bString) 
      : bString.localeCompare(aString);
  });
  
  // Pagination
  const totalPages = Math.ceil(sortedData.length / rowsPerPage);
  const startIndex = (currentPage - 1) * rowsPerPage;
  const endIndex = startIndex + rowsPerPage;
  const paginatedData = sortedData.slice(startIndex, endIndex);
  
  const renderSortIcon = (column: keyof Asset) => {
    if (sortBy !== column) {
      return <ArrowDownUp className="ml-1 h-3 w-3 text-muted-foreground" />;
    }
    return sortDirection === "asc" ? (
      <ChevronUp className="ml-1 h-3 w-3" />
    ) : (
      <ChevronDown className="ml-1 h-3 w-3" />
    );
  };
  
  // Format price with appropriate decimal places
  const formatPrice = (price: number, type: string) => {
    if (type === 'crypto') {
      // Show more decimal places for crypto
      return price.toLocaleString(undefined, {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
      });
    }
    return price.toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    });
  };
  
  // Format large numbers (volume, market cap)
  const formatLargeNumber = (num: number | undefined) => {
    if (num === undefined) return "-";
    if (num >= 1e12) return (num / 1e12).toFixed(2) + "T";
    if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
    if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
    if (num >= 1e3) return (num / 1e3).toFixed(2) + "K";
    return num.toString();
  };
  
  // Reset to first page when filters change
  const handleSearchChange = (value: string) => {
    setSearchTerm(value);
    setCurrentPage(1);
  };
  
  const handleAssetTypeChange = (value: string) => {
    setAssetTypeFilter(value);
    setCurrentPage(1);
  };
  
  return (
    <div className={cn("finance-card", className)}>
      {title && (
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-lg font-medium">{title}</h3>
        </div>
      )}
      
      {/* Filters and controls */}
      <div className="mb-3 flex flex-col gap-3 sm:flex-row">
        <div className="relative flex-1">
          <Input
            placeholder="Search symbol or name..."
            value={searchTerm}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="max-w-sm"
          />
        </div>
        
        <div className="flex items-center gap-2">
          <Select
            value={assetTypeFilter}
            onValueChange={handleAssetTypeChange}
          >
            <SelectTrigger className="w-[130px]">
              <SelectValue placeholder="Asset Type" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
              <SelectItem value="stock">Stocks</SelectItem>
              <SelectItem value="etf">ETFs</SelectItem>
              <SelectItem value="crypto">Crypto</SelectItem>
              <SelectItem value="forex">Forex</SelectItem>
            </SelectContent>
          </Select>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="icon" className="h-9 w-9">
                <SlidersHorizontal className="h-4 w-4" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuLabel>Table Settings</DropdownMenuLabel>
              <DropdownMenuSeparator />
              <DropdownMenuItem onClick={() => setRowsPerPage(5)}>
                Show 5 rows
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setRowsPerPage(10)}>
                Show 10 rows
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setRowsPerPage(20)}>
                Show 20 rows
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem>Export Data</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </div>
      
      {/* Table */}
      <div className="market-table-container">
        <Table className="market-table">
          <TableHeader>
            <TableRow className="market-table-header">
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort("symbol")}
              >
                <div className="flex items-center">
                  Symbol {renderSortIcon("symbol")}
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer"
                onClick={() => handleSort("name")}
              >
                <div className="flex items-center">
                  Name {renderSortIcon("name")}
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer text-right"
                onClick={() => handleSort("price")}
              >
                <div className="flex items-center justify-end">
                  Price {renderSortIcon("price")}
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer text-right"
                onClick={() => handleSort("changePercent")}
              >
                <div className="flex items-center justify-end">
                  Change % {renderSortIcon("changePercent")}
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer text-right hidden md:table-cell"
                onClick={() => handleSort("volume")}
              >
                <div className="flex items-center justify-end">
                  Volume {renderSortIcon("volume")}
                </div>
              </TableHead>
              <TableHead
                className="cursor-pointer text-right hidden lg:table-cell"
                onClick={() => handleSort("marketCap")}
              >
                <div className="flex items-center justify-end">
                  Market Cap {renderSortIcon("marketCap")}
                </div>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {paginatedData.length > 0 ? (
              paginatedData.map((item) => (
                <TableRow key={item.id} className="market-table-row">
                  <TableCell className="font-medium">{item.symbol}</TableCell>
                  <TableCell>{item.name}</TableCell>
                  <TableCell className="text-right">
                    ${formatPrice(item.price, item.type)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className={cn(
                      "flex items-center justify-end",
                      item.changePercent >= 0 ? "text-finance-success-500" : "text-finance-danger-500"
                    )}>
                      {item.changePercent >= 0 ? (
                        <ArrowUp className="mr-1 h-3 w-3" />
                      ) : (
                        <ArrowDown className="mr-1 h-3 w-3" />
                      )}
                      {Math.abs(item.changePercent).toFixed(2)}%
                    </div>
                  </TableCell>
                  <TableCell className="text-right hidden md:table-cell">
                    {formatLargeNumber(item.volume)}
                  </TableCell>
                  <TableCell className="text-right hidden lg:table-cell">
                    {formatLargeNumber(item.marketCap)}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center">
                  No results found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      
      {/* Pagination */}
      {totalPages > 1 && (
        <div className="mt-3 flex items-center justify-between">
          <div className="text-sm text-muted-foreground">
            Showing {startIndex + 1}-{Math.min(endIndex, sortedData.length)} of {sortedData.length} items
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage - 1)}
              disabled={currentPage === 1}
            >
              Previous
            </Button>
            <span className="text-sm">
              Page {currentPage} of {totalPages}
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage(currentPage + 1)}
              disabled={currentPage === totalPages}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}