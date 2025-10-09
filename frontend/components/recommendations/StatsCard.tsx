import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { TrendingUp, TrendingDown, BarChart3, Users, Target, AlertTriangle } from "lucide-react";
import { AnalyzedRecommendation } from "@/__api__/recommendationsApi";

interface StatsCardProps {
  data: (AnalyzedRecommendation | any)[];
  title?: string;
  className?: string;
}

export function RecommendationsStatsCard({ data, title = "Estatísticas", className }: StatsCardProps) {
  if (!data || data.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <AlertTriangle className="h-5 w-5 text-muted-foreground" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Nenhum dado disponível</p>
        </CardContent>
      </Card>
    );
  }

  // Calculate recommendation counts
  const recommendationCounts = data.reduce((acc: {[key: string]: number}, item: any) => {
    const key = item.recommendationKey || 'Unknown';
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});
  
  // Calculate total recommendations
  const totalRecommendations = Object.values(recommendationCounts).reduce((sum: number, count: number) => sum + count, 0);
  
  // Calculate average return_target_consensus where available
  const returnsData = data.filter((item: any) => typeof item.return_target_consensus === 'number');
  const averageReturn = returnsData.length > 0 
    ? returnsData.reduce((sum: number, item: any) => sum + item.return_target_consensus, 0) / returnsData.length
    : null;

  // Calculate risk metrics
  const positiveReturns = data.filter((item: any) => 
    typeof item.return_target_consensus === 'number' && item.return_target_consensus > 0
  );
  const negativeReturns = data.filter((item: any) => 
    typeof item.return_target_consensus === 'number' && item.return_target_consensus < 0
  );
  
  const positiveReturnRate = totalRecommendations > 0 ? (positiveReturns.length / totalRecommendations) * 100 : 0;
  const negativeReturnRate = totalRecommendations > 0 ? (negativeReturns.length / totalRecommendations) * 100 : 0;

  // Calculate analyst coverage
  const totalAnalysts = data.reduce((sum: number, item: any) => sum + (item.numberOfAnalystOpinions || 0), 0);
  const avgAnalystsPerStock = totalRecommendations > 0 ? totalAnalysts / totalRecommendations : 0;
  
  // Map recommendation keys to readable names and colors with improved color scheme
  const recommendationLabels: {[key: string]: { name: string; color: string } } = {
    'strong_buy': { name: 'Compra Forte', color: 'bg-emerald-100 text-emerald-800 border-emerald-200' },
    'buy': { name: 'Compra', color: 'bg-green-100 text-green-800 border-green-200' },
    'hold': { name: 'Manter', color: 'bg-amber-100 text-amber-800 border-amber-200' },
    'sell': { name: 'Venda', color: 'bg-red-100 text-red-800 border-red-200' },
    'strong_sell': { name: 'Venda Forte', color: 'bg-red-100 text-red-800 border-red-200' },
    'underperform': { name: 'Abaixo do Mercado', color: 'bg-orange-100 text-orange-800 border-orange-200' },
    'none': { name: 'Sem Recomendação', color: 'bg-gray-100 text-gray-800 border-gray-200' },
    'Unknown': { name: 'Não Especificado', color: 'bg-gray-100 text-gray-800 border-gray-200' }
  };

  return (
    <Card className={className}>
      <CardHeader className="pb-4">
        <CardTitle className="flex items-center gap-2 text-lg">
          <BarChart3 className="h-5 w-5 text-blue-600" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">{totalRecommendations}</div>
            <div className="text-xs text-blue-600 font-medium">Total de Ativos</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">{avgAnalystsPerStock.toFixed(1)}</div>
            <div className="text-xs text-green-600 font-medium">Analistas/Ativo</div>
          </div>
        </div>

        {/* Return Distribution */}
        {averageReturn !== null && (
          <div className="space-y-3">
            <h4 className="font-medium text-sm flex items-center gap-2">
              <Target className="h-4 w-4" />
              Distribuição de Retornos
            </h4>
            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <span className="text-sm text-green-600">Positivos</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-green-500 h-2 rounded-full" 
                      style={{ width: `${positiveReturnRate}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{positiveReturnRate.toFixed(1)}%</span>
                </div>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-red-600">Negativos</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-red-500 h-2 rounded-full" 
                      style={{ width: `${negativeReturnRate}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium">{negativeReturnRate.toFixed(1)}%</span>
                </div>
              </div>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Retorno Médio:</span>
                <span className={`font-medium ${averageReturn > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {(averageReturn * 100).toFixed(2)}%
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Recommendation Breakdown */}
        <div className="space-y-3">
          <h4 className="font-medium text-sm flex items-center gap-2">
            <Users className="h-4 w-4" />
            Recomendações por Tipo
          </h4>
          <div className="space-y-2">
            {Object.entries(recommendationCounts)
              .sort(([,a], [,b]) => b - a)
              .map(([key, count]) => {
                const label = recommendationLabels[key] || { name: key, color: 'bg-gray-100 text-gray-800 border-gray-200' };
                const percentage = totalRecommendations > 0 ? (count / totalRecommendations) * 100 : 0;
                
                return (
                  <div key={key} className="flex justify-between items-center">
                    <Badge variant="outline" className={`text-xs ${label.color}`}>
                      {label.name}
                    </Badge>
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-blue-500 h-2 rounded-full" 
                          style={{ width: `${percentage}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium">{count}</span>
                    </div>
                  </div>
                );
              })}
          </div>
        </div>

        {/* Quick Insights */}
        <div className="pt-2 border-t">
          <h4 className="font-medium text-sm mb-2">Insights Rápidos</h4>
          <div className="space-y-2 text-xs text-muted-foreground">
            {positiveReturns.length > negativeReturns.length && (
              <div className="flex items-center gap-2">
                <TrendingUp className="h-3 w-3 text-green-600" />
                <span>Maioria dos ativos com retorno esperado positivo</span>
              </div>
            )}
            {avgAnalystsPerStock > 5 && (
              <div className="flex items-center gap-2">
                <Users className="h-3 w-3 text-blue-600" />
                <span>Alta cobertura de analistas</span>
              </div>
            )}
            {recommendationCounts['strong_buy'] > recommendationCounts['sell'] && (
              <div className="flex items-center gap-2">
                <TrendingUp className="h-3 w-3 text-green-600" />
                <span>Viés otimista nas recomendações</span>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}