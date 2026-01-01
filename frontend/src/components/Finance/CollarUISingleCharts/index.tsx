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
  ReferenceLine,
  Area,
  AreaChart,
} from "recharts";
import { CollarUISingleResponse } from "__api__/collarUIApi";
import { useMemo } from "react";

interface CollarUISingleChartsProps {
  data: CollarUISingleResponse;
}

export function CollarUISingleCharts({ data }: CollarUISingleChartsProps) {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;

  // Prepare histogram data
  const histogramData = useMemo(() => {
    const payoffs = data.payoffs;
    const minPayoff = Math.min(...payoffs);
    const maxPayoff = Math.max(...payoffs);
    const bins = 50;
    const binWidth = (maxPayoff - minPayoff) / bins;

    const binsData: { [key: number]: number } = {};

    payoffs.forEach((payoff) => {
      const binIndex = Math.floor((payoff - minPayoff) / binWidth);
      const binKey = Math.min(binIndex, bins - 1);
      if (!binsData[binKey]) {
        binsData[binKey] = 0;
      }
      binsData[binKey]++;
    });

    return Object.entries(binsData).map(([bin, count], idx) => ({
      bin: idx.toString(),
      count,
      label: formatPercent(minPayoff + parseInt(bin) * binWidth),
    }));
  }, [data]);

  // Prepare CDF data
  const cdfData = useMemo(() => {
    const sorted = [...data.payoffs].sort((a, b) => a - b);
    const n = sorted.length;

    // Sample points for CDF
    const minVal = Math.min(...sorted);
    const maxVal = Math.max(...sorted);
    const points = 100;
    const step = (maxVal - minVal) / points;

    return Array.from({ length: points + 1 }, (_, i) => {
      const val = minVal + i * step;
      const prob = sorted.filter((p) => p <= val).length / n;
      return {
        value: val * 100,
        probability: prob,
      };
    });
  }, [data]);

  // Prepare paths data (sample a subset for visualization)
  const pathsData = useMemo(() => {
    const maxPathsToShow = 200;
    const pathsToShow = Math.min(data.paths.length, maxPathsToShow);
    const sampledPaths = data.paths.slice(0, pathsToShow);
    
    // Convert paths to chart format
    const days = data.paths[0]?.length || 0;
    const chartData = Array.from({ length: days }, (_, dayIndex) => {
      const dayData: { day: number; [key: string]: number | string } = { day: dayIndex };
      
      // Sample a few paths for visualization
      sampledPaths.forEach((path, pathIndex) => {
        if (pathIndex < 20) { // Show only first 20 paths to avoid clutter
          dayData[`path${pathIndex}`] = path[dayIndex];
        }
      });
      
      // Add reference levels
      dayData.S0 = data.params.S0;
      dayData.barrier = data.params.S0 * data.params.barreira_ativacao;
      dayData.strikePut = data.params.S0 * data.params.strike_put;
      dayData.strikeCall = data.params.S0 * data.params.strike_call;
      
      return dayData;
    });
    
    return chartData;
  }, [data]);

  // Box plot data (simplified - showing min, Q1, median, Q3, max)
  const boxPlotData = [
    {
      name: "Payoff Distribution",
      min: data.statistics.payoff_min * 100,
      q1: data.additional_metrics.percentis[25] * 100,
      median: data.additional_metrics.percentis[50] * 100,
      q3: data.additional_metrics.percentis[75] * 100,
      max: data.statistics.payoff_max * 100,
    },
  ];

  // Scenario probabilities data
  const scenarioData = [
    {
      scenario: "Perda",
      value: data.statistics.pct_perda,
    },
    {
      scenario: "Ganho\n(sem barreira)",
      value: data.statistics.pct_ganho_sem_barreira,
    },
    {
      scenario: "Ganho\n(barreira ativada)",
      value: data.statistics.pct_ganho_com_barreira,
    },
  ];

  return (
    <div className="space-y-6">
      {/* Price Paths */}
      <Card>
        <CardHeader>
          <CardTitle>Caminhos de Preço Simulados</CardTitle>
          <CardDescription>
            Trajetórias de preço simuladas usando Moving Block Bootstrap (mostrando até 20 caminhos)
          </CardDescription>
        </CardHeader>
        <CardContent className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={pathsData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis 
                dataKey="day" 
                label={{ value: "Dias Úteis", position: "insideBottom", offset: -10 }}
              />
              <YAxis 
                label={{ value: "Preço (R$)", angle: -90, position: "insideLeft" }}
              />
              <Tooltip />
              <Legend />
              <ReferenceLine 
                y={data.params.S0} 
                stroke="#000" 
                strokeDasharray="3 3" 
                label="S0"
              />
              <ReferenceLine 
                y={data.params.S0 * data.params.barreira_ativacao} 
                stroke="#f97316" 
                strokeDasharray="3 3" 
                label="Barreira"
              />
              <ReferenceLine 
                y={data.params.S0 * data.params.strike_put} 
                stroke="#ef4444" 
                strokeDasharray="3 3" 
                label="Strike Put"
              />
              <ReferenceLine 
                y={data.params.S0 * data.params.strike_call} 
                stroke="#3b82f6" 
                strokeDasharray="3 3" 
                label="Strike Call"
              />
              {Array.from({ length: Math.min(20, data.paths.length) }, (_, i) => (
                <Line
                  key={i}
                  type="monotone"
                  dataKey={`path${i}`}
                  stroke="#8884d8"
                  strokeWidth={0.5}
                  dot={false}
                  opacity={0.3}
                  connectNulls
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Histogram */}
      <Card>
        <CardHeader>
          <CardTitle>Distribuição de Payoffs</CardTitle>
          <CardDescription>Histograma da distribuição de payoffs</CardDescription>
        </CardHeader>
        <CardContent className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={histogramData.slice(0, 50)}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="bin" hide />
              <YAxis />
              <Tooltip formatter={(value: number) => value} />
              <Legend />
              <ReferenceLine x={0} stroke="#666" strokeDasharray="3 3" />
              <ReferenceLine 
                y={data.statistics.payoff_medio * 100} 
                stroke="#3b82f6" 
                strokeDasharray="3 3" 
                label="Média"
              />
              <ReferenceLine 
                y={data.statistics.payoff_mediano * 100} 
                stroke="#22c55e" 
                strokeDasharray="3 3" 
                label="Mediana"
              />
              <Bar dataKey="count" fill="#3b82f6" opacity={0.6} name="Frequência" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Box Plot - Simplified using bar chart */}
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

      {/* CDF */}
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
                dataKey="probability"
                stroke="#3b82f6"
                strokeWidth={2}
                name="Probabilidade Cumulativa"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Scenario Probabilities */}
      <Card>
        <CardHeader>
          <CardTitle>Probabilidades de Cenários</CardTitle>
          <CardDescription>Distribuição percentual dos cenários</CardDescription>
        </CardHeader>
        <CardContent className="h-[300px]">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={scenarioData}>
              <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
              <XAxis dataKey="scenario" />
              <YAxis tickFormatter={(value) => `${value}%`} />
              <Tooltip formatter={(value: number) => `${value.toFixed(2)}%`} />
              <Legend />
              <Bar dataKey="value" fill="#3b82f6" name="Probabilidade (%)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}



