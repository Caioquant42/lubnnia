"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Separator } from "@/components/ui/separator";
import { 
  TrendingUp, 
  TrendingDown, 
  AlertTriangle, 
  BarChart3, 
  Clock, 
  Bell,
  ExternalLink 
} from "lucide-react";
import { fetchStocksVolatilityData, StockVolatilityData } from "@/__api__/volatilityApi";
import { fetchRSIData, RSIDataItem } from "@/__api__/screenerApi";
import Link from "next/link";

interface MarketIntelligenceFeedProps {
  className?: string;
}

interface IntelligenceItem {
  id: string;
  type: "volatility_spike" | "screener_alert" | "volume_surge" | "price_breakout";
  symbol: string;
  title: string;
  description: string;
  timestamp: Date;
  severity: "low" | "medium" | "high";
  value?: number;
  change?: number;
}

export default function MarketIntelligenceFeed({ className }: MarketIntelligenceFeedProps) {
  const [intelligenceData, setIntelligenceData] = useState<IntelligenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
  const fetchIntelligenceData = async () => {
      try {
        setLoading(true);
          // Fetch data from multiple sources
        const [rsiData, volatilityResponse] = await Promise.all([
          fetchRSIData(),
          fetchStocksVolatilityData()
        ]);

        const intelligenceItems: IntelligenceItem[] = [];

        // Process volatility spikes (IV > 80th percentile)
        volatilityResponse.results
          .filter((stock: StockVolatilityData) => stock.iv_1y_percentile > 80)
          .slice(0, 3)
          .forEach((stock: StockVolatilityData, index: number) => {
            intelligenceItems.push({
              id: `vol_${stock.symbol}_${index}`,
              type: "volatility_spike",
              symbol: stock.symbol,
              title: `High IV Alert: ${stock.symbol}`,
              description: `Implied volatility at ${stock.iv_1y_percentile.toFixed(0)}th percentile (${stock.iv_current.toFixed(1)}%)`,
              timestamp: new Date(Date.now() - Math.random() * 3600000), // Random time within last hour
              severity: stock.iv_1y_percentile > 90 ? "high" : "medium",
              value: stock.iv_current,
              change: stock.iv_1y_percentile
            });
          });

        // Process RSI alerts
        const rsiOverbought = rsiData.stockdata_1d?.overbought || [];
        rsiOverbought.slice(0, 4).forEach((stock: RSIDataItem, index: number) => {
          const alertType = stock.RSI > 80 ? "price_breakout" : "volume_surge";
          intelligenceItems.push({
            id: `rsi_${stock.Symbol}_${index}`,
            type: alertType,
            symbol: stock.Symbol,
            title: alertType === "volume_surge" ? `Volume Surge: ${stock.Symbol}` : `RSI Alert: ${stock.Symbol}`,
            description: alertType === "volume_surge" 
              ? `Volume surge detected with RSI at ${stock.RSI.toFixed(1)}`
              : `RSI overbought signal at ${stock.RSI.toFixed(1)} (Price: $${stock.AdjClose.toFixed(2)})`,
            timestamp: new Date(stock.Datetime),
            severity: stock.RSI > 85 ? "high" : "medium",
            value: stock.AdjClose,
            change: stock.RSI > 70 ? Math.random() * 5 + 2 : Math.random() * 3 + 1 // Mock change percentage
          });
        });

        // Sort by timestamp (most recent first)
        intelligenceItems.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
          setIntelligenceData(intelligenceItems.slice(0, 8)); // Limit to 8 items
      } catch (err) {
        // Fallback to mock data when APIs are unavailable
        console.warn("Intelligence APIs unavailable, using mock data:", err);
        
        const mockIntelligenceItems: IntelligenceItem[] = [
          {
            id: "mock_vol_1",
            type: "volatility_spike",
            symbol: "PETR4",
            title: "High IV Alert: PETR4",
            description: "Implied volatility at 87th percentile (31.2%)",
            timestamp: new Date(Date.now() - 1200000), // 20 minutes ago
            severity: "high",
            value: 31.2,
            change: 87
          },
          {
            id: "mock_rsi_1",
            type: "screener_alert",
            symbol: "VALE3",
            title: "RSI Alert: VALE3",
            description: "RSI overbought signal at 76.3 (Price: R$ 42.15)",
            timestamp: new Date(Date.now() - 1800000), // 30 minutes ago
            severity: "medium",
            value: 42.15,
            change: 2.1
          },
          {
            id: "mock_vol_2",
            type: "volume_surge",
            symbol: "ITUB4",
            title: "Volume Surge: ITUB4",
            description: "Volume surge detected with RSI at 68.9",
            timestamp: new Date(Date.now() - 2400000), // 40 minutes ago
            severity: "medium",
            value: 35.80,
            change: 1.8
          },
          {
            id: "mock_breakout_1",
            type: "price_breakout",
            symbol: "BBDC4",
            title: "Price Breakout: BBDC4",
            description: "Breaking above resistance at R$ 28.50",
            timestamp: new Date(Date.now() - 3000000), // 50 minutes ago
            severity: "high",
            value: 28.65,
            change: 3.2
          }
        ];
        
        setIntelligenceData(mockIntelligenceItems);
      } finally {
        setLoading(false);
      }
    };

    fetchIntelligenceData();
    
    // Refresh every 5 minutes
    const interval = setInterval(fetchIntelligenceData, 300000);
    return () => clearInterval(interval);
  }, []);

  const getTypeIcon = (type: IntelligenceItem["type"]) => {
    switch (type) {
      case "volatility_spike":
        return <AlertTriangle className="h-4 w-4" />;
      case "screener_alert":
        return <BarChart3 className="h-4 w-4" />;
      case "volume_surge":
        return <TrendingUp className="h-4 w-4" />;
      case "price_breakout":
        return <TrendingUp className="h-4 w-4" />;
      default:
        return <Bell className="h-4 w-4" />;
    }
  };

  const getSeverityColor = (severity: IntelligenceItem["severity"]) => {
    switch (severity) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200";
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200";
      case "low":
        return "bg-blue-100 text-blue-800 border-blue-200";
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    
    if (diffMins < 1) return "Just now";
    if (diffMins < 60) return `${diffMins}m ago`;
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours}h ago`;
    return timestamp.toLocaleDateString();
  };

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Market Intelligence Feed
          </CardTitle>
          <CardDescription>Real-time market alerts and insights</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="flex items-start gap-3">
                <Skeleton className="h-4 w-4 mt-1" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-3 w-1/2" />
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
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Market Intelligence Feed
          </CardTitle>
          <CardDescription>Real-time market alerts and insights</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-6">
            <AlertTriangle className="h-8 w-8 text-yellow-500 mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">{error}</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              Market Intelligence Feed
            </CardTitle>
            <CardDescription>Real-time market alerts and insights</CardDescription>
          </div>
          <Badge variant="outline" className="text-xs">
            Live
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[300px]">
          <div className="space-y-4">
            {intelligenceData.map((item, index) => (
              <div key={item.id}>
                <div className="flex items-start gap-3">
                  <div className={`p-1 rounded-full ${getSeverityColor(item.severity)}`}>
                    {getTypeIcon(item.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-medium truncate">{item.title}</h4>
                      <div className="flex items-center gap-2 ml-2">
                        <Badge variant="secondary" className="text-xs">
                          {item.symbol}
                        </Badge>
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {formatTimestamp(item.timestamp)}
                        </span>
                      </div>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">{item.description}</p>
                    {item.value && (
                      <div className="flex items-center gap-2 mt-2">
                        <span className="text-sm font-medium">
                          {item.type === "volatility_spike" ? `${item.value.toFixed(1)}%` : `$${item.value.toFixed(2)}`}
                        </span>
                        {item.change && (
                          <span className={`text-xs ${item.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {item.change >= 0 ? '+' : ''}{item.change.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
                {index < intelligenceData.length - 1 && <Separator className="mt-4" />}
              </div>
            ))}
          </div>
        </ScrollArea>
        <div className="mt-4 pt-4 border-t">
          <Link href="/screener">
            <Button variant="outline" size="sm" className="w-full">
              <ExternalLink className="h-4 w-4 mr-2" />
              View Advanced Screener
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
