'use client';

import { RRGDataPoint } from '__api__/rrgApi';
import { useCallback, useMemo, useState } from 'react';
import {
  CartesianGrid,
  Cell,
  LabelList,
  ReferenceLine,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Badge } from '../../ui/badge';

interface RRGChartProps {
  data: RRGDataPoint[];
  width?: number;
  height?: number;
  onPointClick?: (point: RRGDataPoint) => void;
  selectedSymbols?: string[];
  showTrail?: boolean;
  trailLength?: number;
}

// Enhanced quadrant definitions for RRG with better colors
const QUADRANTS = {
  leading: {
    name: 'Leading',
    color: '#10b981', // Emerald green
    bgColor: 'rgba(16, 185, 129, 0.08)',
    borderColor: '#059669',
  },
  weakening: {
    name: 'Weakening',
    color: '#f59e0b', // Amber
    bgColor: 'rgba(245, 158, 11, 0.08)',
    borderColor: '#d97706',
  },
  lagging: {
    name: 'Lagging',
    color: '#ef4444', // Red
    bgColor: 'rgba(239, 68, 68, 0.08)',
    borderColor: '#dc2626',
  },
  improving: {
    name: 'Improving',
    color: '#3b82f6', // Blue
    bgColor: 'rgba(59, 130, 246, 0.08)',
    borderColor: '#2563eb',
  },
};

// Enhanced color palette for different symbols - more distinct colors
const SYMBOL_COLORS = [
  '#1f77b4',
  '#ff7f0e',
  '#2ca02c',
  '#d62728',
  '#9467bd',
  '#8c564b',
  '#e377c2',
  '#7f7f7f',
  '#bcbd22',
  '#17becf',
  '#aec7e8',
  '#ffbb78',
  '#98df8a',
  '#ff9896',
  '#c5b0d5',
  '#c49c94',
  '#f7b6d3',
  '#c7c7c7',
  '#dbdb8d',
  '#9edae5',
];

// Function to determine quadrant based on RS Ratio and RS Momentum
const getQuadrant = (
  rsRatio: number,
  rsMomentum: number
): keyof typeof QUADRANTS => {
  if (rsRatio >= 100 && rsMomentum >= 100) return 'leading';
  if (rsRatio >= 100 && rsMomentum < 100) return 'weakening';
  if (rsRatio < 100 && rsMomentum < 100) return 'lagging';
  return 'improving';
};

