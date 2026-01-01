"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CollarUIComparisonResponse } from "__api__/collarUIApi";
import { Badge } from "@/components/ui/badge";

interface CollarUIComparisonTableProps {
  data: CollarUIComparisonResponse;
}

export function CollarUIComparisonTable({ data }: CollarUIComparisonTableProps) {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatNumber = (value: number, decimals: number = 4) => value.toFixed(decimals);

  const metrics = data.comparison_metrics;

  return (
    <div className="space-y-6">
      {/* Return and Risk Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Métricas de Retorno e Risco</CardTitle>
          <CardDescription>Comparação de retorno esperado, volatilidade e ratios</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Métrica</TableHead>
                <TableHead>Estrutura A</TableHead>
                <TableHead>Estrutura B</TableHead>
                <TableHead>Diferença (B - A)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Retorno Esperado</TableCell>
                <TableCell>{formatPercent(metrics.expected_return.A)}</TableCell>
                <TableCell>{formatPercent(metrics.expected_return.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.expected_return.B > metrics.expected_return.A ? "default" : "secondary"}>
                    {formatPercent(metrics.expected_return.B - metrics.expected_return.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Desvio Padrão</TableCell>
                <TableCell>{formatPercent(metrics.std.A)}</TableCell>
                <TableCell>{formatPercent(metrics.std.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.std.B < metrics.std.A ? "default" : "secondary"}>
                    {formatPercent(metrics.std.B - metrics.std.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Sharpe Ratio</TableCell>
                <TableCell>{formatNumber(metrics.sharpe_ratio.A)}</TableCell>
                <TableCell>{formatNumber(metrics.sharpe_ratio.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.sharpe_ratio.B > metrics.sharpe_ratio.A ? "default" : "secondary"}>
                    {formatNumber(metrics.sharpe_ratio.B - metrics.sharpe_ratio.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Sortino Ratio</TableCell>
                <TableCell>{formatNumber(metrics.sortino_ratio.A)}</TableCell>
                <TableCell>{formatNumber(metrics.sortino_ratio.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.sortino_ratio.B > metrics.sortino_ratio.A ? "default" : "secondary"}>
                    {formatNumber(metrics.sortino_ratio.B - metrics.sortino_ratio.A)}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Scenario Probabilities */}
      <Card>
        <CardHeader>
          <CardTitle>Probabilidades de Cenários</CardTitle>
          <CardDescription>Comparação das probabilidades de diferentes cenários</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cenário</TableHead>
                <TableHead>Estrutura A</TableHead>
                <TableHead>Estrutura B</TableHead>
                <TableHead>Diferença (B - A)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Perda</TableCell>
                <TableCell>{formatPercent(metrics.prob_perda.A)}</TableCell>
                <TableCell>{formatPercent(metrics.prob_perda.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.prob_perda.B < metrics.prob_perda.A ? "default" : "secondary"}>
                    {formatPercent(metrics.prob_perda.B - metrics.prob_perda.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho (sem barreira)</TableCell>
                <TableCell>{formatPercent(metrics.prob_ganho_sem_barreira.A)}</TableCell>
                <TableCell>{formatPercent(metrics.prob_ganho_sem_barreira.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.prob_ganho_sem_barreira.B > metrics.prob_ganho_sem_barreira.A ? "default" : "secondary"}>
                    {formatPercent(metrics.prob_ganho_sem_barreira.B - metrics.prob_ganho_sem_barreira.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho (barreira ativada)</TableCell>
                <TableCell>{formatPercent(metrics.prob_ganho_com_barreira.A)}</TableCell>
                <TableCell>{formatPercent(metrics.prob_ganho_com_barreira.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.prob_ganho_com_barreira.B > metrics.prob_ganho_com_barreira.A ? "default" : "secondary"}>
                    {formatPercent(metrics.prob_ganho_com_barreira.B - metrics.prob_ganho_com_barreira.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho Positivo (qualquer)</TableCell>
                <TableCell>{formatPercent(metrics.prob_ganho_positivo.A)}</TableCell>
                <TableCell>{formatPercent(metrics.prob_ganho_positivo.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.prob_ganho_positivo.B > metrics.prob_ganho_positivo.A ? "default" : "secondary"}>
                    {formatPercent(metrics.prob_ganho_positivo.B - metrics.prob_ganho_positivo.A)}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Risk Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Métricas de Risco</CardTitle>
          <CardDescription>Value at Risk, Conditional VaR e percentis</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Métrica</TableHead>
                <TableHead>Estrutura A</TableHead>
                <TableHead>Estrutura B</TableHead>
                <TableHead>Diferença (B - A)</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">VaR 5%</TableCell>
                <TableCell>{formatPercent(metrics.VaR_5.A)}</TableCell>
                <TableCell>{formatPercent(metrics.VaR_5.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.VaR_5.B > metrics.VaR_5.A ? "default" : "secondary"}>
                    {formatPercent(metrics.VaR_5.B - metrics.VaR_5.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">CVaR 5%</TableCell>
                <TableCell>{formatPercent(metrics.CVaR_5.A)}</TableCell>
                <TableCell>{formatPercent(metrics.CVaR_5.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.CVaR_5.B > metrics.CVaR_5.A ? "default" : "secondary"}>
                    {formatPercent(metrics.CVaR_5.B - metrics.CVaR_5.A)}
                  </Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 5%</TableCell>
                <TableCell>{formatPercent(metrics.percentis.A[5])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[5])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[5] - metrics.percentis.A[5])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 25%</TableCell>
                <TableCell>{formatPercent(metrics.percentis.A[25])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[25])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[25] - metrics.percentis.A[25])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Mediana (50%)</TableCell>
                <TableCell>{formatPercent(metrics.percentis.A[50])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[50])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[50] - metrics.percentis.A[50])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 75%</TableCell>
                <TableCell>{formatPercent(metrics.percentis.A[75])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[75])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[75] - metrics.percentis.A[75])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 95%</TableCell>
                <TableCell>{formatPercent(metrics.percentis.A[95])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[95])}</TableCell>
                <TableCell>{formatPercent(metrics.percentis.B[95] - metrics.percentis.A[95])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho Esperado Condicional</TableCell>
                <TableCell>{formatPercent(metrics.ganho_esperado_condicional.A)}</TableCell>
                <TableCell>{formatPercent(metrics.ganho_esperado_condicional.B)}</TableCell>
                <TableCell>
                  <Badge variant={metrics.ganho_esperado_condicional.B > metrics.ganho_esperado_condicional.A ? "default" : "secondary"}>
                    {formatPercent(metrics.ganho_esperado_condicional.B - metrics.ganho_esperado_condicional.A)}
                  </Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Recommendation */}
      <Card>
        <CardHeader>
          <CardTitle>Análise e Recomendação</CardTitle>
          <CardDescription>Score composto e recomendação baseada em múltiplas métricas</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-muted-foreground">Score Composto A</p>
              <p className="text-2xl font-bold">{formatNumber(data.composite_scores.A)}</p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground">Score Composto B</p>
              <p className="text-2xl font-bold">{formatNumber(data.composite_scores.B)}</p>
            </div>
          </div>
          <div className="pt-4 border-t">
            <p className="text-lg font-semibold">
              Recomendação: Estrutura {data.recommendation}
            </p>
            <p className="text-sm text-muted-foreground mt-2">
              Baseado em retorno esperado (30%), Sharpe ratio (20%), probabilidade de ganho (20%),
              CVaR (15%) e ganho esperado condicional (15%).
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

