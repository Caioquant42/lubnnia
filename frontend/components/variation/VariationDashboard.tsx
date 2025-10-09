"use client";

import React, { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { AlertCircle, TrendingUp, TrendingDown, Minus } from "lucide-react";
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

const VariationDashboard: React.FC = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [stocks, setStocks] = useState<StockVariationData[]>([]);
  const [sunburstData, setSunburstData] = useState<SunburstData | null>(null);
  const [sentiment, setSentiment] = useState<MarketSentiment | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const response = await fetchStocksVariationData({ 
          sort_by: "variation",
          sort_order: "desc",
          limit: 100 // Get more stocks for better visualization
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
        setError("Failed to load stock variation data. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getSentimentIcon = (sentiment: string) => {
    switch (sentiment) {
      case 'Bullish':
      case 'Moderately Bullish':
        return <TrendingUp className="h-4 w-4 text-green-500" />;
      case 'Bearish':
      case 'Moderately Bearish':
        return <TrendingDown className="h-4 w-4 text-red-500" />;
      default:
        return <Minus className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getSentimentColor = (sentiment: string) => {
    switch (sentiment) {
      case 'Bullish':
        return 'text-green-600';
      case 'Moderately Bullish':
        return 'text-green-500';
      case 'Bearish':
        return 'text-red-600';
      case 'Moderately Bearish':
        return 'text-red-500';
      default:
        return 'text-yellow-600';
    }
  };
  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
            <Skeleton className="h-4 w-96" />
          </CardHeader>          <CardContent className="flex justify-center">
            <Skeleton className="h-[800px] w-[800px] max-w-4xl" />
          </CardContent>
        </Card>
        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-64" />
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-32" />
              <Skeleton className="h-4 w-64" />
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
                <Skeleton className="h-16 w-full" />
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertTitle>Error</AlertTitle>
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  return (
    <div className="space-y-6">
      {/* Market Sentiment Summary */}
      {sentiment && (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Market Sentiment</CardTitle>
              {getSentimentIcon(sentiment.sentiment)}
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${getSentimentColor(sentiment.sentiment)}`}>
                {sentiment.sentiment}
              </div>
              <p className="text-xs text-muted-foreground">
                {sentiment.description}
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Average Variation</CardTitle>
              {sentiment.avgVariation >= 0 ? (
                <TrendingUp className="h-4 w-4 text-green-500" />
              ) : (
                <TrendingDown className="h-4 w-4 text-red-500" />
              )}
            </CardHeader>
            <CardContent>
              <div className={`text-2xl font-bold ${sentiment.avgVariation >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {sentiment.avgVariation >= 0 ? '+' : ''}{sentiment.avgVariation}%
              </div>
              <p className="text-xs text-muted-foreground">
                Market-wide average
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Positive Stocks</CardTitle>
              <TrendingUp className="h-4 w-4 text-green-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {sentiment.positiveCount}
              </div>
              <p className="text-xs text-muted-foreground">
                {((sentiment.positiveCount / stocks.length) * 100).toFixed(1)}% of market
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Negative Stocks</CardTitle>
              <TrendingDown className="h-4 w-4 text-red-500" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                {sentiment.negativeCount}
              </div>
              <p className="text-xs text-muted-foreground">
                {((sentiment.negativeCount / stocks.length) * 100).toFixed(1)}% of market
              </p>
            </CardContent>
          </Card>
        </div>
      )}      {/* Sunburst Chart */}
      {sunburstData && (
        <Card>
          <CardHeader>
            <CardTitle>Market Sector Distribution</CardTitle>
            <CardDescription>
              Stock price variations by sector - size represents variation magnitude
            </CardDescription>
          </CardHeader>          <CardContent className="flex justify-center">
            <SunburstChart 
              data={sunburstData} 
              width={800} 
              height={800}
              className="w-full max-w-4xl" 
            />
          </CardContent>
        </Card>
      )}

      {/* Top Performers */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Top Gainers</CardTitle>
            <CardDescription>
              Stocks with the highest positive variations today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stocks
                .filter(stock => stock.variation > 0)
                .slice(0, 5)
                .map((stock) => (
                  <div key={stock.symbol} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{stock.symbol}</div>
                      <div className="text-sm text-muted-foreground">
                        {stock.name?.substring(0, 20)}{stock.name?.length > 20 ? '...' : ''}
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="default" className="bg-green-100 text-green-800">
                        +{stock.variation.toFixed(2)}%
                      </Badge>
                      <div className="text-sm text-muted-foreground">
                        ${stock.close.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Top Decliners</CardTitle>
            <CardDescription>
              Stocks with the highest negative variations today
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {stocks
                .filter(stock => stock.variation < 0)
                .sort((a, b) => a.variation - b.variation)
                .slice(0, 5)
                .map((stock) => (
                  <div key={stock.symbol} className="flex items-center justify-between">
                    <div>
                      <div className="font-medium">{stock.symbol}</div>
                      <div className="text-sm text-muted-foreground">
                        {stock.name?.substring(0, 20)}{stock.name?.length > 20 ? '...' : ''}
                      </div>
                    </div>
                    <div className="text-right">
                      <Badge variant="destructive">
                        {stock.variation.toFixed(2)}%
                      </Badge>
                      <div className="text-sm text-muted-foreground">
                        ${stock.close.toFixed(2)}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default VariationDashboard;