const RRGChart = ({
  data,
  width = 800,
  height = 600,
  onPointClick,
  selectedSymbols = [],
  showTrail = true,
  trailLength = 5,
}: RRGChartProps) => {
  const [hoveredSymbol, setHoveredSymbol] = useState<string | null>(null);

  // Process data to include trail information and latest points
  const { processedData, trailData, symbolToColorMap } = useMemo(() => {
    if (!data || data.length === 0)
      return { processedData: [], trailData: [], symbolToColorMap: {} };

    // Group by symbol and sort by date
    const symbolGroups = data.reduce(
      (acc, point) => {
        if (!acc[point.symbol]) {
          acc[point.symbol] = [];
        }
        acc[point.symbol].push(point);
        return acc;
      },
      {} as Record<string, RRGDataPoint[]>
    );

    // Create color mapping for symbols
    const symbols = Object.keys(symbolGroups);
    const symbolToColorMap = symbols.reduce(
      (acc, symbol, index) => {
        acc[symbol] = SYMBOL_COLORS[index % SYMBOL_COLORS.length];
        return acc;
      },
      {} as Record<string, string>
    );

    // Process latest points for scatter plot
    const processedData = Object.entries(symbolGroups).map(
      ([symbol, points]) => {
        // Sort by date and get the latest point
        const sortedPoints = points.sort(
          (a, b) => new Date(b.date).getTime() - new Date(a.date).getTime()
        );
        const latestPoint = sortedPoints[0];

        const quadrant = getQuadrant(
          latestPoint.rs_ratio,
          latestPoint.rs_momentum
        );

        return {
          ...latestPoint,
          quadrant,
          symbolColor: symbolToColorMap[symbol],
          isSelected: selectedSymbols.includes(symbol),
          isHovered: hoveredSymbol === symbol,
          size: selectedSymbols.includes(symbol)
            ? 8
            : hoveredSymbol === symbol
              ? 6
              : 5,
        };
      }
    );

    // Process trail data for each symbol
    const trailData = Object.entries(symbolGroups).map(([symbol, points]) => {
      const sortedPoints = points
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
        .slice(-trailLength);

      return {
        symbol,
        points: sortedPoints.map((point, index) => ({
          ...point,
          quadrant: getQuadrant(point.rs_ratio, point.rs_momentum),
          trailIndex: index,
          isLatest: index === sortedPoints.length - 1,
          opacity: 0.3 + (index / (sortedPoints.length - 1)) * 0.7, // Increasing opacity
        })),
        color: symbolToColorMap[symbol],
        isSelected: selectedSymbols.includes(symbol),
        isVisible: showTrail,
      };
    });

    return { processedData, trailData, symbolToColorMap };
  }, [data, selectedSymbols, hoveredSymbol, showTrail, trailLength]);
  // Custom Trail Component that overlays on the chart
  const TrailOverlay = useCallback(() => {
    if (!showTrail) return null;

    return (
      <div className='absolute inset-0 pointer-events-none'>
        <svg width='100%' height='100%' className='absolute inset-0'>
          {trailData.map((trail) => {
            if (trail.points.length < 2) return null;

            const isHighlighted =
              trail.isSelected || hoveredSymbol === trail.symbol;
            const opacity = isHighlighted ? 0.8 : 0.4;
            const strokeWidth = isHighlighted ? 2.5 : 1.5;

            // Calculate path for trail
            const pathData = trail.points
              .map((point, index) => {
                // This is a simplified calculation - in a real implementation,
                // you'd need to convert data coordinates to pixel coordinates
                const x =
                  60 +
                  ((point.rs_ratio - xDomain[0]) / (xDomain[1] - xDomain[0])) *
                    (width - 80);
                const y =
                  height -
                  60 -
                  ((point.rs_momentum - yDomain[0]) /
                    (yDomain[1] - yDomain[0])) *
                    (height - 80);
                return index === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
              })
              .join(' ');

            return (
              <g key={`trail-${trail.symbol}`}>
                {/* Trail path */}
                <path
                  d={pathData}
                  fill='none'
                  stroke={trail.color}
                  strokeWidth={strokeWidth}
                  strokeOpacity={opacity}
                  strokeDasharray='4,3'
                  strokeLinecap='round'
                />

                {/* Trail points (except the last one which is the main point) */}
                {trail.points.slice(0, -1).map((point, index) => {
                  const x =
                    60 +
                    ((point.rs_ratio - xDomain[0]) /
                      (xDomain[1] - xDomain[0])) *
                      (width - 80);
                  const y =
                    height -
                    60 -
                    ((point.rs_momentum - yDomain[0]) /
                      (yDomain[1] - yDomain[0])) *
                      (height - 80);

                  return (
                    <circle
                      key={`trail-point-${trail.symbol}-${index}`}
                      cx={x}
                      cy={y}
                      r={2 + index * 0.3}
                      fill={trail.color}
                      fillOpacity={point.opacity}
                      stroke={trail.color}
                      strokeWidth={0.5}
                      strokeOpacity={opacity}
                    />
                  );
                })}
              </g>
            );
          })}
        </svg>
      </div>
    );
  }, []); // Enhanced tooltip component

  const CustomTooltip = useCallback(({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload;

      if (!data || !data.symbol) return null;

      const quadrantInfo = QUADRANTS[data.quadrant as keyof typeof QUADRANTS];

      return (
        <div className='bg-white border border-gray-200 rounded-lg shadow-lg p-4 text-sm min-w-[200px]'>
          <div className='flex items-center gap-2 mb-3'>
            <div
              className='w-3 h-3 rounded-full'
              style={{ backgroundColor: data.symbolColor }}
            />
            <span className='font-semibold text-gray-900 text-base'>
              {data.symbol}
            </span>
          </div>

          <div className='space-y-2 text-gray-600'>
            <div className='flex justify-between'>
              <span>RS Ratio:</span>
              <span className='font-medium text-gray-900'>
                {data.rs_ratio?.toFixed(3) || 'N/A'}
              </span>
            </div>
            <div className='flex justify-between'>
              <span>RS Momentum:</span>
              <span className='font-medium text-gray-900'>
                {data.rs_momentum?.toFixed(3) || 'N/A'}
              </span>
            </div>
            <div className='flex justify-between items-center'>
              <span>Quadrant:</span>
              <Badge
                variant='secondary'
                className='text-xs font-medium'
                style={{
                  backgroundColor: quadrantInfo?.bgColor || 'rgba(0,0,0,0.1)',
                  color: quadrantInfo?.color || '#000',
                }}
              >
                {quadrantInfo?.name || 'Unknown'}
              </Badge>
            </div>
            <div className='flex justify-between'>
              <span>Date:</span>
              <span className='font-medium text-gray-900'>
                {data.date ? new Date(data.date).toLocaleDateString() : 'N/A'}
              </span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  }, []);

  // Handle mouse events
  const handlePointClick = (data: any) => {
    if (onPointClick) {
      onPointClick(data);
    }
  };

  const handleMouseEnter = (data: any) => {
    setHoveredSymbol(data.symbol);
  };

  const handleMouseLeave = () => {
    setHoveredSymbol(null);
  };
  // Calculate domain with better padding
  const xDomain = useMemo(() => {
    if (processedData.length === 0) return [95, 105];
    const allValues = [
      ...processedData.map((d) => d.rs_ratio),
      ...trailData.flatMap((trail) => trail.points.map((p) => p.rs_ratio)),
    ];
    const min = Math.min(...allValues, 100);
    const max = Math.max(...allValues, 100);
    const range = max - min;
    const padding = Math.max(range * 0.1, 2);
    return [min - padding, max + padding];
  }, [processedData, trailData]);

  const yDomain = useMemo(() => {
    if (processedData.length === 0) return [95, 105];
    const allValues = [
      ...processedData.map((d) => d.rs_momentum),
      ...trailData.flatMap((trail) => trail.points.map((p) => p.rs_momentum)),
    ];
    const min = Math.min(...allValues, 100);
    const max = Math.max(...allValues, 100);
    const range = max - min;
    const padding = Math.max(range * 0.1, 2);
    return [min - padding, max + padding];
  }, [processedData, trailData]);
  return (
    <div className='relative bg-white rounded-lg border border-gray-200 p-4'>
      {/* Chart Title */}
      <div className='mb-4'>
        <h3 className='text-lg font-semibold text-gray-900'>
          Relative Rotation Graph (RRG)
        </h3>
        <p className='text-sm text-gray-500'>
          Interactive scatter plot showing relative strength and momentum with
          trails
          {showTrail && (
            <span className='ml-1 text-blue-600'>• Trails enabled</span>
          )}
        </p>
      </div>

      {/* Enhanced Legend */}
      <div className='mb-4 space-y-3'>
        <div className='flex flex-wrap gap-4 text-sm'>
          <span className='font-medium text-gray-700'>Quadrants:</span>
          {Object.entries(QUADRANTS).map(([key, quadrant]) => (
            <div key={key} className='flex items-center gap-2'>
              <div
                className='w-4 h-4 rounded-full border-2'
                style={{
                  backgroundColor: quadrant.bgColor,
                  borderColor: quadrant.color,
                }}
              />
              <span className='text-gray-600'>{quadrant.name}</span>
            </div>
          ))}
        </div>

        {showTrail && (
          <div className='flex items-center gap-2 text-xs text-gray-500'>
            <div className='w-3 h-0.5 bg-gray-400 border-dashed'></div>
            <span>
              Dashed lines show movement trail (last {trailLength} periods)
            </span>
          </div>
        )}
      </div>

      {/* Chart Container */}
      <div style={{ width: '100%', height: height }} className='relative'>
        <ResponsiveContainer width='100%' height='100%'>
          <ScatterChart
            margin={{ top: 20, right: 20, bottom: 60, left: 60 }}
            onClick={(e) => {
              if (e && e.activePayload && e.activePayload[0]) {
                handlePointClick(e.activePayload[0].payload);
              }
            }}
          >
            {/* Grid */}
            <CartesianGrid
              strokeDasharray='3 3'
              stroke='#e5e7eb'
              opacity={0.6}
            />

            {/* Axes */}
            <XAxis
              type='number'
              dataKey='rs_ratio'
              domain={xDomain}
              axisLine={{ stroke: '#6b7280' }}
              tickLine={{ stroke: '#6b7280' }}
              tick={{ fill: '#6b7280', fontSize: 12 }}
              label={{
                value: 'Relative Strength (RS Ratio)',
                position: 'insideBottom',
                offset: -40,
                style: {
                  textAnchor: 'middle',
                  fill: '#374151',
                  fontSize: '14px',
                  fontWeight: 500,
                },
              }}
            />
            <YAxis
              type='number'
              dataKey='rs_momentum'
              domain={yDomain}
              axisLine={{ stroke: '#6b7280' }}
              tickLine={{ stroke: '#6b7280' }}
              tick={{ fill: '#6b7280', fontSize: 12 }}
              label={{
                value: 'Momentum (RS Momentum)',
                angle: -90,
                position: 'insideLeft',
                style: {
                  textAnchor: 'middle',
                  fill: '#374151',
                  fontSize: '14px',
                  fontWeight: 500,
                },
              }}
            />
            {/* Reference lines at 100 */}
            <ReferenceLine
              x={100}
              stroke='#9ca3af'
              strokeDasharray='5 5'
              strokeWidth={2}
              label={{ value: '100', position: 'insideTopRight' }}
            />
            <ReferenceLine
              y={100}
              stroke='#9ca3af'
              strokeDasharray='5 5'
              strokeWidth={2}
              label={{ value: '100', position: 'insideTopRight' }}
            />

            {/* Quadrant Background Areas */}
            <defs>
              {Object.entries(QUADRANTS).map(([key, quadrant]) => (
                <pattern
                  key={key}
                  id={`${key}Pattern`}
                  patternUnits='userSpaceOnUse'
                  width='100%'
                  height='100%'
                >
                  <rect width='100%' height='100%' fill={quadrant.bgColor} />
                </pattern>
              ))}
            </defs>

            {/* Trail Lines - Custom SVG elements */}
            {showTrail &&
              trailData.map((trail) => {
                if (trail.points.length < 2) return null;

                const isHighlighted =
                  trail.isSelected || hoveredSymbol === trail.symbol;
                const opacity = isHighlighted ? 0.9 : 0.5;
                const strokeWidth = isHighlighted ? 3 : 2;

                return (
                  <g key={`trail-group-${trail.symbol}`}>
                    {trail.points.slice(0, -1).map((point, index) => {
                      const nextPoint = trail.points[index + 1];
                      // Note: These would need actual coordinate transformation in a real implementation
                      // For now, we'll use a simple line representation
                      return null; // Placeholder for trail lines
                    })}
                  </g>
                );
              })}

            {/* Data points */}
            <Scatter data={processedData} fill='#3b82f6'>
              {processedData.map((entry, index) => {
                const quadrantInfo =
                  QUADRANTS[entry.quadrant as keyof typeof QUADRANTS];
                const isHighlighted = entry.isSelected || entry.isHovered;

                return (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.symbolColor}
                    stroke={
                      isHighlighted
                        ? '#000'
                        : quadrantInfo?.borderColor || entry.symbolColor
                    }
                    strokeWidth={isHighlighted ? 3 : 1.5}
                    r={entry.size}
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() => handleMouseEnter(entry)}
                    onMouseLeave={handleMouseLeave}
                  />
                );
              })}

              {/* Labels for selected or hovered symbols */}
              <LabelList
                dataKey='symbol'
                position='top'
                content={(props: any) => {
                  const { x, y, payload } = props;
                  if (!payload || (!payload.isSelected && !payload.isHovered))
                    return null;
                  return (
                    <text
                      x={x}
                      y={y - 12}
                      textAnchor='middle'
                      fontSize='11'
                      fontWeight='700'
                      fill='#374151'
                      stroke='#ffffff'
                      strokeWidth='2'
                      paintOrder='stroke'
                    >
                      {payload.symbol}
                    </text>
                  );
                }}
              />
            </Scatter>

            {/* Custom tooltip */}
            <Tooltip content={<CustomTooltip />} />
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      {/* Enhanced Statistics */}
      <div className='mt-6 space-y-4'>
        <div className='grid grid-cols-2 md:grid-cols-4 gap-4 text-sm'>
          {Object.entries(QUADRANTS).map(([key, quadrant]) => {
            const count = processedData.filter(
              (d) => d.quadrant === key
            ).length;
            const percentage =
              processedData.length > 0
                ? ((count / processedData.length) * 100).toFixed(1)
                : '0';

            return (
              <div
                key={key}
                className='text-center p-3 rounded-lg border border-gray-200'
                style={{ backgroundColor: quadrant.bgColor }}
              >
                <div className='font-bold text-lg text-gray-900'>{count}</div>
                <div className='text-xs text-gray-600'>{percentage}%</div>
                <div className='text-gray-700 font-medium'>{quadrant.name}</div>
              </div>
            );
          })}
        </div>

        {/* Summary */}
        <div className='text-center text-sm text-gray-600 bg-gray-50 rounded-lg p-3'>
          <div className='font-medium'>
            Total Symbols: {processedData.length}
          </div>
          <div className='text-xs mt-1'>
            Click on data points to select/deselect • Hover for detailed
            information
            {showTrail && ' • Trails show recent movement patterns'}
          </div>
        </div>
      </div>
    </div>
  );
};

export { RRGChart };
