'use client';

import * as echarts from 'echarts';
import { useEffect, useRef } from 'react';

import { AnalyzedRecommendation } from '__api__/recommendationsApi';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

interface RecommendationsBarChartProps {
  data: (AnalyzedRecommendation | any)[];
  className?: string;
  title?: string;
  type?: 'return' | 'price' | 'analysts';
}

export function RecommendationsBarChart({
  data,
  className,
  title = 'Análise de Dados',
  type = 'return',
}: RecommendationsBarChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return;

    let chartData: any[] = [];
    let xAxisLabel = '';
    let yAxisLabel = '';

    switch (type) {
      case 'return':
        // Top 10 stocks by expected return
        chartData = data
          .filter((item) => typeof item.return_target_consensus === 'number')
          .sort(
            (a, b) =>
              (b.return_target_consensus || 0) -
              (a.return_target_consensus || 0)
          )
          .slice(0, 10)
          .map((item) => ({
            name: item.ticker || item.symbol || 'N/A',
            value: (item.return_target_consensus || 0) * 100,
            color:
              (item.return_target_consensus || 0) > 0 ? '#10b981' : '#ef4444',
          }));
        xAxisLabel = 'Ticker';
        yAxisLabel = 'Retorno Esperado (%)';
        break;

      case 'price':
        // Top 10 stocks by price target vs current price ratio
        chartData = data
          .filter((item) => item.currentPrice && item.targetMedianPrice)
          .map((item) => {
            const ratio =
              (item.targetMedianPrice / item.currentPrice - 1) * 100;
            return {
              name: item.ticker || item.symbol || 'N/A',
              value: ratio,
              color: ratio > 0 ? '#10b981' : '#ef4444',
            };
          })
          .sort((a, b) => b.value - a.value)
          .slice(0, 10);
        xAxisLabel = 'Ticker';
        yAxisLabel = 'Potencial de Valorização (%)';
        break;

      case 'analysts':
        // Top 10 stocks by number of analysts
        chartData = data
          .filter((item) => item.numberOfAnalystOpinions)
          .sort(
            (a, b) =>
              (b.numberOfAnalystOpinions || 0) -
              (a.numberOfAnalystOpinions || 0)
          )
          .slice(0, 10)
          .map((item) => ({
            name: item.ticker || item.symbol || 'N/A',
            value: item.numberOfAnalystOpinions || 0,
            color: '#3b82f6',
          }));
        xAxisLabel = 'Ticker';
        yAxisLabel = 'Número de Analistas';
        break;
    }

    if (chartData.length === 0) return;

    // Initialize chart
    const chart = echarts.init(chartRef.current);

    // Set chart options
    const option = {
      title: {
        text: title,
        left: 'center',
        top: 10,
        textStyle: {
          fontSize: 16,
          fontWeight: '500',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          color: '#1e293b',
        },
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        formatter: (params: any) => {
          const data = params[0];
          return `${data.name}<br/>${yAxisLabel}: ${data.value.toFixed(2)}`;
        },
        backgroundColor: 'rgba(0, 0, 0, 0.75)',
        borderColor: '#2d3748',
        borderWidth: 1,
        padding: [8, 12],
        textStyle: {
          color: '#ffffff',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontSize: 13,
          fontWeight: 'normal',
        },
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '20%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: chartData.map((item) => item.name),
        axisLabel: {
          rotate: 45,
          fontSize: 11,
          color: '#475569',
        },
        axisLine: {
          lineStyle: {
            color: '#e2e8f0',
          },
        },
      },
      yAxis: {
        type: 'value',
        name: yAxisLabel,
        nameTextStyle: {
          color: '#475569',
          fontSize: 12,
        },
        axisLabel: {
          fontSize: 11,
          color: '#475569',
        },
        axisLine: {
          lineStyle: {
            color: '#e2e8f0',
          },
        },
        splitLine: {
          lineStyle: {
            color: '#f1f5f9',
          },
        },
      },
      series: [
        {
          name: yAxisLabel,
          type: 'bar',
          data: chartData.map((item) => ({
            value: item.value,
            itemStyle: {
              color: item.color,
              borderRadius: [4, 4, 0, 0],
            },
          })),
          barWidth: '60%',
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.3)',
            },
          },
          label: {
            show: true,
            position: 'top',
            fontSize: 10,
            color: '#475569',
            formatter: (params: any) => params.value.toFixed(1),
          },
        },
      ],
    };

    chart.setOption(option);

    // Responsive handling
    const handleResize = () => {
      chart.resize();
    };

    window.addEventListener('resize', handleResize);

    return () => {
      chart.dispose();
      window.removeEventListener('resize', handleResize);
    };
  }, [data, type, title]);

  if (!data || data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>{title}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className='h-[300px] flex items-center justify-center text-muted-foreground'>
            Nenhum dado disponível para visualização
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <div ref={chartRef} style={{ width: '100%', height: '300px' }} />
      </CardContent>
    </Card>
  );
}
