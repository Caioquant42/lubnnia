'use client';

import * as echarts from 'echarts';
import { useEffect, useRef } from 'react';

import { AnalyzedRecommendation } from '__api__/recommendationsApi';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

type RecommendationCountType = {
  [key: string]: number;
};

interface TranslationsType {
  title?: string;
  tooltipTitle?: string;
  keys?: {
    [key: string]: string;
  };
}

interface RecommendationsPieChartProps {
  data: AnalyzedRecommendation[];
  className?: string;
  translations?: TranslationsType;
}

export function RecommendationsPieChart({
  data,
  className,
  translations,
}: RecommendationsPieChartProps) {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data || data.length === 0) return;

    // Count recommendations by recommendationKey
    const recommendationCounts: RecommendationCountType = data.reduce(
      (acc, item) => {
        const key = item.recommendationKey || 'Unknown';
        acc[key] = (acc[key] || 0) + 1;
        return acc;
      },
      {} as RecommendationCountType
    );

    // Transform for ECharts
    const chartData = Object.entries(recommendationCounts).map(
      ([name, value]) => {
        // If translations are provided, translate the category names
        const translatedName = translations?.keys?.[name] || name;
        return { name, translatedName, value };
      }
    );

    // Define colors for different recommendation types with improved vibrant color scheme
    const colorMap: { [key: string]: string } = {
      strong_buy: '#059669', // Rich emerald green - more professional and distinct
      buy: '#10b981', // Vibrant emerald green - clear and attractive
      hold: '#f59e0b', // Warm amber - neutral but not alarming
      sell: '#ef4444', // Clean red - clear sell signal
      strong_sell: '#dc2626', // Strong red - clear strong sell signal
      underperform: '#f97316', // Orange - distinct from strong sell
      none: '#6b7280', // Neutral gray
      Unknown: '#9ca3af', // Light gray
    };

    // Initialize chart
    const chart = echarts.init(chartRef.current);

    // Set chart options with improved typography and white captions
    const option = {
      title: {
        text: translations?.title || 'Analyst Recommendations Distribution',
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
        trigger: 'item',
        formatter: (params: any) => {
          const tooltipTitle =
            translations?.tooltipTitle || 'Recommendation Type';
          const name = translations?.keys?.[params.name] || params.name;
          return `${tooltipTitle} <br/>${name}: ${params.value} (${params.percent}%)`;
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
        extraCssText: 'box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);',
      },
      legend: {
        orient: 'vertical',
        left: 10,
        top: 'middle',
        itemWidth: 16,
        itemHeight: 12,
        itemGap: 12,
        formatter: (name: string) => translations?.keys?.[name] || name,
        textStyle: {
          fontSize: 13,
          color: '#475569',
          fontFamily: 'system-ui, -apple-system, sans-serif',
          fontWeight: 'normal',
        },
        data: chartData.map((item) => item.name),
      },
      series: [
        {
          name: translations?.tooltipTitle || 'Recommendation Type',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['60%', '55%'],
          avoidLabelOverlap: true,
          itemStyle: {
            borderRadius: 4,
            borderColor: '#fff',
            borderWidth: 1,
          },
          data: chartData.map((item) => ({
            name: item.name,
            value: item.value,
            itemStyle: {
              color: colorMap[item.name.toLowerCase()] || '#94a3b8',
            },
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 5,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.3)',
            },
            label: {
              show: true,
              fontSize: 14,
              fontWeight: '500',
              fontFamily: 'system-ui, -apple-system, sans-serif',
              color: '#ffffff',
              formatter: (params: any) =>
                translations?.keys?.[params.name] || params.name,
            },
          },
          label: {
            formatter: (params: any) => {
              const name = translations?.keys?.[params.name] || params.name;
              return `${name}: ${params.value} (${params.percent}%)`;
            },
            fontSize: 13,
            fontFamily: 'system-ui, -apple-system, sans-serif',
            color: '#ffffff',
            textShadow: '0 1px 2px rgba(0, 0, 0, 0.5)',
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
  }, [data, translations]);

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>
          {translations?.title || 'Analyst Recommendations'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div ref={chartRef} style={{ width: '100%', height: '380px' }} />
      </CardContent>
    </Card>
  );
}
