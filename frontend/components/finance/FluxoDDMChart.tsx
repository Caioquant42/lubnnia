"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  TrendingUp, 
  TrendingDown, 
  Minus, 
  ArrowUpIcon, 
  ArrowDownIcon, 
  Users, 
  Building, 
  Banknote,
  Globe,
  RefreshCw
} from "lucide-react";
import { 
  fetchFluxoData, 
  fetchFluxoByInvestorType,
  FluxoDataPoint,
  FluxoResponse
} from "@/__api__/fluxoApi";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';
import {
  Tooltip as UITooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";

interface FluxoSummary {
  positiveFlow: number;
  negativeFlow: number;
  lastUpdate: string;
}

const FluxoDDMChart: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [fluxoData, setFluxoData] = useState<FluxoDataPoint[]>([]);
  const [summary, setSummary] = useState<FluxoSummary | null>(null);
  const [selectedInvestorType, setSelectedInvestorType] = useState<string>("all");
  const [timeRange, setTimeRange] = useState<string>("20");

  const investorTypes = [
    { value: "all", label: "Todos os Investidores", icon: Users },
    { value: "Estrangeiro", label: "Estrangeiro", icon: Globe },
    { value: "Institucional", label: "Institucional", icon: Building },
    { value: "PF", label: "Pessoa Física", icon: Users },
    { value: "IF", label: "Inst. Financeira", icon: Banknote },
    { value: "Outros", label: "Outros", icon: Minus }
  ];

  const getInvestorIcon = (type: string) => {
    const investor = investorTypes.find(inv => inv.value === type);
    return investor ? investor.icon : Users;
  };

  const getFlowColor = (value: number) => {
    if (value > 0) return "text-green-600 dark:text-green-400";
    if (value < 0) return "text-red-600 dark:text-red-400";
    return "text-gray-600 dark:text-gray-400";
  };

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value * 1000000); // Convert from millions to actual value
  };
  const formatMillions = (value: number) => {
    return `${value.toFixed(2)}M`;
  };
  // Format date for the chart
  const formatChartDate = (dateString: string) => {
    if (!dateString) return "";
    
    // Parse DD/MM/YYYY format
    const parts = dateString.split('/');
    if (parts.length !== 3) return dateString;
    
    const day = parseInt(parts[0], 10);
    const month = parseInt(parts[1], 10) - 1; // Month is 0-indexed in JavaScript Date
    const year = parseInt(parts[2], 10);
    
    const date = new Date(year, month, day);
    
    // Validate the date
    if (isNaN(date.getTime())) return dateString;
    
    return date.toLocaleDateString("pt-BR", { month: "short", day: "numeric" });
  };
  // Prepare chart data from flux data
  const prepareChartData = (data: FluxoDataPoint[]) => {
    return data
      .filter(item => item.Data) // Only include items with dates
      .map(item => {
        const total = (item.Estrangeiro || 0) + (item.Institucional || 0) + 
                     (item.PF || 0) + (item.IF || 0) + (item.Outros || 0);
        
        return {
          date: item.Data,
          displayDate: formatChartDate(item.Data || ''),
          Estrangeiro: item.Estrangeiro || 0,
          Institucional: item.Institucional || 0,
          PF: item.PF || 0,
          IF: item.IF || 0,
          Outros: item.Outros || 0,
          Total: total
        };
      })
      .reverse(); // Reverse to show chronological order (oldest to newest)
  };
  // Chart color palette for investor types
  const chartColors = {
    Estrangeiro: "#8884d8",
    Institucional: "#82ca9d",
    PF: "#ffc658",
    IF: "#ff7300",
    Outros: "#8dd1e1"
  };
  const calculateSummary = (data: FluxoDataPoint[]) => {
    if (!data.length) return null;

    // Calculate summary for individual investor types instead of total flow
    let totalPositiveFlow = 0;
    let totalNegativeFlow = 0;
    let count = 0;

    data.forEach(item => {
      // Sum positive and negative flows for each investor type
      [item.Estrangeiro, item.Institucional, item.PF, item.IF, item.Outros].forEach(flow => {
        if (flow && flow > 0) totalPositiveFlow += flow;
        if (flow && flow < 0) totalNegativeFlow += flow;
      });
      count++;
    });

    return {
      positiveFlow: totalPositiveFlow,
      negativeFlow: totalNegativeFlow,
      lastUpdate: new Date().toLocaleString('pt-BR')
    };
  };
  const fetchData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      let response: FluxoResponse;
      
      if (selectedInvestorType === "all") {
        response = await fetchFluxoData({
          limit: parseInt(timeRange)
        });
      } else {
        response = await fetchFluxoByInvestorType(
          selectedInvestorType as any,
          parseInt(timeRange)
        );
      }

      if (response.error) {
        throw new Error(response.error);
      }

      setFluxoData(response.data);
      const calculatedSummary = calculateSummary(response.data);
      setSummary(calculatedSummary);

    } catch (err: any) {
      console.error('Error fetching flux data:', err);
      setError(err.message || 'Erro ao carregar dados de fluxo');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [selectedInvestorType, timeRange]);

  const handleRefresh = () => {
    fetchData();
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-lg">Fluxo de Investimentos (DDM)</CardTitle>
              <CardDescription>Fluxo de recursos por tipo de investidor</CardDescription>
            </div>
            <Skeleton className="h-8 w-8 rounded" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 gap-4 mb-6">
            {[...Array(2)].map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-4 w-20" />
                <Skeleton className="h-6 w-full" />
              </div>
            ))}
          </div>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-center justify-between">
                <Skeleton className="h-4 w-24" />
                <div className="flex items-center gap-2">
                  <Skeleton className="h-4 w-16" />
                  <Skeleton className="h-4 w-20" />
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader>
          <CardTitle className="text-lg">Fluxo de Investimentos </CardTitle>
          <CardDescription>Fluxo de recursos por tipo de investidor</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-red-500 mb-4">{error}</p>
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />
              Tentar Novamente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Fluxo de Investimentos </CardTitle>
            <CardDescription>Fluxo de recursos por tipo de investidor</CardDescription>
          </div>
          <div className="flex items-center gap-2">
            <Select value={timeRange} onValueChange={setTimeRange}>
              <SelectTrigger className="w-20">
                <SelectValue />
              </SelectTrigger>              <SelectContent>
                <SelectItem value="20">20 registros</SelectItem>
                <SelectItem value="50">50 registros</SelectItem>
                <SelectItem value="100">100 registros</SelectItem>
                <SelectItem value="200">200 registros</SelectItem>
              </SelectContent>
            </Select>
            <Select value={selectedInvestorType} onValueChange={setSelectedInvestorType}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {investorTypes.map((type) => (
                  <SelectItem key={type.value} value={type.value}>
                    <div className="flex items-center gap-2">
                      <type.icon className="h-4 w-4" />
                      {type.label}
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Button onClick={handleRefresh} variant="outline" size="sm">
              <RefreshCw className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {summary && (
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Entrada</p>
              <div className="flex items-center gap-1">
                <ArrowUpIcon className="h-4 w-4 text-green-500" />
                <span className="font-medium text-green-600">
                  {formatMillions(summary.positiveFlow)}
                </span>
              </div>
            </div>
            
            <div className="space-y-1">
              <p className="text-sm text-muted-foreground">Saída</p>
              <div className="flex items-center gap-1">
                <ArrowDownIcon className="h-4 w-4 text-red-500" />
                <span className="font-medium text-red-600">
                  {formatMillions(Math.abs(summary.negativeFlow))}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Line Chart Visualization */}
        {fluxoData.length > 0 && (
          <div className="mb-6">
            <h3 className="text-sm font-medium mb-4">Evolução do Fluxo por Categoria</h3>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart
                  data={prepareChartData(fluxoData)}
                  margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis 
                    dataKey="displayDate" 
                    minTickGap={30}
                    fontSize={12}
                  />
                  <YAxis 
                    fontSize={12}
                    tickFormatter={(value) => `${value.toFixed(1)}M`}
                  />
                  <Tooltip 
                    labelFormatter={(label, payload) => {
                      const data = payload && payload[0] && payload[0].payload;
                      return data ? `Data: ${data.date}` : `Data: ${label}`;
                    }}
                    formatter={(value: number, name: string) => [
                      formatMillions(value),
                      name
                    ]}
                  />
                  <Legend />
                  <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />

                  {selectedInvestorType === "all" ? (
                    // Show all investor types when "all" is selected
                    <>
                      <Line
                        type="monotone"
                        dataKey="Estrangeiro"
                        name="Estrangeiro"
                        stroke={chartColors.Estrangeiro}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Institucional"
                        name="Institucional"
                        stroke={chartColors.Institucional}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="PF"
                        name="Pessoa Física"
                        stroke={chartColors.PF}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="IF"
                        name="Inst. Financeira"
                        stroke={chartColors.IF}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                      />
                      <Line
                        type="monotone"
                        dataKey="Outros"
                        name="Outros"
                        stroke={chartColors.Outros}
                        strokeWidth={2}
                        dot={{ r: 3 }}
                        activeDot={{ r: 5 }}
                      />
                    </>
                  ) : (
                    // Show selected investor type and total
                    <>
                      <Line
                        type="monotone"
                        dataKey={selectedInvestorType}
                        name={investorTypes.find(t => t.value === selectedInvestorType)?.label || selectedInvestorType}
                        stroke={chartColors[selectedInvestorType as keyof typeof chartColors] || "#8884d8"}
                        strokeWidth={3}
                        dot={{ r: 4 }}
                        activeDot={{ r: 6 }}
                      />
                    </>
                  )}
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>
        )}        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-medium">Fluxos Recentes</h3>
          </div>
          <TooltipProvider>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {fluxoData.slice(0, 10).map((item, index) => {
                return (
                  <div key={index} className="flex items-center justify-between py-2 px-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-3">
                      <UITooltip>
                        <TooltipTrigger asChild>
                          <div className="text-xs text-muted-foreground cursor-help">
                            {item.Data || `${index + 1}º`}
                          </div>
                        </TooltipTrigger>
                        <TooltipContent>
                          <div className="text-center">
                            <p className="font-medium">Data</p>
                            <p className="text-sm text-muted-foreground">
                              {item.Data || `Registro ${index + 1}`}
                            </p>
                            <p className="text-xs text-muted-foreground">
                              Clique para ver detalhes
                            </p>
                          </div>
                        </TooltipContent>
                      </UITooltip>
                      <div className="grid grid-cols-5 gap-2 text-xs">
                        {item.Estrangeiro !== undefined && (
                          <UITooltip>
                            <TooltipTrigger asChild>
                              <div className="flex items-center gap-1 cursor-help">
                                <Globe className="h-3 w-3" />
                                <span className={getFlowColor(item.Estrangeiro)}>
                                  {formatMillions(item.Estrangeiro)}
                                </span>
                              </div>
                            </TooltipTrigger>
                            <TooltipContent>
                              <div className="text-center">
                                <p className="font-medium">Estrangeiro</p>
                                <p className="text-sm text-muted-foreground">
                                  {item.Estrangeiro > 0 ? 'Entrada' : 'Saída'}: {formatCurrency(item.Estrangeiro)}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {item.Data || 'Data não disponível'}
                                </p>
                              </div>
                            </TooltipContent>
                          </UITooltip>
                        )}
                        {item.Institucional !== undefined && (
                          <UITooltip>
                            <TooltipTrigger asChild>
                              <div className="flex items-center gap-1 cursor-help">
                                <Building className="h-3 w-3" />
                                <span className={getFlowColor(item.Institucional)}>
                                  {formatMillions(item.Institucional)}
                                </span>
                              </div>
                            </TooltipTrigger>
                            <TooltipContent>
                              <div className="text-center">
                                <p className="font-medium">Institucional</p>
                                <p className="text-sm text-muted-foreground">
                                  {item.Institucional > 0 ? 'Entrada' : 'Saída'}: {formatCurrency(item.Institucional)}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {item.Data || 'Data não disponível'}
                                </p>
                              </div>
                            </TooltipContent>
                          </UITooltip>
                        )}
                        {item.PF !== undefined && (
                          <UITooltip>
                            <TooltipTrigger asChild>
                              <div className="flex items-center gap-1 cursor-help">
                                <Users className="h-3 w-3" />
                                <span className={getFlowColor(item.PF)}>
                                  {formatMillions(item.PF)}
                                </span>
                              </div>
                            </TooltipTrigger>
                            <TooltipContent>
                              <div className="text-center">
                                <p className="font-medium">Pessoa Física</p>
                                <p className="text-sm text-muted-foreground">
                                  {item.PF > 0 ? 'Entrada' : 'Saída'}: {formatCurrency(item.PF)}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {item.Data || 'Data não disponível'}
                                </p>
                              </div>
                            </TooltipContent>
                          </UITooltip>
                        )}
                        {item.IF !== undefined && (
                          <UITooltip>
                            <TooltipTrigger asChild>
                              <div className="flex items-center gap-1 cursor-help">
                                <Banknote className="h-3 w-3" />
                                <span className={getFlowColor(item.IF)}>
                                  {formatMillions(item.IF)}
                                </span>
                              </div>
                            </TooltipTrigger>
                            <TooltipContent>
                              <div className="text-center">
                                <p className="font-medium">Instituição Financeira</p>
                                <p className="text-sm text-muted-foreground">
                                  {item.IF > 0 ? 'Entrada' : 'Saída'}: {formatCurrency(item.IF)}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {item.Data || 'Data não disponível'}
                                </p>
                              </div>
                            </TooltipContent>
                          </UITooltip>
                        )}
                        {item.Outros !== undefined && (
                          <UITooltip>
                            <TooltipTrigger asChild>
                              <div className="flex items-center gap-1 cursor-help">
                                <Minus className="h-3 w-3" />
                                <span className={getFlowColor(item.Outros)}>
                                  {formatMillions(item.Outros)}
                                </span>
                              </div>
                            </TooltipTrigger>
                            <TooltipContent>
                              <div className="text-center">
                                <p className="font-medium">Outros</p>
                                <p className="text-sm text-muted-foreground">
                                  {item.Outros > 0 ? 'Entrada' : 'Saída'}: {formatCurrency(item.Outros)}
                                </p>
                                <p className="text-xs text-muted-foreground">
                                  {item.Data || 'Data não disponível'}
                                </p>
                              </div>
                            </TooltipContent>
                          </UITooltip>
                        )}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </TooltipProvider>
        </div>

        {summary && (
          <div className="mt-4 pt-4 border-t">
            <p className="text-xs text-muted-foreground">
              Última atualização: {summary.lastUpdate}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

export default FluxoDDMChart;
