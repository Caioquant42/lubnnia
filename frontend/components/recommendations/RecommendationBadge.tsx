import React from 'react';
import { cn } from '@/lib/utils';

interface RecommendationBadgeProps {
  recommendationKey: string;
  className?: string;
  children?: React.ReactNode;
}

export function RecommendationBadge({ 
  recommendationKey, 
  className,
  children 
}: RecommendationBadgeProps) {
  // Define improved color scheme for recommendation badges
  const getBadgeColors = (key: string) => {
    switch (key.toLowerCase()) {
      case 'strong_buy':
        return 'bg-emerald-100 text-emerald-800 border-emerald-200 hover:bg-emerald-200';
      case 'buy':
        return 'bg-green-100 text-green-800 border-green-200 hover:bg-green-200';
      case 'hold':
        return 'bg-amber-100 text-amber-800 border-amber-200 hover:bg-amber-200';
      case 'sell':
        return 'bg-red-100 text-red-800 border-red-200 hover:bg-red-200';
      case 'strong_sell':
        return 'bg-red-100 text-red-800 border-red-200 hover:bg-red-200';
      case 'underperform':
        return 'bg-orange-100 text-orange-800 border-orange-200 hover:bg-orange-200';
      case 'none':
        return 'bg-gray-100 text-gray-800 border-gray-200 hover:bg-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200 hover:bg-gray-200';
    }
  };

  // Get readable name for the recommendation
  const getRecommendationName = (key: string) => {
    switch (key.toLowerCase()) {
      case 'strong_buy':
        return 'Compra Forte';
      case 'buy':
        return 'Compra';
      case 'hold':
        return 'Manter';
      case 'sell':
        return 'Venda';
      case 'strong_sell':
        return 'Venda Forte';
      case 'underperform':
        return 'Abaixo do Mercado';
      case 'none':
        return 'Sem Recomendação';
      default:
        return key;
    }
  };

  const colors = getBadgeColors(recommendationKey);
  const name = getRecommendationName(recommendationKey);

  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors',
        colors,
        className
      )}
    >
      {children || name}
    </span>
  );
} 