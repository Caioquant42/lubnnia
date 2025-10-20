import React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis, Cell, Legend } from "recharts";

type VolatilityDistribution = {
  name: string;
  value: number;
  color: string;
};

type VolatilityDistributionChartProps = {
  distribution: Record<string, number>;
  title: string;
  description?: string;
};

export default function VolatilityDistributionChart({
  distribution,
  title,
  description,
}: VolatilityDistributionChartProps) {
  // Map distribution to chart data with improved color scheme
  const chartData: VolatilityDistribution[] = [
    {
      name: "Extremamente Baixa",
      value: distribution["Extremamente Baixa"] || 0,
      color: "#1e40af", // blue-700 - darker blue for very low volatility
    },
    {
      name: "Muito Baixa",
      value: distribution["Muito Baixa"] || 0,
      color: "#3b82f6", // blue-500
    },
    {
      name: "Baixa",
      value: distribution["Baixa"] || 0,
      color: "#06b6d4", // cyan-500
    },
    {
      name: "Neutra",
      value: distribution["Neutra"] || 0,
      color: "#10b981", // green-500
    },
    {
      name: "Alta",
      value: distribution["Alta"] || 0,
      color: "#f59e0b", // amber-500
    },
    {
      name: "Muito Alta",
      value: distribution["Muito Alta"] || 0,
      color: "#f97316", // orange-500
    },
    {
      name: "Extremamente Alta",
      value: distribution["Extremamente Alta"] || 0,
      color: "#dc2626", // red-600 - darker red for very high volatility
    },
  ];

  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const total = chartData.reduce((sum, item) => sum + item.value, 0);
      const percentage = total > 0 ? ((payload[0].value / total) * 100).toFixed(1) : 0;
      
      return (
        <div className="bg-background p-3 border rounded-md shadow-lg">
          <p className="font-medium text-sm">{`Volatilidade ${label}`}</p>
          <p className="text-sm text-muted-foreground">{`Quantidade: ${payload[0].value} ações`}</p>
          <p className="text-sm text-muted-foreground">{`Percentual: ${percentage}%`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>{title}</CardTitle>
        {description && <CardDescription>{description}</CardDescription>}
      </CardHeader>
      <CardContent>
        <div className="h-[350px] w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 80 }}>
              <XAxis
                dataKey="name"
                tickLine={false}
                axisLine={false}
                fontSize={11}
                angle={-45}
                textAnchor="end"
                height={80}
                tick={{ fill: '#6b7280' }}
              />
                              <YAxis
                  tickLine={false}
                  axisLine={false}
                  fontSize={11}
                  tick={{ fill: '#6b7280' }}
                  label={{ value: 'Número de Ações', angle: -90, position: 'insideLeft', offset: 0 }}
                />
              <Tooltip content={<CustomTooltip />} />
              <Legend 
                verticalAlign="top" 
                height={36}
                wrapperStyle={{ paddingBottom: '10px' }}
              />
              <Bar
                dataKey="value"
                radius={[6, 6, 0, 0]}
                strokeWidth={1}
                stroke="rgba(0,0,0,0.1)"
                name="Ações"
              >
                {chartData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary Statistics */}
        <div className="mt-4 pt-4 border-t">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div className="text-center">
                <div className="font-semibold text-blue-600">
                  {chartData.slice(0, 3).reduce((sum, item) => sum + item.value, 0)}
                </div>
                <div className="text-muted-foreground">Baixa Volatilidade</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-green-600">
                  {chartData[3]?.value || 0}
                </div>
                <div className="text-muted-foreground">Neutra</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-orange-600">
                  {chartData.slice(4, 6).reduce((sum, item) => sum + item.value, 0)}
                </div>
                <div className="text-muted-foreground">Alta Volatilidade</div>
              </div>
              <div className="text-center">
                <div className="font-semibold text-red-600">
                  {chartData[6]?.value || 0}
                </div>
                <div className="text-muted-foreground">Extremamente Alta</div>
              </div>
            </div>
        </div>
      </CardContent>
    </Card>
  );
}