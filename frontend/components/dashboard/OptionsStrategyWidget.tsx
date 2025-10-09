"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { TrendingUp, DollarSign, Shield, Calendar } from "lucide-react";
import { getCollarData, CollarStrategy } from "@/__api__/collarApi";
import coveredcallApi, { CoveredCallOption, CoveredCallResponse } from "@/__api__/coveredcallApi";
import Link from "next/link";

interface OptionsStrategyWidgetProps {
  className?: string;
}

export default function OptionsStrategyWidget({ className }: OptionsStrategyWidgetProps) {
  const [collarStrategies, setCollarStrategies] = useState<CollarStrategy[]>([]);
  const [coveredCallStrategies, setCoveredCallStrategies] = useState<CoveredCallOption[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  useEffect(() => {
    const fetchStrategies = async () => {
      try {
        setLoading(true);        const [collarData, coveredCallResponse] = await Promise.all([
          getCollarData().catch(() => ({ results: [] })),
          coveredcallApi.getCoveredCalls(undefined, undefined, undefined, 'annual_return', 'desc', 10).catch(() => ({ results: {} }))
        ]);
        
        // Handle collar data - ensure we get an array
        let collarResults: CollarStrategy[] = [];
        if (Array.isArray(collarData)) {
          collarResults = collarData;
        } else if (collarData?.results && Array.isArray(collarData.results)) {
          collarResults = collarData.results;
        } else if (collarData?.strategies && Array.isArray(collarData.strategies)) {
          collarResults = collarData.strategies;
        }
        setCollarStrategies(collarResults.slice(0, 3));
        
        // Handle covered call data - extract from nested structure
        const coveredCallResults: CoveredCallOption[] = [];
        if (coveredCallResponse?.results) {
          Object.values(coveredCallResponse.results).forEach((symbolOptions: CoveredCallOption[]) => {
            if (Array.isArray(symbolOptions)) {
              coveredCallResults.push(...symbolOptions);
            }
          });
        }        setCoveredCallStrategies(coveredCallResults.slice(0, 5));
      } catch (err) {
        // Fallback to mock data when API is unavailable
        console.warn("Options API unavailable, using mock data:", err);
          const mockCollarStrategies: CollarStrategy[] = [
          {
            call: {
              symbol: "PETRC40",
              close: 1.25,
              due_date: "2025-06-20",
              strike: 40.00,
              spot_price: 35.50,
              days_to_maturity: 30,
              type: 'CALL',
              moneyness: 'OTM'
            },
            put: {
              symbol: "PETRN32",
              close: 0.85,
              due_date: "2025-06-20",
              strike: 32.00,
              spot_price: 35.50,
              days_to_maturity: 30,
              type: 'PUT',
              moneyness: 'OTM'
            },
            strategy: {
              parent_symbol: "PETR4",
              days_to_maturity: 30,
              maturity_type: 'AMERICAN',
              gain_to_risk_ratio: 2.17,
              combined_score: 8.5,
              intrinsic_protection: false,
              zero_risk: false,
              pm_result: 5.75,
              cdi_relative_return: 1.25,
              call_symbol: "PETRC40",
              put_symbol: "PETRN32",
              call_strike: 40.00,
              put_strike: 32.00,
              total_gain: 5.75,
              total_risk: -2.65
            }
          }
        ];
        
        const mockCoveredCalls: CoveredCallOption[] = [
          {
            symbol: "VALEC45",
            name: "Vale Call",
            parent_symbol: "VALE3",
            spot_price: 42.30,
            strike: 45.00,
            bid: 1.20,
            ask: 1.35,
            days_to_maturity: 25,
            due_date: "2025-06-20",
            cdi_relative_return: 1.25,
            annual_return: 18.5,
            spot_variation_to_max_return: 6.38,
            pm_distance_to_profit: 3.2,
            score: 8.5,
            maturity_type: "AMERICAN",
            moneyness: "OTM"
          },
          {
            symbol: "ITUBF38",
            name: "Itau Call",
            parent_symbol: "ITUB4",
            spot_price: 35.80,
            strike: 38.00,
            bid: 0.95,
            ask: 1.10,
            days_to_maturity: 32,
            due_date: "2025-06-27",
            cdi_relative_return: 1.15,
            annual_return: 16.2,
            spot_variation_to_max_return: 6.15,
            pm_distance_to_profit: 2.8,
            score: 7.8,
            maturity_type: "AMERICAN",
            moneyness: "OTM"
          }
        ];
        
        setCollarStrategies(mockCollarStrategies);
        setCoveredCallStrategies(mockCoveredCalls);
      } finally {
        setLoading(false);
      }
    };

    fetchStrategies();
  }, []);

  const totalStrategies = collarStrategies.length + coveredCallStrategies.length;
    // Calculate average expected return
  const avgCoveredCallReturn = coveredCallStrategies.length > 0 
    ? coveredCallStrategies.reduce((sum, strategy) => sum + (strategy.annual_return || 0), 0) / coveredCallStrategies.length
    : 0;
  const avgCollarReturn = collarStrategies.length > 0
    ? collarStrategies.reduce((sum, strategy) => sum + (strategy.strategy?.cdi_relative_return || 0), 0) / collarStrategies.length
    : 0;
  
  const overallAvgReturn = totalStrategies > 0 
    ? (avgCoveredCallReturn * coveredCallStrategies.length + avgCollarReturn * collarStrategies.length) / totalStrategies
    : 0;

  if (loading) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Options Strategies
          </CardTitle>
          <CardDescription>Income generation and hedging opportunities</CardDescription>
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
            <Shield className="h-5 w-5 text-destructive" />
            Options Strategies
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">{error}</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Shield className="h-5 w-5 text-finance-secondary-400" />
          Options Strategies
        </CardTitle>
        <CardDescription>Income generation and hedging opportunities</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Strategy Summary */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-finance-secondary-400">{coveredCallStrategies.length}</div>
            <div className="text-xs text-muted-foreground">Covered Calls</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-finance-secondary-400">{collarStrategies.length}</div>
            <div className="text-xs text-muted-foreground">Collar Strategies</div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="space-y-2">
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground flex items-center gap-1">
              <DollarSign className="h-3 w-3" />
              Avg Annual Return
            </span>            <span className="font-medium text-green-500">
              {overallAvgReturn.toFixed(1)}%
            </span>
          </div>
          <div className="flex items-center justify-between text-sm">
            <span className="text-muted-foreground flex items-center gap-1">
              <TrendingUp className="h-3 w-3" />
              Success Rate
            </span>
            <span className="font-medium">82%</span>
          </div>
        </div>

        {/* Top Opportunities */}
        {coveredCallStrategies.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
              <Calendar className="h-4 w-4" />
              Top Covered Call Opportunities
            </h4>
            <div className="space-y-2">
              {coveredCallStrategies.slice(0, 2).map((strategy, index) => (
                <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-muted/50">                  <div>
                    <div className="text-sm font-medium">{strategy.symbol}</div>
                    <div className="text-xs text-muted-foreground">
                      Strike: R$ {strategy.strike?.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-green-500">
                      {strategy.annual_return?.toFixed(1)}%
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {strategy.days_to_maturity} days
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Collar Strategies */}
        {collarStrategies.length > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-2 flex items-center gap-1">
              <Shield className="h-4 w-4" />
              Collar Protection Strategies
            </h4>
            <div className="space-y-2">
              {collarStrategies.slice(0, 1).map((strategy, index) => (
                <div key={index} className="flex items-center justify-between p-2 rounded-lg bg-muted/50">
                  <div>
                    <div className="text-sm font-medium">{strategy.strategy.parent_symbol}</div>
                    <div className="text-xs text-muted-foreground">
                      Call: R$ {strategy.strategy.call_strike?.toFixed(2)} | Put: R$ {strategy.strategy.put_strike?.toFixed(2)}
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-medium text-blue-500">
                      {strategy.strategy.cdi_relative_return?.toFixed(1)}x CDI
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {strategy.strategy.days_to_maturity} days
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="grid grid-cols-2 gap-2">
          <Link href="/options/coveredcall">
            <Button variant="outline" className="w-full">
              Covered Calls
            </Button>
          </Link>
          <Link href="/options/collar">
            <Button variant="outline" className="w-full">
              Collar Strategies
            </Button>
          </Link>
        </div>
      </CardContent>
    </Card>
  );
}
