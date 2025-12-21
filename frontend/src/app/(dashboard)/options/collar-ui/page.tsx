"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/components/ui/use-toast";
import { getCollarUIData, CollarUIResponse } from "__api__/collarUIApi";
import { Loader2, TrendingUp, Shield, Target } from "lucide-react";
import { Area, AreaChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

type ScenarioKey = "downside" | "normal_upside" | "knockout_scenario2" | "knockout_scenario1";

export default function CollarUIPage() {
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<CollarUIResponse | null>(null);

  const [ticker, setTicker] = useState("VALE3");
  const [S0, setS0] = useState<string>("");
  const [ttm, setTtm] = useState("93");
  const [maxLoss, setMaxLoss] = useState("-0.05");
  const [thresholdPct, setThresholdPct] = useState("0.1346");
  const [limitedGain, setLimitedGain] = useState("0.048");
  const [nBootstrap, setNBootstrap] = useState("1000");
  const [iterations, setIterations] = useState("50000");

  const handleCalculate = async () => {
    try {
      setLoading(true);
      const params = {
        ticker,
        ttm: parseInt(ttm),
        max_loss: parseFloat(maxLoss),
        threshold_percentage: parseFloat(thresholdPct),
        limited_gain: parseFloat(limitedGain),
        n_bootstrap: parseInt(nBootstrap),
        iterations: parseInt(iterations),
      } as any;
      if (S0) params.S0 = parseFloat(S0);

      const res = await getCollarUIData(params);
      setData(res);
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error?.response?.data?.error || "Falha ao calcular Collar UI",
        variant: "destructive",
      });
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const payoffChartData =
    data?.payoff_distribution.slice(0, 5000).map((p, idx) => ({
      idx,
      payoff: p,
    })) || [];

  const scenarioColors: Record<ScenarioKey, string> = {
    downside: "#EF4444",
    normal_upside: "#22C55E",
    knockout_scenario2: "#F97316",
    knockout_scenario1: "#6366F1",
  };

  const formatCurrency = (v: number) =>
    v?.toLocaleString("pt-BR", { style: "currency", currency: "BRL", maximumFractionDigits: 2 });

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="mb-4">
        <h1 className="text-3xl font-bold tracking-tight">Collar Up & In (MBB)</h1>
        <p className="text-muted-foreground">
          Análise da estratégia Collar Up & In utilizando Moving Block Bootstrap e Monte Carlo.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Parâmetros</CardTitle>
          <CardDescription>Defina os parâmetros da estrutura</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Ativo</Label>
              <Input value={ticker} onChange={(e) => setTicker(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Preço de Referência (S0) opcional</Label>
              <Input value={S0} onChange={(e) => setS0(e.target.value)} placeholder="ex: 63.5" />
            </div>
            <div className="space-y-2">
              <Label>Dias úteis até vencimento (ttm)</Label>
              <Input type="number" value={ttm} onChange={(e) => setTtm(e.target.value)} />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Perda máxima (ex: -0.05)</Label>
              <Input value={maxLoss} onChange={(e) => setMaxLoss(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Barreira knockout (% acima S0, ex: 0.1346)</Label>
              <Input value={thresholdPct} onChange={(e) => setThresholdPct(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Ganho limitado (ex: 0.048)</Label>
              <Input value={limitedGain} onChange={(e) => setLimitedGain(e.target.value)} />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label>Bootstrap samples</Label>
              <Input type="number" value={nBootstrap} onChange={(e) => setNBootstrap(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label>Monte Carlo iterations</Label>
              <Input type="number" value={iterations} onChange={(e) => setIterations(e.target.value)} />
            </div>
          </div>

          <Button onClick={handleCalculate} disabled={loading}>
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Calculando...
              </>
            ) : (
              "Calcular"
            )}
          </Button>
        </CardContent>
      </Card>

      {data && (
        <>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <TrendingUp className="h-4 w-4" /> Valor Esperado
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(data.statistics.expected_value)}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Shield className="h-4 w-4" /> Perda Máxima
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(data.metadata.perda_maxima)}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Target className="h-4 w-4" /> Barreira Knockout
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{formatCurrency(data.metadata.barreira_knockout)}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium">Amostras / Iterações</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {data.metadata.n_bootstrap} / {data.metadata.iterations}
                </div>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Distribuição de Payoffs</CardTitle>
              <CardDescription>Payoffs simulados (amostra)</CardDescription>
            </CardHeader>
            <CardContent className="h-[320px]">
              {payoffChartData.length === 0 ? (
                <div className="flex h-full items-center justify-center text-muted-foreground">
                  Nenhum dado para exibir
                </div>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={payoffChartData}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
                    <XAxis dataKey="idx" hide />
                    <YAxis />
                    <Tooltip formatter={(v) => formatCurrency(Number(v))} />
                    <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
                    <Area dataKey="payoff" stroke="#2563EB" fill="#60A5FA" fillOpacity={0.4} />
                  </AreaChart>
                </ResponsiveContainer>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Distribuição de Cenários</CardTitle>
              <CardDescription>Contagem e porcentagem</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {(["downside", "normal_upside", "knockout_scenario2", "knockout_scenario1"] as ScenarioKey[]).map(
                (k) => (
                  <div key={k} className="flex items-center justify-between rounded-md border p-2">
                    <div className="flex items-center gap-2">
                      <div className="h-3 w-3 rounded-full" style={{ backgroundColor: scenarioColors[k] }} />
                      <span className="capitalize">
                        {k.replace("_", " ")}
                      </span>
                    </div>
                    <div className="text-sm text-muted-foreground">
                      {data.scenarios[k]} ({data.scenario_percentages[k].toFixed(2)}%)
                    </div>
                  </div>
                )
              )}
            </CardContent>
          </Card>
        </>
      )}
    </div>
  );
}


