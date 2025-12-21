"use client";

import { useEffect, useState } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, TrendingUp, Shield, DollarSign, BarChart3, Target, AlertCircle } from "lucide-react";
import { getCryptoCollarData, CryptoCollarStrategy, generateCryptoCollarPayoffData } from "__api__/cryptoCollarApi";
import { Badge } from "@/components/ui/badge";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function CryptoCollarStrategyPage() {
  const [loading, setLoading] = useState(true);
  const [collarData, setCollarData] = useState<{[key: string]: {[key: string]: CryptoCollarStrategy[]}}>({});
  const [metadata, setMetadata] = useState<any>(null);
  const [selectedUnderlying, setSelectedUnderlying] = useState<string>("BTC");
  const [selectedStrategy, setSelectedStrategy] = useState<CryptoCollarStrategy | null>(null);
  const [payoffData, setPayoffData] = useState<any[]>([]);
  const { toast } = useToast();
  
  const underlyings = ["BTC", "ETH", "SOL", "BNB"];
  
  useEffect(() => {
    const fetchCollarData = async () => {
      try {
        setLoading(true);
        const data = await getCryptoCollarData({
          underlying: selectedUnderlying,
          exchange: 'bybit',
          min_days: 0,
          max_days: 90
        });
        setCollarData(data.results);
        setMetadata(data.metadata);
      } catch (error) {
        toast({
          title: "Error",
          description: "Failed to load crypto collar strategy data.",
          variant: "destructive"
        });
        console.error("Failed to fetch crypto collar data:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchCollarData();
  }, [selectedUnderlying, toast]);

  // Generate optimized payoff data when strategy is selected (using API function)
  useEffect(() => {
    console.log('useEffect triggered, selectedStrategy:', selectedStrategy);
    
    if (!selectedStrategy) {
      console.log('No selectedStrategy, clearing payoffData');
      setPayoffData([]);
      return;
    }

    // Use the centralized payoff generation function from the API
    const payoff = generateCryptoCollarPayoffData(selectedStrategy);
    
    console.log(`Generated optimized payoff data with ${payoff.length} points`);
    console.log('Sample payoff data:', payoff.slice(0, 5));
    setPayoffData(payoff);
  }, [selectedStrategy]);
  
  const handleStrategySelect = (strategy: CryptoCollarStrategy) => {
    setSelectedStrategy(strategy);
  };
  
  const handleBackToList = () => {
    setSelectedStrategy(null);
  };

  const renderStrategyTable = (strategies: CryptoCollarStrategy[]) => {
    if (!strategies || strategies.length === 0) {
      return (
        <div className="text-center py-8 text-muted-foreground">
          No strategies found for this timeframe
        </div>
      );
    }

    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Asset</th>
              <th className="text-left p-2">Call Strike</th>
              <th className="text-left p-2">Put Strike</th>
              <th className="text-left p-2">Days</th>
              <th className="text-right p-2">Max Gain</th>
              <th className="text-right p-2">Max Risk</th>
              <th className="text-right p-2">Gain/Risk</th>
              <th className="text-right p-2">Score</th>
              <th className="text-center p-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map((strategy, idx) => (
              <tr key={idx} className="border-b hover:bg-muted/50">
                <td className="p-2 font-medium">{strategy.strategy.underlying}</td>
                <td className="p-2">${strategy.strategy.call_strike.toLocaleString()}</td>
                <td className="p-2">${strategy.strategy.put_strike.toLocaleString()}</td>
                <td className="p-2">{strategy.strategy.days_to_maturity}</td>
                <td className="p-2 text-right text-green-600">${strategy.strategy.max_gain.toFixed(2)}</td>
                <td className="p-2 text-right text-red-600">${strategy.strategy.max_risk.toFixed(2)}</td>
                <td className="p-2 text-right font-medium">{strategy.strategy.gain_to_risk_ratio.toFixed(2)}</td>
                <td className="p-2 text-right">{strategy.strategy.combined_score.toFixed(2)}</td>
                <td className="p-2 text-center">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => handleStrategySelect(strategy)}
                  >
                    Details
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const renderStrategyDetail = () => {
    if (!selectedStrategy) return null;

    const { strategy, call, put } = selectedStrategy;
    
    // Format currency helper function (matching traditional collar)
    const formatCurrency = (value: number) => {
      return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    };

    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Strategy Details</h2>
          <Button variant="outline" onClick={handleBackToList}>
            Back to List
          </Button>
        </div>

        {/* Enhanced Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <TrendingUp className="mr-2 h-4 w-4" />
                Max Gain
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                ${strategy.max_gain.toFixed(2)}
              </div>
              {strategy.payoff_function && (
                <div className="text-xs text-muted-foreground">
                  From payoff: ${strategy.payoff_function.max_profit.toFixed(2)}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <Shield className="mr-2 h-4 w-4" />
                Max Risk
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-red-600">
                ${strategy.max_risk.toFixed(2)}
              </div>
              {strategy.payoff_function && (
                <div className="text-xs text-muted-foreground">
                  From payoff: ${strategy.payoff_function.max_loss.toFixed(2)}
                </div>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <DollarSign className="mr-2 h-4 w-4" />
                Gain/Risk Ratio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {strategy.gain_to_risk_ratio.toFixed(2)}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <Target className="mr-2 h-4 w-4" />
                Combined Score
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {strategy.combined_score.toFixed(3)}
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Call Option (Sold)
                {strategy.call_protection && strategy.call_protection > 0 && (
                  <Badge variant="default" className="text-xs">ITM</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Symbol:</span>
                <span className="font-mono text-xs">{call.symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Strike:</span>
                <span>${call.strike.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Price:</span>
                <span>${strategy.call_price.toFixed(2)}</span>
              </div>
              {strategy.call_intrinsic_value !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Intrinsic:</span>
                  <span className="text-green-600">${strategy.call_intrinsic_value.toFixed(2)}</span>
                </div>
              )}
              {strategy.call_extrinsic_value !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Extrinsic:</span>
                  <span className="text-blue-600">${strategy.call_extrinsic_value.toFixed(2)}</span>
                </div>
              )}
              {strategy.call_protection !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Protection:</span>
                  <span>{(strategy.call_protection * 100).toFixed(2)}%</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-muted-foreground">Delta:</span>
                <span>{strategy.call_delta?.toFixed(4) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Gamma:</span>
                <span>{strategy.call_gamma?.toFixed(6) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Theta:</span>
                <span>{strategy.call_theta?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Expiry:</span>
                <span>{call.expiry_date}</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                Put Option (Bought)
                {strategy.put_protection && strategy.put_protection > 0 && (
                  <Badge variant="default" className="text-xs">ITM</Badge>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Symbol:</span>
                <span className="font-mono text-xs">{put.symbol}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Strike:</span>
                <span>${put.strike.toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Price:</span>
                <span>${strategy.put_price.toFixed(2)}</span>
              </div>
              {strategy.put_intrinsic_value !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Intrinsic:</span>
                  <span className="text-green-600">${strategy.put_intrinsic_value.toFixed(2)}</span>
                </div>
              )}
              {strategy.put_extrinsic_value !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Extrinsic:</span>
                  <span className="text-blue-600">${strategy.put_extrinsic_value.toFixed(2)}</span>
                </div>
              )}
              {strategy.put_protection !== undefined && (
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Protection:</span>
                  <span>{(strategy.put_protection * 100).toFixed(2)}%</span>
                </div>
              )}
              <div className="flex justify-between">
                <span className="text-muted-foreground">Delta:</span>
                <span>{strategy.put_delta?.toFixed(4) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Gamma:</span>
                <span>{strategy.put_gamma?.toFixed(6) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Theta:</span>
                <span>{strategy.put_theta?.toFixed(2) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Expiry:</span>
                <span>{put.expiry_date}</span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Enhanced Payoff Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Gráfico de Payoff</CardTitle>
            <CardDescription>
              Lucro/prejuízo para diferentes níveis de preço da criptomoeda no vencimento
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Debug: Show payoff data status */}
            <div className="mb-4 p-2 bg-gray-100 text-xs text-gray-600">
              Debug: payoffData.length = {payoffData.length}, selectedStrategy = {selectedStrategy ? 'exists' : 'null'}
            </div>
            
            {payoffData.length === 0 ? (
              <div className="h-[28rem] w-full flex items-center justify-center text-muted-foreground">
                <Loader2 className="h-8 w-8 animate-spin" />
                <span className="ml-2">Gerando visualização...</span>
              </div>
            ) : (
              <div className="h-[28rem] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart
                    data={payoffData}
                    margin={{ top: 40, right: 50, left: 30, bottom: 50 }}
                  >
                  <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                  <XAxis 
                    dataKey="price" 
                    domain={['dataMin', 'dataMax']} 
                    tickFormatter={(value) => formatCurrency(value)}
                    label={{ value: 'Preço da Criptomoeda no Vencimento', position: 'insideBottom', offset: -10 }}
                  />
                  <YAxis
                    tickFormatter={(value) => formatCurrency(value)}
                    label={{ value: 'Lucro/Prejuízo', angle: -90, position: 'insideLeft', offset: 0 }}
                  />
                  <Tooltip
                    formatter={(value: any) => [formatCurrency(value), 'Lucro/Prejuízo']}
                    labelFormatter={(label) => `Preço da Criptomoeda: ${formatCurrency(label)}`}
                  />
                  <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
                  <ReferenceLine 
                    x={strategy.spot_price} 
                    stroke="#FF8C00" 
                    strokeDasharray="3 3"
                    label={{ value: 'Preço', position: 'top', fill: '#FF8C00', offset: 20 }} 
                  />
                  <ReferenceLine 
                    x={call.strike} 
                    stroke="#00CED1" 
                    strokeDasharray="3 3"
                    label={{ value: 'Strike Call', position: 'top', fill: '#00CED1', offset: 20 }} 
                  />
                  <ReferenceLine 
                    x={put.strike} 
                    stroke="#BA55D3" 
                    strokeDasharray="3 3"
                    label={{ value: 'Strike Put', position: 'top', fill: '#BA55D3', offset: 20 }} 
                  />
                  
                  {/* Gradient definitions for profit/loss areas */}
                  <defs>
                    <linearGradient id="profitGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#4CAF50" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#4CAF50" stopOpacity={0.2}/>
                    </linearGradient>
                    <linearGradient id="lossGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#FF5252" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#FF5252" stopOpacity={0.2}/>
                    </linearGradient>
                  </defs>
                  
                  {/* Area for profits (values >= 0) */}
                  <Area 
                    type="monotone" 
                    dataKey="payoff"
                    stroke="#4CAF50"
                    fill="url(#profitGradient)" 
                    activeDot={{ r: 8 }} 
                    baseValue={0}
                    isAnimationActive={false}
                    connectNulls
                    fillOpacity={1}
                    stackId="1"
                  />
                  
                  {/* Area for losses (values < 0) */}
                  <Area 
                    type="monotone" 
                    dataKey="negativePayoff"
                    stroke="#FF5252"
                    fill="url(#lossGradient)" 
                    activeDot={{ r: 8 }} 
                    baseValue={0}
                    isAnimationActive={false}
                    connectNulls
                    fillOpacity={1}
                    stackId="2"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            )}
            
            {/* Breakeven Points */}
            {strategy.payoff_function?.breakeven_points && strategy.payoff_function.breakeven_points.length > 0 && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-900/20 dark:border-blue-800">
                <div className="flex items-center mb-2">
                  <AlertCircle className="mr-2 h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-800 dark:text-blue-200">Breakeven Points</span>
                </div>
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  {strategy.payoff_function.breakeven_points.map((be, idx) => (
                    <span key={idx}>
                      ${be.toLocaleString()}
                      {idx < strategy.payoff_function!.breakeven_points.length - 1 && ', '}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Strategy Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Underlying:</span>
              <span className="font-medium">{strategy.underlying}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Spot Price:</span>
              <span>${strategy.spot_price.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Net Premium:</span>
              <span className={strategy.net_premium >= 0 ? 'text-green-600' : 'text-red-600'}>
                ${strategy.net_premium.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Days to Maturity:</span>
              <span>{strategy.days_to_maturity} days</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Intrinsic Protection:</span>
              <span>
                {strategy.intrinsic_protection ? (
                  <Badge variant="default">Yes</Badge>
                ) : (
                  <Badge variant="secondary">No</Badge>
                )}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Zero Risk:</span>
              <span>
                {strategy.zero_risk ? (
                  <Badge variant="default">Yes</Badge>
                ) : (
                  <Badge variant="secondary">No</Badge>
                )}
              </span>
            </div>
          </CardContent>
        </Card>

        {/* Risk and Return Analysis */}
        <Card>
          <CardHeader>
            <CardTitle>Risk and Return Analysis</CardTitle>
            <CardDescription>Financial metrics for this crypto collar strategy</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Return Metrics</h4>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max Gain:</span>
                  <span className="font-medium text-green-500">${strategy.max_gain.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Max Risk:</span>
                  <span className="font-medium text-red-500">${strategy.max_risk.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Gain/Risk Ratio:</span>
                  <span className="font-medium">{strategy.gain_to_risk_ratio.toFixed(2)}</span>
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Protection Metrics</h4>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Intrinsic Protection:</span>
                  <span className="font-medium">
                    {strategy.intrinsic_protection ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Call Protection:</span>
                  <span className="font-medium">
                    {strategy.call_protection ? `${(strategy.call_protection * 100).toFixed(2)}%` : 'N/A'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Zero Risk:</span>
                  <span className="font-medium">
                    {strategy.zero_risk ? 'Yes' : 'No'}
                  </span>
                </div>
              </div>
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Strategy Scores</h4>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Combined Score:</span>
                  <span className="font-medium">{strategy.combined_score.toFixed(3)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Days to Maturity:</span>
                  <span className="font-medium">{strategy.days_to_maturity} days</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Net Premium:</span>
                  <span className={`font-medium ${strategy.net_premium >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                    ${strategy.net_premium.toFixed(2)}
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (selectedStrategy) {
    return (
      <div className="container mx-auto py-6">
        {renderStrategyDetail()}
      </div>
    );
  }

  return (
    <div className="container mx-auto py-6">
      <div className="mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Crypto Collar Strategy</h1>
            <p className="text-muted-foreground">
              A collar is an options strategy that limits both upside potential and downside risk of an underlying cryptocurrency position.
            </p>
          </div>
          
          <div className="flex items-center gap-4">
            <Select value={selectedUnderlying} onValueChange={setSelectedUnderlying}>
              <SelectTrigger className="w-32">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {underlyings.map(underlying => (
                  <SelectItem key={underlying} value={underlying}>
                    {underlying}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>

        {metadata && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Spot Price</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">${metadata.spot_price.toLocaleString()}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Total Strategies</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{metadata.total_count}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Exchange</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold capitalize">{metadata.exchange}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Last Updated</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-sm">{new Date(metadata.timestamp).toLocaleString()}</div>
              </CardContent>
            </Card>
          </div>
        )}
        
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-900/20 dark:border-blue-800">
          <p className="text-blue-800 dark:text-blue-200 text-sm">
            ℹ️ Data sourced from Bybit Options Exchange. Only strategies with valid pricing are displayed.
          </p>
        </div>
      </div>

      {collarData && (
        <Tabs defaultValue="intrinsic" className="space-y-4">
          <div className="flex items-center justify-between">
            <TabsList>
              <TabsTrigger value="intrinsic">
                Intrinsic Protection
                {collarData.intrinsic && (
                  <Badge variant="secondary" className="ml-2">
                    {Object.values(collarData.intrinsic).flat().length}
                  </Badge>
                )}
              </TabsTrigger>
              <TabsTrigger value="otm">
                OTM Strategies
                {collarData.otm && (
                  <Badge variant="secondary" className="ml-2">
                    {Object.values(collarData.otm).flat().length}
                  </Badge>
                )}
              </TabsTrigger>
            </TabsList>
          </div>
          
          <TabsContent value="intrinsic" className="space-y-4">
            {collarData.intrinsic && (
              <Tabs defaultValue="less_than_14_days" className="space-y-4">
                <TabsList>
                  <TabsTrigger value="less_than_14_days">
                    &lt; 14 Days
                    {collarData.intrinsic.less_than_14_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.intrinsic.less_than_14_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="between_15_and_30_days">
                    15-30 Days
                    {collarData.intrinsic.between_15_and_30_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.intrinsic.between_15_and_30_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="between_30_and_60_days">
                    30-60 Days
                    {collarData.intrinsic.between_30_and_60_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.intrinsic.between_30_and_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="more_than_60_days">
                    &gt; 60 Days
                    {collarData.intrinsic.more_than_60_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.intrinsic.more_than_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="less_than_14_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Short-Term Collar Strategies (&lt; 14 days)</CardTitle>
                      <CardDescription>
                        Collar strategies with less than 14 days to expiration providing intrinsic protection
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.intrinsic.less_than_14_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="between_15_and_30_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Medium-Term Collar Strategies (15-30 days)</CardTitle>
                      <CardDescription>
                        Collar strategies with 15-30 days to expiration providing intrinsic protection
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.intrinsic.between_15_and_30_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="between_30_and_60_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Medium-Long Term Collar Strategies (30-60 days)</CardTitle>
                      <CardDescription>
                        Collar strategies with 30-60 days to expiration providing intrinsic protection
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.intrinsic.between_30_and_60_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="more_than_60_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Long-Term Collar Strategies (&gt; 60 days)</CardTitle>
                      <CardDescription>
                        Collar strategies with more than 60 days to expiration providing intrinsic protection
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.intrinsic.more_than_60_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            )}
          </TabsContent>
          
          <TabsContent value="otm" className="space-y-4">
            {collarData.otm && (
              <Tabs defaultValue="less_than_14_days" className="space-y-4">
                <TabsList>
                  <TabsTrigger value="less_than_14_days">
                    &lt; 14 Days
                    {collarData.otm.less_than_14_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.otm.less_than_14_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="between_15_and_30_days">
                    15-30 Days
                    {collarData.otm.between_15_and_30_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.otm.between_15_and_30_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="between_30_and_60_days">
                    30-60 Days
                    {collarData.otm.between_30_and_60_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.otm.between_30_and_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                  <TabsTrigger value="more_than_60_days">
                    &gt; 60 Days
                    {collarData.otm.more_than_60_days && (
                      <Badge variant="secondary" className="ml-2">
                        {collarData.otm.more_than_60_days.length}
                      </Badge>
                    )}
                  </TabsTrigger>
                </TabsList>
                
                <TabsContent value="less_than_14_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Short-Term OTM Collar Strategies (&lt; 14 days)</CardTitle>
                      <CardDescription>
                        Out-of-the-money collar strategies with less than 14 days to expiration
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.otm.less_than_14_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="between_15_and_30_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Medium-Term OTM Collar Strategies (15-30 days)</CardTitle>
                      <CardDescription>
                        Out-of-the-money collar strategies with 15-30 days to expiration
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.otm.between_15_and_30_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="between_30_and_60_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Medium-Long Term OTM Collar Strategies (30-60 days)</CardTitle>
                      <CardDescription>
                        Out-of-the-money collar strategies with 30-60 days to expiration
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.otm.between_30_and_60_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
                
                <TabsContent value="more_than_60_days" className="space-y-4">
                  <Card>
                    <CardHeader>
                      <CardTitle>Long-Term OTM Collar Strategies (&gt; 60 days)</CardTitle>
                      <CardDescription>
                        Out-of-the-money collar strategies with more than 60 days to expiration
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {renderStrategyTable(collarData.otm.more_than_60_days || [])}
                    </CardContent>
                  </Card>
                </TabsContent>
              </Tabs>
            )}
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}

