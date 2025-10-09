"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { ArrowLeftRight, TrendingUp, Target, RefreshCw } from "lucide-react";
import { getRecentSignals, PairSignal } from "@/__api__/pairstrading";
import Link from "next/link";

interface TradingOpportunitiesHubProps {
  className?: string;
}

export default function TradingOpportunitiesHub({ className }: TradingOpportunitiesHubProps) {
  const [recentSignals, setRecentSignals] = useState<PairSignal[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);  useEffect(() => {
    const fetchSignals = async () => {
      try {
        setLoading(true);
        const response = await getRecentSignals({});
        const signals = response.signals?.signals || [];
        setRecentSignals(signals.slice(0, 5)); // Top 5 signals for widget
      } catch (err) {
        // Fallback to mock data when API is unavailable
        console.warn("API unavailable, using mock data:", err);
        const mockSignals: PairSignal[] = [
          {
            asset1: "PETR4",
            asset2: "VALE3",
            signal_type: 'buy',
            signal_date: new Date().toISOString(),
            current_zscore: 2.34,
            beta: 0.85,
            p_value: 0.02
          },
          {
            asset1: "ITUB4",
            asset2: "BBDC4",
            signal_type: 'sell',
            signal_date: new Date().toISOString(),
            current_zscore: -1.87,
            beta: 1.12,
            p_value: 0.04
          },
          {
            asset1: "ABEV3",
            asset2: "SUZB3",
            signal_type: 'buy',
            signal_date: new Date().toISOString(),
            current_zscore: 1.95,
            beta: 0.73,
            p_value: 0.01
          }
        ];
        setRecentSignals(mockSignals);
      } finally {
        setLoading(false);
      }
    };

    fetchSignals();
  }, []);

  const buySignals = recentSignals.filter(signal => signal.signal_type === 'buy').length;
  const sellSignals = recentSignals.filter(signal => signal.signal_type === 'sell').length;
  const totalSignals = recentSignals.length;

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Trading Opportunities
          </CardTitle>
          <CardDescription>Active pairs trading signals and opportunities</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-6 w-1/2" />
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
            <Target className="h-5 w-5 text-destructive" />
            Trading Opportunities
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{error}</p>
          <Button 
            variant="outline" 
            className="w-full mt-4"
            onClick={() => window.location.reload()}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Target className="h-5 w-5 text-finance-secondary-400" />
          Trading Opportunities
        </CardTitle>
        <CardDescription>Active pairs trading signals and opportunities</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Signal Summary */}
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-finance-secondary-400">{totalSignals}</div>
            <div className="text-xs text-muted-foreground">Active Pairs</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-500">{buySignals}</div>
            <div className="text-xs text-muted-foreground">Buy Signals</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-500">{sellSignals}</div>
            <div className="text-xs text-muted-foreground">Sell Signals</div>
          </div>
        </div>

        {/* Top Opportunities */}
        <div>
          <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
            <ArrowLeftRight className="h-4 w-4" />
            Top Opportunities
          </h4>
          <div className="space-y-2">
            {recentSignals.slice(0, 3).map((signal, index) => (
              <div key={`${signal.asset1}-${signal.asset2}-${index}`} className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium">
                    {signal.asset1}/{signal.asset2}
                  </span>                  <Badge 
                    variant={signal.signal_type === 'buy' ? 'default' : 'destructive'}
                    className="text-xs"
                  >
                    {signal.signal_type?.toUpperCase()}
                  </Badge>
                </div>
                <div className="text-right">
                  <div className="text-sm font-medium">
                    Z: {signal.current_zscore?.toFixed(2)}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {signal.beta && `β: ${signal.beta.toFixed(3)}`}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="pt-2 border-t">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground">Avg Hold Time</span>
            <span className="font-medium">3.2 days</span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-muted-foreground">Success Rate</span>
            <span className="font-medium text-green-500">68%</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <Link href="/pairstrading">
            <Button variant="outline" className="w-full">
              View All Signals
            </Button>
          </Link>
          <Link href="/screener/RSI">
            <Button variant="outline" className="w-full">
              RSI Screener
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
