import React, { useState } from "react";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { StockVolatilityData } from "@/__api__/volatilityApi";
import { ArrowUpDown, Search } from "lucide-react";

type VolatilityDataTableProps = {
  data: StockVolatilityData[];
  onStockSelect: (symbol: string) => void;
};

export default function VolatilityDataTable({
  data,
  onStockSelect,
}: VolatilityDataTableProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [sortField, setSortField] = useState<string>("symbol");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");
  const [sectorFilter, setSectorFilter] = useState<string>("ALL_SECTORS");

  // Get unique sectors that are not null, undefined, or empty strings
  const sectors = Array.from(
    new Set(
      data
        .map((stock) => stock.sector)
        .filter((sector): sector is string => !!sector && sector.trim() !== "")
    )
  ).sort();

  // Filter data based on search term and sector
  const filteredData = data.filter((stock) => {
    const matchesSearch =
      stock.symbol.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (stock.name && stock.name.toLowerCase().includes(searchTerm.toLowerCase()));
    
    const matchesSector = 
      sectorFilter === "ALL_SECTORS" || 
      (stock.sector && stock.sector === sectorFilter);
    
    return matchesSearch && matchesSector;
  });

  // Sort data
  const sortedData = [...filteredData].sort((a, b) => {
    const fieldA = a[sortField as keyof StockVolatilityData];
    const fieldB = b[sortField as keyof StockVolatilityData];

    if (fieldA === undefined || fieldB === undefined) return 0;

    if (typeof fieldA === "string" && typeof fieldB === "string") {
      return sortDirection === "asc"
        ? fieldA.localeCompare(fieldB)
        : fieldB.localeCompare(fieldA);
    } else {
      return sortDirection === "asc"
        ? Number(fieldA) - Number(fieldB)
        : Number(fieldB) - Number(fieldA);
    }
  });

  // Handle sort
  const handleSort = (field: string) => {
    if (field === sortField) {
      setSortDirection(sortDirection === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortDirection("asc");
    }
  };

  const formatPercentile = (value: number | undefined) => {
    if (value === undefined || isNaN(value)) return "-";
    return `${value.toFixed(1)}%`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between gap-4">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Buscar..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-8"
          />
        </div>
        <Select
          value={sectorFilter}
          onValueChange={(value) => setSectorFilter(value)}
        >
          <SelectTrigger className="w-full sm:w-72">
            <SelectValue placeholder="Filtrar por setor" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="ALL_SECTORS">Todos os Setores</SelectItem>
            {sectors.map((sector) => (
              <SelectItem key={sector} value={sector}>
                {sector}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Button
                  variant="ghost"
                  onClick={() => handleSort("symbol")}
                  className="flex items-center gap-1 font-medium"
                >
                  Símbolo
                  <ArrowUpDown size={16} />
                </Button>
              </TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  onClick={() => handleSort("name")}
                  className="flex items-center gap-1 font-medium"
                >
                  Nome
                  <ArrowUpDown size={16} />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  onClick={() => handleSort("iv_ewma_ratio")}
                  className="flex items-center gap-1 font-medium justify-end w-full"
                >
                  IV/EWMA
                  <ArrowUpDown size={16} />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  onClick={() => handleSort("iv_current")}
                  className="flex items-center gap-1 font-medium justify-end w-full"
                >
                  VI
                  <ArrowUpDown size={16} />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  onClick={() => handleSort("ewma_current")}
                  className="flex items-center gap-1 font-medium justify-end w-full"
                >
                  EWMA
                  <ArrowUpDown size={16} />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  onClick={() => handleSort("iv_1y_percentile")}
                  className="flex items-center gap-1 font-medium justify-end w-full"
                >
                  VI %ile
                  <ArrowUpDown size={16} />
                </Button>
              </TableHead>
              <TableHead className="text-right">
                <Button
                  variant="ghost"
                  onClick={() => handleSort("beta_ibov")}
                  className="flex items-center gap-1 font-medium justify-end w/full"
                >
                  Beta
                  <ArrowUpDown size={16} />
                </Button>
              </TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedData.length > 0 ? (
              sortedData.map((stock) => (
                <TableRow
                  key={stock.symbol}
                  className="cursor-pointer hover:bg-muted/50"
                  onClick={() => onStockSelect(stock.symbol)}
                >
                  <TableCell className="font-medium">{stock.symbol}</TableCell>
                  <TableCell>{stock.name}</TableCell>
                  <TableCell className="text-right font-medium">
                    {stock.iv_ewma_ratio !== undefined
                      ? stock.iv_ewma_ratio.toFixed(2)
                      : "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    {stock.iv_current !== undefined
                      ? stock.iv_current.toFixed(1)
                      : "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    {stock.ewma_current !== undefined
                      ? stock.ewma_current.toFixed(1)
                      : "-"}
                  </TableCell>
                  <TableCell className="text-right">
                    {formatPercentile(stock.iv_1y_percentile)}
                  </TableCell>
                  <TableCell className="text-right">
                    {stock.beta_ibov !== undefined
                      ? stock.beta_ibov.toFixed(2)
                      : "-"}
                  </TableCell>
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center">
                  No results found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
      <div className="text-xs text-muted-foreground">
        {filteredData.length} stocks found
      </div>
    </div>
  );
}