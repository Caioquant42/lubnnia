"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { formatNumber } from "@/lib/utils";

interface PairDetailsProps {
  data: any;
}

export default function PairDetails({ data }: PairDetailsProps) {
  if (!data) {
    return (
      <div className="text-center py-8">
        <p className="text-muted-foreground">Nenhum dado disponível para este par.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Section */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Status de Cointegração
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.cointegrated ? (
                <Badge variant="default" className="text-lg px-3 py-1">
                  Cointegrado
                </Badge>
              ) : (
                <Badge variant="secondary" className="text-lg px-3 py-1">
                  Não Cointegrado
                </Badge>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Valor P
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.p_value !== undefined ? formatNumber(data.p_value, 4) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {data.p_value !== undefined && data.p_value < 0.05 ? 'Estatisticamente significativo' : 'Não significativo'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Beta (Razão de Hedge)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.beta !== undefined ? formatNumber(data.beta, 3) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Razão de hedge para neutralizar risco
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Meia-Vida (Dias)
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.half_life !== undefined ? formatNumber(data.half_life, 1) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Tempo para o spread retornar à média
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Z-Score Atual
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {data.current_zscore !== undefined ? formatNumber(data.current_zscore, 2) : 'N/A'}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              {data.current_zscore !== undefined && Math.abs(data.current_zscore) > 2 ? 'Oportunidade de trading' : 'Dentro da faixa normal'}
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs for detailed information */}
      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="overview">Visão Geral</TabsTrigger>
          <TabsTrigger value="signals">Sinais Recentes</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <Card>
            <CardContent className="pt-6">
              <div className="space-y-4">
                <div>
                  <h4 className="font-medium mb-2">Resumo da Análise</h4>
                  <p className="text-sm text-muted-foreground">
                    {data.cointegrated 
                      ? 'Este par de ativos mostra evidência estatística de cointegração, indicando uma relação de longo prazo entre os preços. Isso sugere oportunidades de arbitragem estatística quando os preços se desviam significativamente de sua relação histórica.'
                      : 'Este par de ativos não mostra evidência estatística de cointegração, indicando que não há uma relação de longo prazo estável entre os preços.'
                    }
                  </p>
                </div>
                
                {data.cointegrated && (
                  <div>
                    <h4 className="font-medium mb-2">Estratégia de Trading</h4>
                    <p className="text-sm text-muted-foreground">
                      Quando o Z-Score excede 2 (sobrevalorizado) ou -2 (subvalorizado), considere posições contrárias: 
                      comprar o ativo subvalorizado e vender o sobrevalorizado, esperando que retornem à sua relação histórica.
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="signals">
          <Card>
            <CardContent className="pt-6">
              {data.recent_signals && data.recent_signals.length > 0 ? (
                <div className="rounded-md border">
                  <table className="w-full caption-bottom text-sm">
                    <thead>
                      <tr className="border-b">
                        <th className="p-3 text-left font-medium">Tipo de Sinal</th>
                        <th className="p-3 text-left font-medium">Data</th>
                        <th className="p-3 text-left font-medium">Z-Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.recent_signals.map((signal: any, index: number) => (
                        <tr key={index} className="border-b">
                          <td className="p-3">
                            <Badge variant={signal.signal_type === 'buy' ? 'default' : 'destructive'}>
                              {signal.signal_type === 'buy' ? 'COMPRA' : 'VENDA'}
                            </Badge>
                          </td>
                          <td className="p-3">{new Date(signal.signal_date).toLocaleDateString('pt-BR')}</td>
                          <td className="p-3">{formatNumber(signal.current_zscore)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <p className="text-muted-foreground">Nenhum sinal recente disponível para este par.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}