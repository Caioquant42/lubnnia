"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { TrendingUp, TrendingDown, Minus, ChevronLeft, Home, BarChart3 } from "lucide-react";
import SunburstChart from "@/components/charts/SunburstChart";
import { 
  fetchStocksVariationData, 
  transformDataForSunburst, 
  getVariationSentiment,
  StockVariationData 
} from "@/__api__/variationApi";

interface MarketSentiment {
  sentiment: string;
  avgVariation: number;
  positiveCount: number;
  negativeCount: number;
  neutralCount: number;
  description: string;
}

interface SunburstData {
  name: string;
  children: {
    name: string;
    children: {
      name: string;
      value: number;
      variation: number;
      color: string;
      fullName: string;
      close: number;
      sector: string;
    }[];
  }[];
}

interface StockVariationChartProps {
  timeRange?: string;
}

const StockVariationChart: React.FC<StockVariationChartProps> = ({ timeRange = "1D" }) => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stocks, setStocks] = useState<StockVariationData[]>([]);
  const [sunburstData, setSunburstData] = useState<SunburstData | null>(null);
  const [sentiment, setSentiment] = useState<MarketSentiment | null>(null);
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [drillDownPath, setDrillDownPath] = useState<string[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetchStocksVariationData({ 
          sort_by: "variation",
          sort_order: "desc",
          limit: 50 // Smaller dataset for dashboard
        });
        
        setStocks(response.results);
        
        // Transform data for sunburst chart
        const chartData = transformDataForSunburst(response.results);
        setSunburstData(chartData);
        
        // Get market sentiment
        const marketSentiment = getVariationSentiment(response.results);
        setSentiment(marketSentiment);
        
        setError(null);
      } catch (err) {
        console.error("Error fetching variation data:", err);
        setError("Failed to load stock variation data");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [timeRange]);

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'bullish':
        return <TrendingUp className="h-4 w-4 text-green-600" />;
      case 'bearish':
        return <TrendingDown className="h-4 w-4 text-red-600" />;
      default:
        return <Minus className="h-4 w-4 text-gray-600" />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment.toLowerCase()) {
      case 'bullish':
        return 'text-green-600';
      case 'bearish':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const formatVariation = (variation: number) => {
    const sign = variation >= 0 ? '+' : '';
    return `${sign}${variation.toFixed(2)}%`;
  };

  const getVariationBadgeVariant = (variation: number) => {
    if (variation > 1) return 'default'; // Green-ish for positive
    if (variation > 0) return 'secondary';
    if (variation > -1) return 'outline';
    return 'destructive'; // Red for negative
  };

  const handleSectorClick = (sectorName: string) => {
    setSelectedSector(sectorName);
    setDrillDownPath(['Home', sectorName]);
  };

  const handleBackToRoot = () => {
    setSelectedSector(null);
    setDrillDownPath([]);
  };

  const getTimeRangeLabel = (range: string) => {
    switch (range) {
      case '1D': return '1 Dia';
      case '1W': return '1 Semana';
      case '1M': return '1 Mês';
      case '3M': return '3 Meses';
      case '1Y': return '1 Ano';
      default: return range;
    }
  };

  if (loading) {
    return (
      <Card className="w-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Variações IBOV</CardTitle>
          <CardDescription className="text-sm">
            Sentimento do mercado e mudanças de preço - {getTimeRangeLabel(timeRange)}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
              <Skeleton className="h-8 w-full" />
            </div>
            <div className="flex justify-center">
              <Skeleton className="h-[600px] w-[600px]" />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
              </div>
              <div className="space-y-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="w-full">
        <CardHeader className="pb-3">
          <CardTitle className="text-lg">Variações IBOV</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-4">
            <p className="text-red-500 text-sm">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Get top gainers and decliners with proper data
  const topGainers = stocks
    .filter(stock => stock.variation > 0)
    .slice(0, 3);

  const topDecliners = stocks
    .filter(stock => stock.variation < 0)
    .slice(-3)
    .reverse();

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="text-lg">Variações IBOV</CardTitle>
            <CardDescription className="text-sm">
              Sentimento do mercado e mudanças de preço - {getTimeRangeLabel(timeRange)}
            </CardDescription>
          </div>
          {selectedSector && (
            <Button
              variant="outline"
              size="sm"
              onClick={handleBackToRoot}
              className="flex items-center gap-2"
            >
              <ChevronLeft className="h-4 w-4" />
              Voltar
            </Button>
          )}
        </div>
        
        {/* Breadcrumb Navigation */}
        {drillDownPath.length > 0 && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground mt-2">
            {drillDownPath.map((path, index) => (
              <React.Fragment key={index}>
                {index > 0 && <span>/</span>}
                <span className="flex items-center gap-1">
                  {index === 0 ? <Home className="h-3 w-3" /> : <BarChart3 className="h-3 w-3" />}
                  {path}
                </span>
              </React.Fragment>
            ))}
          </div>
        )}
      </CardHeader>
      
      <CardContent>
        <div className="space-y-3">
          {/* Enhanced Market Sentiment Summary */}
          {sentiment && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border">
                <div className="flex items-center gap-2">
                  {getSentimentIcon(sentiment.sentiment)}
                  <span className="text-sm font-medium">Sentimento</span>
                </div>
                <span className={`text-sm font-bold ${getSentimentColor(sentiment.sentiment)}`}>
                  {sentiment.sentiment}
                </span>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border">
                <span className="text-sm font-medium">Mudança Média</span>
                <Badge variant={getVariationBadgeVariant(sentiment.avgVariation)} className="text-sm">
                  {formatVariation(sentiment.avgVariation)}
                </Badge>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border">
                <span className="text-sm font-medium">Positivas</span>
                <span className="text-sm font-bold text-green-600">
                  {sentiment.positiveCount} ({((sentiment.positiveCount / stocks.length) * 100).toFixed(0)}%)
                </span>
              </div>
            </div>
          )}

          {/* Enhanced Sunburst Chart with Interactivity */}
          {sunburstData && (
            <div className="w-full flex justify-center">
              <div className="relative">
                <SunburstChart 
                  data={sunburstData} 
                  width={600} 
                  height={600}
                  onSectorClick={handleSectorClick}
                  selectedSector={selectedSector}
                />
                
                {/* Enhanced Center Info Display */}
                <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                  <div className="bg-gradient-to-br from-purple-900/90 to-purple-800/90 backdrop-blur-sm rounded-full p-6 text-center shadow-2xl border border-purple-600/30 min-w-[120px] min-h-[120px] flex flex-col items-center justify-center">
                    <div className="text-xs text-purple-200 mb-1 font-medium">
                      {selectedSector ? 'Setor Selecionado' : 'Visão Geral'}
                    </div>
                    <div className="text-lg font-bold text-white mb-1">
                      {selectedSector || `${stocks.length} Ações`}
                    </div>
                    {selectedSector ? (
                      <div className="text-xs text-purple-300 mt-1">
                        Clique para voltar
                      </div>
                    ) : (
                      <div className="text-xs text-purple-300 mt-1">
                        Clique nos setores
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Enhanced Top Performers Summary */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg border border-green-200 shadow-sm">
              <h4 className="text-sm font-semibold mb-4 text-green-800 flex items-center gap-2">
                <TrendingUp className="h-5 w-5" />
                Maiores Altas
              </h4>
              <div className="space-y-3">
                {topGainers.map((stock, index) => (
                  <div key={stock.symbol} className="flex justify-between items-center p-2 bg-white/60 rounded-md border border-green-200/50">
                    <div className="flex items-center gap-3">
                      <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center text-xs font-bold text-green-700">
                        {index + 1}
                      </div>
                      <div className="flex flex-col">
                        <span className="font-semibold text-sm text-gray-900">{stock.symbol}</span>
                        <span className="text-xs text-gray-600 truncate max-w-[120px]">{stock.name}</span>
                      </div>
                    </div>
                    <Badge variant="default" className="text-xs h-7 px-2 font-semibold bg-green-600 hover:bg-green-700">
                      {formatVariation(stock.variation)}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 bg-gradient-to-br from-red-50 to-red-100 rounded-lg border border-red-200 shadow-sm">
              <h4 className="text-sm font-semibold mb-4 text-red-800 flex items-center gap-2">
                <TrendingDown className="h-5 w-5" />
                Maiores Baixas
              </h4>
              <div className="space-y-3">
                {topDecliners.map((stock, index) => (
                  <div key={stock.symbol} className="flex justify-between items-center p-2 bg-white/60 rounded-md border border-red-200/50">
                    <div className="flex items-center gap-3">
                      <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center text-xs font-bold text-red-700">
                        {index + 1}
                      </div>
                      <div className="flex flex-col">
                        <span className="font-semibold text-sm text-gray-900">{stock.symbol}</span>
                        <span className="text-xs text-gray-600 truncate max-w-[120px]">{stock.name}</span>
                      </div>
                    </div>
                    <Badge variant="destructive" className="text-xs h-7 px-2 font-semibold">
                      {formatVariation(stock.variation)}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default StockVariationChart;
