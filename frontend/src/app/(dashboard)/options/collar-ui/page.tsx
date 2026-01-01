"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/components/ui/use-toast";
import {
  getCollarUIComparison,
  CollarUIComparisonParams,
  CollarUIComparisonResponse,
  getCollarUISingle,
  CollarUISingleParams,
  CollarUISingleResponse,
} from "__api__/collarUIApi";
import { Loader2 } from "lucide-react";
import { CollarUIComparisonParams as ComparisonParamsComponent } from "@/components/Finance/CollarUIComparisonParams";
import { CollarUIComparisonTable } from "@/components/Finance/CollarUIComparisonTable";
import { CollarUIComparisonCharts } from "@/components/Finance/CollarUIComparisonCharts";
import { CollarUISingleParams as SingleParamsComponent } from "@/components/Finance/CollarUISingleParams";
import { CollarUISingleTable } from "@/components/Finance/CollarUISingleTable";
import { CollarUISingleCharts } from "@/components/Finance/CollarUISingleCharts";

export default function CollarUIPage() {
  const { toast } = useToast();
  const [comparisonData, setComparisonData] = useState<CollarUIComparisonResponse | null>(null);
  const [comparisonLoading, setComparisonLoading] = useState(false);
  const [singleData, setSingleData] = useState<CollarUISingleResponse | null>(null);
  const [singleLoading, setSingleLoading] = useState(false);

  // Comparison parameters
  const [comparisonParams, setComparisonParams] = useState<CollarUIComparisonParams>({
    ticker_A: "PETR4",
    S0_A: 38.50,
    strike_put_pct_A: 90.0,
    strike_call_pct_A: 107.5,
    expiration_date_A: "",
    barrier_pct_A: 144.0,
    ticker_B: "VALE3",
    S0_B: 63.50,
    strike_put_pct_B: 90.0,
    strike_call_pct_B: 107.5,
    expiration_date_B: "",
    barrier_pct_B: 144.0,
    n_bootstrap: 1000,
  });

  // Single view parameters
  const [singleParams, setSingleParams] = useState<CollarUISingleParams>({
    ticker: "PETR4",
    S0: 38.50,
    strike_put_pct: 90.0,
    strike_call_pct: 107.5,
    expiration_date: "",
    barrier_pct: 144.0,
    n_bootstrap: 1000,
  });

  const handleComparisonCalculate = async () => {
    try {
      setComparisonLoading(true);
      const res = await getCollarUIComparison(comparisonParams);
      setComparisonData(res);
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error?.response?.data?.error || "Falha ao calcular comparação",
        variant: "destructive",
      });
      console.error(error);
    } finally {
      setComparisonLoading(false);
    }
  };

  const handleSingleCalculate = async () => {
    try {
      setSingleLoading(true);
      const res = await getCollarUISingle(singleParams);
      setSingleData(res);
    } catch (error: any) {
      toast({
        title: "Erro",
        description: error?.response?.data?.error || "Falha ao calcular estrutura",
        variant: "destructive",
      });
      console.error(error);
    } finally {
      setSingleLoading(false);
    }
  };

  return (
    <div className="container mx-auto py-6 space-y-6">
      <div className="mb-4">
        <h1 className="text-3xl font-bold tracking-tight">Collar Up & In (MBB)</h1>
        <p className="text-muted-foreground">
          Analise estruturas Collar Up & In utilizando Moving Block Bootstrap e Monte Carlo.
        </p>
      </div>

      <Tabs defaultValue="single" className="w-full">
        <TabsList>
          <TabsTrigger value="single">Análise Individual</TabsTrigger>
          <TabsTrigger value="comparison">Comparação</TabsTrigger>
        </TabsList>

        <TabsContent value="single" className="space-y-6">
          <SingleParamsComponent
            params={singleParams}
            onChange={setSingleParams}
          />

          <Button onClick={handleSingleCalculate} disabled={singleLoading} className="w-full">
            {singleLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Calculando...
              </>
            ) : (
              "Calcular Estrutura"
            )}
          </Button>

          {singleData && (
            <>
              <CollarUISingleTable data={singleData} />
              <CollarUISingleCharts data={singleData} />
            </>
          )}
        </TabsContent>

        <TabsContent value="comparison" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <ComparisonParamsComponent
              params={comparisonParams}
              onChange={(params) => {
                setComparisonParams({ ...comparisonParams, ...params });
              }}
              structureLabel="A"
            />
            <ComparisonParamsComponent
              params={comparisonParams}
              onChange={(params) => {
                setComparisonParams({ ...comparisonParams, ...params });
              }}
              structureLabel="B"
            />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Parâmetros Compartilhados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label>Número de Caminhos Bootstrap</Label>
                  <Input
                    type="number"
                    value={comparisonParams.n_bootstrap || 1000}
                    onChange={(e) =>
                      setComparisonParams({
                        ...comparisonParams,
                        n_bootstrap: parseInt(e.target.value) || 1000,
                      })
                    }
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          <Button onClick={handleComparisonCalculate} disabled={comparisonLoading} className="w-full">
            {comparisonLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Calculando Comparação...
              </>
            ) : (
              "Calcular Comparação"
            )}
          </Button>

          {comparisonData && (
            <>
              <CollarUIComparisonTable data={comparisonData} />
              <CollarUIComparisonCharts data={comparisonData} />
            </>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
