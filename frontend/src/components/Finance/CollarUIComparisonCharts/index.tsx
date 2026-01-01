"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  LineChart,
  Line,
  ScatterChart,
  Scatter,
  ReferenceLine,
  Area,
  AreaChart,
} from "recharts";
import { CollarUIComparisonResponse } from "__api__/collarUIApi";
import { useMemo } from "react";

interface CollarUIComparisonChartsProps {
  data: CollarUIComparisonResponse;
}

export function CollarUIComparisonCharts({ data }: CollarUIComparisonChartsProps) {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;

  // Prepare histogram data
  const histogramData = useMemo(() => {
    const payoffsA = data.structure_A.payoffs;
    const payoffsB = data.structure_B.payoffs;
    const minPayoff = Math.min(...payoffsA, ...payoffsB);
    const maxPayoff = Math.max(...payoffsA, ...payoffsB);
    const bins = 50;
    const binWidth = (maxPayoff - minPayoff) / bins;

    const binsData: { [key: number]: { A: number; B: number; bin: string } } = {};

    payoffsA.forEach((payoff) => {
      const binIndex = Math.floor((payoff - minPayoff) / binWidth);
      const binKey = Math.min(binIndex, bins - 1);
      if (!binsData[binKey]) {
        binsData[binKey] = { A: 0, B: 0, bin: formatPercent(minPayoff + binKey * binWidth) };
      }
      binsData[binKey].A++;
    });

    payoffsB.forEach((payoff) => {
      const binIndex = Math.floor((payoff - minPayoff) / binWidth);
      const binKey = Math.min(binIndex, bins - 1);
      if (!binsData[binKey]) {
        binsData[binKey] = { A: 0, B: 0, bin: formatPercent(minPayoff + binKey * binWidth) };
      }
      binsData[binKey].B++;
    });

    return Object.values(binsData).map((bin, idx) => ({
      bin: idx.toString(),
      A: bin.A,
      B: bin.B,
      label: bin.bin,
    }));
  }, [data]);

  // Prepare CDF data
  const cdfData = useMemo(() => {
    const sortedA = [...data.structure_A.payoffs].sort((a, b) => a - b);
    const sortedB = [...data.structure_B.payoffs].sort((a, b) => a - b);
    const nA = sortedA.length;
    const nB = sortedB.length;

    // Sample points for CDF
    const minVal = Math.min(...sortedA, ...sortedB);
    const maxVal = Math.max(...sortedA, ...sortedB);
    const points = 100;
    const step = (maxVal - minVal) / points;

    return Array.from({ length: points + 1 }, (_, i) => {
      const val = minVal + i * step;
      const probA = sortedA.filter((p) => p <= val).length / nA;
      const probB = sortedB.filter((p) => p <= val).length / nB;
      return {
        value: val * 100,
        A: probA,
        B: probB,
      };
    });
  }, [data]);

  // Box plot data (simplified - showing min, Q1, median, Q3, max)
  const boxPlotData = [
    {
      name: "Estrutura A",
      min: data.structure_A.statistics.payoff_min * 100,
      q1: data.comparison_metrics.percentis.A[25] * 100,
      median: data.comparison_metrics.percentis.A[50] * 100,
      q3: data.comparison_metrics.percentis.A[75] * 100,
      max: data.structure_A.statistics.payoff_max * 100,
    },
    {
      name: "Estrutura B",
      min: data.structure_B.statistics.payoff_min * 100,
      q1: data.comparison_metrics.percentis.B[25] * 100,
      median: data.comparison_metrics.percentis.B[50] * 100,
      q3: data.comparison_metrics.percentis.B[75] * 100,
      max: data.structure_B.statistics.payoff_max * 100,
    },
  ];

  // Scenario probabilities data
  const scenarioData = [
    {
      scenario: "Perda",
      A: data.comparison_metrics.prob_perda.A * 100,
      B: data.comparison_metrics.prob_perda.B * 100,
    },
    {
      scenario: "Ganho\n(sem barreira)",
      A: data.comparison_metrics.prob_ganho_sem_barreira.A * 100,
      B: data.comparison_metrics.prob_ganho_sem_barreira.B * 100,
    },
    {
      scenario: "Ganho\n(barreira ativada)",
      A: data.comparison_metrics.prob_ganho_com_barreira.A * 100,
      B: data.comparison_metrics.prob_ganho_com_barreira.B * 100,
    },
  ];

  // Risk-return scatter data
  const riskReturnData = [
    {
      risk: data.comparison_metrics.std.A * 100,
      return: data.comparison_metrics.expected_return.A * 100,
      structure: "A",
    },
    {
      risk: data.comparison_metrics.std.B * 100,
      return: data.comparison_metrics.expected_return.B * 100,
      structure: "B",
    },
  ];

  return (
    <div className="space-y-6">
      {/* Histogram Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Distribuição Comparativa de Payoffs</CardTitle>
          <CardDescription>Histograma comparativo das distribuições de payoffs</CardDescription>
        </CardHeader>
        <CardContent className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={histogramData.slice(0, 50)}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="bin" hide />
              <YAxis />
              <Tooltip />
              <Legend />
              <ReferenceLine x={0} stroke="#666" strokeDasharray="3 3" />
              <Bar dataKey="A" fill="#3b82f6" opacity={0.6} name="Estrutura A" />
              <Bar dataKey="B" fill="#f97316" opacity={0.6} name="Estrutura B" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Box Plot Comparison - Simplified using area chart */}
      <Card>
        <CardHeader>
          <CardTitle>Distribuição de Payoffs (Estatísticas)</CardTitle>
          <CardDescription>Mínimo, Q1, Mediana, Q3, Máximo</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={boxPlotData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="name" />
              <YAxis tickFormatter={(value) => formatPercent(value / 100)} />
              <Tooltip formatter={(value: number) => formatPercent(value / 100)} />
              <Legend />
              <ReferenceLine y={0} stroke="#666" strokeDasharray="3 3" />
              <Bar dataKey="min" fill="#ef4444" name="Mínimo" />
              <Bar dataKey="q1" fill="#f97316" name="Q1" />
              <Bar dataKey="median" fill="#3b82f6" name="Mediana" />
              <Bar dataKey="q3" fill="#22c55e" name="Q3" />
              <Bar dataKey="max" fill="#10b981" name="Máximo" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* CDF Comparison */}
      <Card>
        <CardHeader>
          <CardTitle>Função de Distribuição Cumulativa (CDF)</CardTitle>
          <CardDescription>Probabilidade cumulativa de payoffs</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={cdfData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis
                dataKey="value"
                tickFormatter={(value) => formatPercent(value / 100)}
                label={{ value: "Payoff (%)", position: "insideBottom", offset: -10 }}
              />
              <YAxis
                label={{ value: "Probabilidade Cumulativa", angle: -90, position: "insideLeft" }}
              />
              <Tooltip
                formatter={(value: number) => `${(value * 100).toFixed(2)}%`}
                labelFormatter={(label) => `Payoff: ${formatPercent(Number(label) / 100)}`}
              />
              <Legend />
              <ReferenceLine x={0} stroke="#666" strokeDasharray="3 3" />
              <Line
                type="monotone"
                dataKey="A"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Estrutura A"
                dot={false}
              />
              <Line
                type="monotone"
                dataKey="B"
                stroke="#f97316"
                strokeWidth={2}
                name="Estrutura B"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Risk-Return Scatter */}
      <Card>
        <CardHeader>
          <CardTitle>Retorno vs Risco</CardTitle>
          <CardDescription>Análise de retorno esperado versus desvio padrão</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <ScatterChart>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis
                type="number"
                dataKey="risk"
                name="Risco"
                label={{ value: "Risco (Desvio Padrão %)", position: "insideBottom", offset: -10 }}
                tickFormatter={(value) => formatPercent(value / 100)}
              />
              <YAxis
                type="number"
                dataKey="return"
                name="Retorno"
                label={{ value: "Retorno Esperado (%)", angle: -90, position: "insideLeft" }}
                tickFormatter={(value) => formatPercent(value / 100)}
              />
              <Tooltip
                cursor={{ strokeDasharray: "3 3" }}
                formatter={(value: number) => formatPercent(value / 100)}
              />
              <Scatter
                name="Estrutura A"
                data={[riskReturnData[0]]}
                fill="#3b82f6"
              />
              <Scatter
                name="Estrutura B"
                data={[riskReturnData[1]]}
                fill="#f97316"
              />
            </ScatterChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Scenario Probabilities */}
      <Card>
        <CardHeader>
          <CardTitle>Probabilidades de Cenários</CardTitle>
          <CardDescription>Comparação das probabilidades de diferentes cenários</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scenarioData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="scenario" />
              <YAxis label={{ value: "Probabilidade (%)", angle: -90, position: "insideLeft" }} />
              <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
              <Legend />
              <Bar dataKey="A" fill="#3b82f6" name="Estrutura A" />
              <Bar dataKey="B" fill="#f97316" name="Estrutura B" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

