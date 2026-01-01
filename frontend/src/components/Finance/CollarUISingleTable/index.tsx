"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { CollarUISingleResponse } from "__api__/collarUIApi";
import { Badge } from "@/components/ui/badge";

interface CollarUISingleTableProps {
  data: CollarUISingleResponse;
}

export function CollarUISingleTable({ data }: CollarUISingleTableProps) {
  const formatPercent = (value: number) => `${(value * 100).toFixed(2)}%`;
  const formatNumber = (value: number, decimals: number = 4) => value.toFixed(decimals);

  const stats = data.statistics;
  const metrics = data.additional_metrics;

  return (
    <div className="space-y-6">
      {/* Basic Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Estatísticas Básicas</CardTitle>
          <CardDescription>Estatísticas dos payoffs e cenários da estrutura</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Métrica</TableHead>
                <TableHead>Valor</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Payoff Médio</TableCell>
                <TableCell>{formatPercent(stats.payoff_medio)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Payoff Mediano</TableCell>
                <TableCell>{formatPercent(stats.payoff_mediano)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Desvio Padrão</TableCell>
                <TableCell>{formatPercent(stats.payoff_std)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Payoff Mínimo</TableCell>
                <TableCell>
                  <Badge variant="destructive">{formatPercent(stats.payoff_min)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Payoff Máximo</TableCell>
                <TableCell>
                  <Badge variant="default">{formatPercent(stats.payoff_max)}</Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Scenario Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Cenários</CardTitle>
          <CardDescription>Distribuição dos cenários simulados</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Cenário</TableHead>
                <TableHead>Quantidade</TableHead>
                <TableHead>Percentual</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Perda</TableCell>
                <TableCell>{stats.n_perda}</TableCell>
                <TableCell>
                  <Badge variant="destructive">{formatPercent(stats.pct_perda / 100)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho (sem barreira)</TableCell>
                <TableCell>{stats.n_ganho_sem_barreira}</TableCell>
                <TableCell>
                  <Badge variant="default">{formatPercent(stats.pct_ganho_sem_barreira / 100)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho (barreira ativada)</TableCell>
                <TableCell>{stats.n_ganho_com_barreira}</TableCell>
                <TableCell>
                  <Badge variant="default">{formatPercent(stats.pct_ganho_com_barreira / 100)}</Badge>
                </TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Risk and Return Metrics */}
      <Card>
        <CardHeader>
          <CardTitle>Métricas de Retorno e Risco</CardTitle>
          <CardDescription>Análise de retorno esperado, volatilidade e ratios</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Métrica</TableHead>
                <TableHead>Valor</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Retorno Esperado</TableCell>
                <TableCell>{formatPercent(metrics.expected_return)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Desvio Padrão</TableCell>
                <TableCell>{formatPercent(metrics.std)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Sharpe Ratio</TableCell>
                <TableCell>{formatNumber(metrics.sharpe_ratio)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Sortino Ratio</TableCell>
                <TableCell>{formatNumber(metrics.sortino_ratio)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Probabilidade de Ganho Positivo</TableCell>
                <TableCell>{formatPercent(metrics.prob_ganho_positivo)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho Esperado Condicional</TableCell>
                <TableCell>{formatPercent(metrics.ganho_esperado_condicional)}</TableCell>
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
                <TableHead>Valor</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">VaR 5%</TableCell>
                <TableCell>
                  <Badge variant="destructive">{formatPercent(metrics.VaR_5)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">CVaR 5%</TableCell>
                <TableCell>
                  <Badge variant="destructive">{formatPercent(metrics.CVaR_5)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 5%</TableCell>
                <TableCell>{formatPercent(metrics.percentis[5])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 25%</TableCell>
                <TableCell>{formatPercent(metrics.percentis[25])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Mediana (50%)</TableCell>
                <TableCell>{formatPercent(metrics.percentis[50])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 75%</TableCell>
                <TableCell>{formatPercent(metrics.percentis[75])}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Percentil 95%</TableCell>
                <TableCell>{formatPercent(metrics.percentis[95])}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>

      {/* Structure Parameters */}
      <Card>
        <CardHeader>
          <CardTitle>Parâmetros da Estrutura</CardTitle>
          <CardDescription>Configuração da estrutura Collar Up & In</CardDescription>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Parâmetro</TableHead>
                <TableHead>Valor</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              <TableRow>
                <TableCell className="font-medium">Ticker</TableCell>
                <TableCell>{data.ticker}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Preço Inicial (S0)</TableCell>
                <TableCell>R$ {data.params.S0.toFixed(2)}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Strike Put</TableCell>
                <TableCell>{formatPercent(data.params.strike_put)} (R$ {(data.params.S0 * data.params.strike_put).toFixed(2)})</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Strike Call</TableCell>
                <TableCell>{formatPercent(data.params.strike_call)} (R$ {(data.params.S0 * data.params.strike_call).toFixed(2)})</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Barreira Up&In</TableCell>
                <TableCell>{formatPercent(data.params.barreira_ativacao)} (R$ {(data.params.S0 * data.params.barreira_ativacao).toFixed(2)})</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Prejuízo Máximo</TableCell>
                <TableCell>
                  <Badge variant="destructive">{formatPercent(data.params.prejuizo_maximo)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho Máximo (barreira ativada)</TableCell>
                <TableCell>
                  <Badge variant="default">{formatPercent(data.params.ganho_max_ativado)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Ganho Máximo (barreira NÃO ativada)</TableCell>
                <TableCell>
                  <Badge variant="default">{formatPercent(data.params.ganho_max_nao_ativado)}</Badge>
                </TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Dias Úteis até Vencimento</TableCell>
                <TableCell>{data.params.dias_uteis}</TableCell>
              </TableRow>
              <TableRow>
                <TableCell className="font-medium">Data de Vencimento</TableCell>
                <TableCell>{new Date(data.params.data_vencimento).toLocaleDateString('pt-BR')}</TableCell>
              </TableRow>
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}



