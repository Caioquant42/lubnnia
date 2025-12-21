"use client";

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { RadioGroup, RadioGroupItem } from "@/components/ui/radio-group";
import { useToast } from "@/components/ui/use-toast";
import { Loader2, TrendingUp, Shield, DollarSign, Target, AlertCircle, ArrowLeft } from "lucide-react";
import { getTailHedgeStrategies, TailHedgeStrategy, generateTailHedgePayoffData } from "__api__/tailHedgeApi";
import { Badge } from "@/components/ui/badge";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export default function TailHedgeStrategyPage() {
  const [loading, setLoading] = useState(false);
  const [strategies, setStrategies] = useState<TailHedgeStrategy[]>([]);
  const [metadata, setMetadata] = useState<any>(null);
  const [selectedUnderlying, setSelectedUnderlying] = useState<string>("BTC");
  const [selectedStrategy, setSelectedStrategy] = useState<TailHedgeStrategy | null>(null);
  const [payoffData, setPayoffData] = useState<any[]>([]);
  const { toast } = useToast();
  
  // Portfolio input state
  const [portfolioSize, setPortfolioSize] = useState<string>("1000");
  const [portfolioType, setPortfolioType] = useState<'units' | 'usd'>('units');
  const [portfolioHedgePercentage, setPortfolioHedgePercentage] = useState<'0.5' | '0.75' | '1'>('0.5');
  const [financingPercentage, setFinancingPercentage] = useState<'0.5' | '0.75' | '1'>('0.5');
  
  // Strategy parameters
  const [putDeltaMin, setPutDeltaMin] = useState<string>("-0.20");
  const [putDeltaMax, setPutDeltaMax] = useState<string>("-0.10");
  const [callDelta, setCallDelta] = useState<string>("0.05");
  const [putMinDays, setPutMinDays] = useState<string>("30");
  const [putMaxDays, setPutMaxDays] = useState<string>("60");
  const [callMinDays, setCallMinDays] = useState<string>("60");
  const [callMaxDays, setCallMaxDays] = useState<string>("90");
  const [minMaturityDiff, setMinMaturityDiff] = useState<string>("7");
  
  const underlyings = ["BTC", "ETH", "SOL", "BNB"];
  
  // Helper to convert selected percentage strings to numbers for API
  const toNumber = (value: '0.5' | '0.75' | '1'): number => parseFloat(value);
  
  const fetchStrategies = async () => {
    try {
      setLoading(true);
      const size = parseFloat(portfolioSize);
      if (isNaN(size) || size <= 0) {
        toast({
          title: "Error",
          description: "Please enter a valid portfolio size.",
          variant: "destructive"
        });
        return;
      }
      
      const data = await getTailHedgeStrategies({
        underlying: selectedUnderlying,
        exchange: 'bybit',
        portfolio_size: size,
        portfolio_type: portfolioType,
        portfolio_hedge_percentage: toNumber(portfolioHedgePercentage),
        financing_percentage: toNumber(financingPercentage),
        put_delta_min: parseFloat(putDeltaMin),
        put_delta_max: parseFloat(putDeltaMax),
        call_delta: parseFloat(callDelta),
        put_min_days: parseInt(putMinDays),
        put_max_days: parseInt(putMaxDays),
        call_min_days: parseInt(callMinDays),
        call_max_days: parseInt(callMaxDays),
        min_maturity_diff: parseInt(minMaturityDiff)
      });
      
      setStrategies(data.strategies);
      setMetadata(data.metadata);
    } catch (error: any) {
      toast({
        title: "Error",
        description: error.response?.data?.error || "Failed to load tail hedge strategies.",
        variant: "destructive"
      });
      console.error("Failed to fetch tail hedge data:", error);
    } finally {
      setLoading(false);
    }
  };
  
  // Generate payoff data when strategy is selected
  useEffect(() => {
    if (!selectedStrategy) {
      setPayoffData([]);
      return;
    }
    
    const payoff = generateTailHedgePayoffData(selectedStrategy);
    setPayoffData(payoff);
  }, [selectedStrategy]);
  
  const handleStrategySelect = (strategy: TailHedgeStrategy) => {
    setSelectedStrategy(strategy);
  };
  
  const handleBackToList = () => {
    setSelectedStrategy(null);
  };
  
  const formatCurrency = (value: number) => {
    return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  };
  
  const renderStrategyTable = () => {
    if (!strategies || strategies.length === 0) {
      return (
        <div className="text-center py-8 text-muted-foreground">
          No strategies found. Try adjusting your parameters.
        </div>
      );
    }
    
    return (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b">
              <th className="text-left p-2">Put Strike</th>
              <th className="text-left p-2">Call Strike</th>
              <th className="text-left p-2">Put Qty</th>
              <th className="text-left p-2">Call Qty</th>
              <th className="text-right p-2">Net Cost</th>
              <th className="text-right p-2">Financing</th>
              <th className="text-right p-2">Protection</th>
              <th className="text-center p-2">Action</th>
            </tr>
          </thead>
          <tbody>
            {strategies.map((strategy, idx) => (
              <tr key={idx} className="border-b hover:bg-muted/50">
                <td className="p-2">${strategy.put.strike.toLocaleString()}</td>
                <td className="p-2">${strategy.call.strike.toLocaleString()}</td>
                <td className="p-2">{strategy.strategy_metrics.put_quantity.toFixed(2)}</td>
                <td className="p-2">{strategy.strategy_metrics.call_quantity.toFixed(2)}</td>
                <td className="p-2 text-right">{formatCurrency(strategy.strategy_metrics.net_cost)}</td>
                <td className="p-2 text-right">{(strategy.strategy_metrics.financing_ratio * 100).toFixed(1)}%</td>
                <td className="p-2 text-right">{formatCurrency(strategy.strategy_metrics.protection_coverage)}</td>
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
    
    const { put, call, strategy_metrics } = selectedStrategy;
    
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold">Strategy Details</h2>
          <Button variant="outline" onClick={handleBackToList}>
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to List
          </Button>
        </div>
        
        {/* Metrics Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <DollarSign className="mr-2 h-4 w-4" />
                Net Cost
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(strategy_metrics.net_cost)}
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <Shield className="mr-2 h-4 w-4" />
                Protection Coverage
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {formatCurrency(strategy_metrics.protection_coverage)}
              </div>
              <div className="text-xs text-muted-foreground">
                {(strategy_metrics.protection_percentage * 100).toFixed(0)}% of portfolio
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <Target className="mr-2 h-4 w-4" />
                Financing Ratio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {(strategy_metrics.financing_ratio * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-muted-foreground">
                Target: {(strategy_metrics.financing_percentage * 100).toFixed(0)}%
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium flex items-center">
                <TrendingUp className="mr-2 h-4 w-4" />
                Max Loss Protected
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(strategy_metrics.max_loss_protected)}
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Option Details */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Put Option (Long)</CardTitle>
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
                <span>{formatCurrency(put.price)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Delta:</span>
                <span>{put.delta?.toFixed(4) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Quantity:</span>
                <span>{strategy_metrics.put_quantity.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Cost:</span>
                <span className="font-medium">{formatCurrency(strategy_metrics.total_put_cost)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Expiry:</span>
                <span>{put.expiry_date}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Days to Expiry:</span>
                <span>{put.days_to_expiry} days</span>
              </div>
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Call Option (Short)</CardTitle>
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
                <span>{formatCurrency(call.price)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Delta:</span>
                <span>{call.delta?.toFixed(4) || 'N/A'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Quantity:</span>
                <span>{strategy_metrics.call_quantity.toFixed(2)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Total Premium:</span>
                <span className="font-medium text-green-600">{formatCurrency(strategy_metrics.total_call_premium)}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Expiry:</span>
                <span>{call.expiry_date}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Days to Expiry:</span>
                <span>{call.days_to_expiry} days</span>
              </div>
            </CardContent>
          </Card>
        </div>
        
        {/* Payoff Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Payoff Chart</CardTitle>
            <CardDescription>
              Profit/loss for different price levels at expiration
            </CardDescription>
          </CardHeader>
          <CardContent>
            {payoffData.length === 0 ? (
              <div className="h-[28rem] w-full flex items-center justify-center text-muted-foreground">
                <Loader2 className="h-8 w-8 animate-spin" />
                <span className="ml-2">Generating visualization...</span>
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
                      label={{ value: 'Price at Expiration', position: 'insideBottom', offset: -10 }}
                    />
                    <YAxis
                      tickFormatter={(value) => formatCurrency(value)}
                      label={{ value: 'Profit/Loss', angle: -90, position: 'insideLeft', offset: 0 }}
                    />
                    <Tooltip
                      formatter={(value: any) => [formatCurrency(value), 'Profit/Loss']}
                      labelFormatter={(label) => `Price: ${formatCurrency(label)}`}
                    />
                    <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
                    <ReferenceLine 
                      x={metadata?.spot_price} 
                      stroke="#FF8C00" 
                      strokeDasharray="3 3"
                      label={{ value: 'Spot', position: 'top', fill: '#FF8C00', offset: 20 }} 
                    />
                    <ReferenceLine 
                      x={put.strike} 
                      stroke="#BA55D3" 
                      strokeDasharray="3 3"
                      label={{ value: 'Put Strike', position: 'top', fill: '#BA55D3', offset: 20 }} 
                    />
                    <ReferenceLine 
                      x={call.strike} 
                      stroke="#00CED1" 
                      strokeDasharray="3 3"
                      label={{ value: 'Call Strike', position: 'top', fill: '#00CED1', offset: 20 }} 
                    />
                    
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
            
            {selectedStrategy.payoff_function?.breakeven_points && selectedStrategy.payoff_function.breakeven_points.length > 0 && (
              <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg dark:bg-blue-900/20 dark:border-blue-800">
                <div className="flex items-center mb-2">
                  <AlertCircle className="mr-2 h-4 w-4 text-blue-600" />
                  <span className="font-medium text-blue-800 dark:text-blue-200">Breakeven Points</span>
                </div>
                <div className="text-sm text-blue-700 dark:text-blue-300">
                  {selectedStrategy.payoff_function.breakeven_points.map((be, idx) => (
                    <span key={idx}>
                      {formatCurrency(be)}
                      {idx < selectedStrategy.payoff_function!.breakeven_points.length - 1 && ', '}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  };
  
  if (loading && !metadata) {
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
        <h1 className="text-3xl font-bold tracking-tight mb-2">Tail Hedge Strategy</h1>
        <p className="text-muted-foreground mb-6">
          Protect your portfolio against tail risk by combining long puts (shorter maturity) with short calls (longer maturity) to finance the protection.
        </p>
        
        {/* Portfolio Input Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Portfolio Configuration</CardTitle>
            <CardDescription>Enter your portfolio size and select protection parameters</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Portfolio Type</Label>
                <Select value={portfolioType} onValueChange={(value: 'units' | 'usd') => setPortfolioType(value)}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="units">Units (e.g., 1000 BTC)</SelectItem>
                    <SelectItem value="usd">USD Value (e.g., $65,000,000)</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              <div className="space-y-2">
                <Label>Portfolio Size</Label>
                <Input
                  type="number"
                  value={portfolioSize}
                  onChange={(e) => setPortfolioSize(e.target.value)}
                  placeholder={portfolioType === 'units' ? '1000' : '65000000'}
                />
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="space-y-3">
                <Label>Portfolio Hedge Percentage</Label>
                <RadioGroup
                  value={portfolioHedgePercentage || '0.5'}
                  onValueChange={(value) => {
                    // Ensure only valid values are set
                    const validValue = value === '0.5' || value === '0.75' || value === '1' ? value : '0.5';
                    setPortfolioHedgePercentage(validValue);
                  }}
                  className="space-y-2"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="0.5" id="hedge-50" />
                    <Label htmlFor="hedge-50" className="cursor-pointer font-normal">50%</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="0.75" id="hedge-75" />
                    <Label htmlFor="hedge-75" className="cursor-pointer font-normal">75%</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="1" id="hedge-100" />
                    <Label htmlFor="hedge-100" className="cursor-pointer font-normal">100%</Label>
                  </div>
                </RadioGroup>
                {metadata && (
                  <p className="text-sm text-muted-foreground">
                    Protection Target: {formatCurrency(metadata.protection_target)}
                  </p>
                )}
              </div>
              
              <div className="space-y-3">
                <Label>Financing Percentage</Label>
                <RadioGroup
                  value={financingPercentage || '0.5'}
                  onValueChange={(value) => {
                    // Ensure only valid values are set
                    const validValue = value === '0.5' || value === '0.75' || value === '1' ? value : '0.5';
                    setFinancingPercentage(validValue);
                  }}
                  className="space-y-2"
                >
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="0.5" id="finance-50" />
                    <Label htmlFor="finance-50" className="cursor-pointer font-normal">50%</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="0.75" id="finance-75" />
                    <Label htmlFor="finance-75" className="cursor-pointer font-normal">75%</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <RadioGroupItem value="1" id="finance-100" />
                    <Label htmlFor="finance-100" className="cursor-pointer font-normal">100% (Zero Cost)</Label>
                  </div>
                </RadioGroup>
              </div>
            </div>
          </CardContent>
        </Card>
        
        {/* Strategy Parameters */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Strategy Parameters</CardTitle>
            <CardDescription>Configure put and call selection criteria</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
              <div className="space-y-2">
                <Label>Underlying</Label>
                <Select value={selectedUnderlying} onValueChange={setSelectedUnderlying}>
                  <SelectTrigger>
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
              
              <div className="space-y-2">
                <Label>Put Delta Min</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={putDeltaMin}
                  onChange={(e) => setPutDeltaMin(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Put Delta Max</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={putDeltaMax}
                  onChange={(e) => setPutDeltaMax(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Call Delta</Label>
                <Input
                  type="number"
                  step="0.01"
                  value={callDelta}
                  onChange={(e) => setCallDelta(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Put Min Days</Label>
                <Input
                  type="number"
                  value={putMinDays}
                  onChange={(e) => setPutMinDays(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Put Max Days</Label>
                <Input
                  type="number"
                  value={putMaxDays}
                  onChange={(e) => setPutMaxDays(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Call Min Days</Label>
                <Input
                  type="number"
                  value={callMinDays}
                  onChange={(e) => setCallMinDays(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Call Max Days</Label>
                <Input
                  type="number"
                  value={callMaxDays}
                  onChange={(e) => setCallMaxDays(e.target.value)}
                />
              </div>
              
              <div className="space-y-2">
                <Label>Min Maturity Diff</Label>
                <Input
                  type="number"
                  value={minMaturityDiff}
                  onChange={(e) => setMinMaturityDiff(e.target.value)}
                />
              </div>
            </div>
            
            <Button onClick={fetchStrategies} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Calculating...
                </>
              ) : (
                'Calculate Strategies'
              )}
            </Button>
          </CardContent>
        </Card>
        
        {/* Results */}
        {metadata && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Spot Price</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(metadata.spot_price)}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Portfolio Value</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(metadata.portfolio_value_usd)}</div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Protection Target</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(metadata.protection_target)}</div>
                <div className="text-xs text-muted-foreground">
                  {(metadata.portfolio_hedge_percentage * 100).toFixed(0)}% hedge
                </div>
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
          </div>
        )}
        
        {strategies.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Available Strategies</CardTitle>
              <CardDescription>
                Strategies sorted by net cost (lowest first)
              </CardDescription>
            </CardHeader>
            <CardContent>
              {renderStrategyTable()}
            </CardContent>
          </Card>
        )}
      </div>
    </div>
    );
}

