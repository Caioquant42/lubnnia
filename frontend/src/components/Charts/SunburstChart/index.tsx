'use client';

import ReactECharts from 'echarts-for-react';
import React, { useMemo } from 'react';
import { getSectorMapping } from '@/utils/sectorMapping';

interface SunburstNode {
  name: string;
  value?: number;
  variation?: number;
  color?: string;
  fullName?: string;
  close?: number;
  sector?: string;
  children?: SunburstNode[];
}

interface SunburstChartProps {
  data: SunburstNode;
  width?: number;
  height?: number;
  className?: string;
  onSectorClick?: (sectorName: string) => void;
  selectedSector?: string | null;
}

const SunburstChart: React.FC<SunburstChartProps> = ({
  data,
  width = 600,
  height = 600,
  className = '',
  onSectorClick,
  selectedSector,
}) => {
  const getColorByVariation = (variation: number) => {
    const absVariation = Math.abs(variation);
    const intensity = Math.min(200, Math.round(absVariation * 20));

    if (variation > 0) {
      // Green for positive variations - adjusted for purple theme
      return `rgb(34, ${intensity + 55}, 34)`;
    } else if (variation < 0) {
      // Red for negative variations - adjusted for purple theme
      return `rgb(${intensity + 55}, 34, 34)`;
    } else {
      // Gray for neutral - adjusted for purple theme
      return `rgb(100, 100, 100)`;
    }
  };

  const processDataForECharts = (node: SunburstNode): any[] => {
    if (!node.children || node.children.length === 0) {
      return [];
    }

    // Filter to show only top sectors and limit the number of stocks per sector
    const topSectors = node.children
      .sort((a, b) => {
        const aValue =
          a.children?.reduce(
            (sum, child) => sum + Math.abs(child.variation || 0),
            0
          ) || 0;
        const bValue =
          b.children?.reduce(
            (sum, child) => sum + Math.abs(child.variation || 0),
            0
          ) || 0;
        return bValue - aValue;
      })
      .slice(0, 8); // Show only top 8 sectors

    return topSectors.map((sectorNode) => {
      const sectorMapping = getSectorMapping(sectorNode.name);
      const sectorDisplayName = `${sectorMapping.icon} ${sectorMapping.shortName}`;
      const isSelected = selectedSector === sectorNode.name;

      // Limit stocks per sector to top performers
      const topStocks =
        sectorNode.children
          ?.sort(
            (a, b) => Math.abs(b.variation || 0) - Math.abs(a.variation || 0)
          )
          .slice(0, 6) || []; // Show only top 6 stocks per sector

      return {
        name: sectorDisplayName,
        originalName: sectorNode.name,
        itemStyle: {
          borderWidth: isSelected ? 3 : 1,
          borderColor: isSelected ? '#8b5cf6' : '#4c1d95', // Purple theme colors
          shadowBlur: isSelected ? 15 : 0,
          shadowColor: isSelected ? 'rgba(139, 92, 246, 0.6)' : 'transparent',
        },
        children: topStocks.map((stockNode) => ({
          name: stockNode.name,
          value: Math.abs(stockNode.variation || 0),
          variation: stockNode.variation || 0,
          fullName: stockNode.fullName,
          close: stockNode.close,
          sector: sectorNode.name,
          itemStyle: {
            color: getColorByVariation(stockNode.variation || 0),
          },
        })),
      };
    });
  };

  const chartData = useMemo(() => {
    return processDataForECharts(data);
  }, [data, selectedSector]);

  const option = useMemo(
    () => ({
      backgroundColor: 'transparent',
      tooltip: {
        trigger: 'item',
        backgroundColor: 'rgba(30, 30, 30, 0.95)',
        borderColor: '#8b5cf6',
        borderWidth: 1,
        textStyle: {
          color: '#ffffff',
        },
        formatter: (params: any) => {
          if (params.data.variation !== undefined) {
            // Stock tooltip
            const value = params.data.variation.toFixed(2);
            const sign = params.data.variation >= 0 ? '+' : '';
            const color = params.data.variation >= 0 ? '#10b981' : '#ef4444';

            return `
            <div class="p-3">
              <div class="font-semibold text-sm mb-2 text-white">${params.name}</div>
              <div class="text-xs text-gray-300 mb-2">${params.data.fullName || ''}</div>
              <div class="flex justify-between items-center mb-1">
                <span class="text-xs text-gray-300">Variação:</span>
                <span style="color: ${color}; font-weight: bold;">${sign}${value}%</span>
              </div>
              ${
                params.data.close
                  ? `
                <div class="flex justify-between items-center mb-1">
                  <span class="text-xs text-gray-300">Preço:</span>
                  <span class="text-xs font-medium text-white">R$ ${params.data.close.toFixed(2)}</span>
                </div>
              `
                  : ''
              }
              <div class="text-xs text-gray-400 mt-2">Setor: ${params.data.sector || 'N/A'}</div>
            </div>
          `;
          } else {
            // Sector tooltip
            const originalName = params.data.originalName || params.name;
            const stockCount = params.data.children?.length || 0;
            const positiveStocks =
              params.data.children?.filter((s: any) => s.variation > 0)
                .length || 0;
            const negativeStocks =
              params.data.children?.filter((s: any) => s.variation < 0)
                .length || 0;

            return `
            <div class="p-3">
              <div class="font-semibold text-sm mb-2 text-white">${originalName}</div>
              <div class="text-xs text-gray-300 mb-2">${stockCount} ações</div>
              <div class="flex justify-between items-center text-xs mb-2">
                <span style="color: #10b981;">▲ ${positiveStocks}</span>
                <span style="color: #ef4444;">▼ ${negativeStocks}</span>
              </div>
              <div class="text-xs text-gray-400">Clique para detalhes</div>
            </div>
          `;
          }
        },
      },
      series: {
        type: 'sunburst',
        data: chartData,
        radius: [0, '90%'],
        sort: null,
        emphasis: {
          focus: 'ancestor',
          itemStyle: {
            shadowBlur: 15,
            shadowColor: 'rgba(139, 92, 246, 0.4)',
          },
        },
        levels: [
          {
            r0: '0%',
            r: '15%',
            itemStyle: {
              borderWidth: 2,
              borderColor: '#8b5cf6',
            },
            label: {
              show: true,
              fontSize: 14,
              color: '#ffffff',
              fontWeight: 'bold',
            },
          },
          {
            r0: '15%',
            r: '45%',
            itemStyle: {
              borderWidth: 2,
              borderColor: '#4c1d95',
            },
            label: {
              rotate: 'tangential',
              fontSize: width >= 400 ? 12 : 10,
              align: 'center',
              show: true,
              color: '#ffffff',
              fontWeight: 'medium',
            },
          },
          {
            r0: '45%',
            r: '75%',
            label: {
              align: 'right',
              fontSize: width >= 400 ? 10 : 8,
              show: width >= 300,
              color: '#e5e7eb',
              fontWeight: 'normal',
            },
          },
          {
            r0: '75%',
            r: '85%',
            label: {
              position: 'outside',
              padding: 3,
              silent: false,
              fontSize: width >= 400 ? 9 : 7,
              show: width >= 350,
              color: '#d1d5db',
              fontWeight: 'normal',
            },
            itemStyle: {
              borderWidth: 1,
              borderColor: '#4c1d95',
            },
          },
        ],
      },
    }),
    [chartData, width]
  );

  const onChartClick = (params: any) => {
    if (onSectorClick && params.data.originalName) {
      onSectorClick(params.data.originalName);
    }
  };

  return (
    <div className={`relative ${className}`}>
      <ReactECharts
        option={option}
        style={{
          height: `${height}px`,
          width: `${width}px`,
        }}
        opts={{
          renderer: 'canvas',
        }}
        onEvents={{
          click: onChartClick,
        }}
      />
    </div>
  );
};

export { SunburstChart };
