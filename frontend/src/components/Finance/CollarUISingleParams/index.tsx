"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CollarUISingleParams as SingleParams } from "__api__/collarUIApi";

interface CollarUISingleParamsProps {
  params: SingleParams;
  onChange: (params: SingleParams) => void;
}

export function CollarUISingleParams({
  params,
  onChange,
}: CollarUISingleParamsProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Parâmetros da Estrutura</CardTitle>
        <CardDescription>Configure os parâmetros da estrutura Collar Up & In</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Ticker</Label>
            <Input
              value={params.ticker || ""}
              onChange={(e) =>
                onChange({ ...params, ticker: e.target.value.toUpperCase() })
              }
              placeholder="ex: PETR4"
            />
          </div>
          <div className="space-y-2">
            <Label>Preço Inicial (S0)</Label>
            <Input
              type="number"
              step="0.01"
              value={params.S0 || 0}
              onChange={(e) =>
                onChange({ ...params, S0: parseFloat(e.target.value) || 0 })
              }
              placeholder="ex: 38.50"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Strike Put (% do S0)</Label>
            <Input
              type="number"
              step="0.1"
              value={params.strike_put_pct || 0}
              onChange={(e) =>
                onChange({ ...params, strike_put_pct: parseFloat(e.target.value) || 0 })
              }
              placeholder="ex: 90.0"
            />
          </div>
          <div className="space-y-2">
            <Label>Strike Call (% do S0)</Label>
            <Input
              type="number"
              step="0.1"
              value={params.strike_call_pct || 0}
              onChange={(e) =>
                onChange({ ...params, strike_call_pct: parseFloat(e.target.value) || 0 })
              }
              placeholder="ex: 107.5"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Data de Vencimento (DD-MM-YYYY)</Label>
            <Input
              value={params.expiration_date || ""}
              onChange={(e) =>
                onChange({ ...params, expiration_date: e.target.value })
              }
              placeholder="ex: 12-03-2026"
            />
          </div>
          <div className="space-y-2">
            <Label>Barreira Up&In (% do S0)</Label>
            <Input
              type="number"
              step="0.1"
              value={params.barrier_pct || 0}
              onChange={(e) =>
                onChange({ ...params, barrier_pct: parseFloat(e.target.value) || 0 })
              }
              placeholder="ex: 144.0"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Número de Caminhos Bootstrap</Label>
            <Input
              type="number"
              value={params.n_bootstrap || 1000}
              onChange={(e) =>
                onChange({ ...params, n_bootstrap: parseInt(e.target.value) || 1000 })
              }
              placeholder="ex: 1000"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}



