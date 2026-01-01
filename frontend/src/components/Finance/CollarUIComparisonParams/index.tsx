"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { CollarUIComparisonParams as ComparisonParams } from "__api__/collarUIApi";

interface CollarUIComparisonParamsProps {
  params: ComparisonParams;
  onChange: (params: ComparisonParams) => void;
  structureLabel: "A" | "B";
}

export function CollarUIComparisonParams({
  params,
  onChange,
  structureLabel,
}: CollarUIComparisonParamsProps) {
  const tickerKey = `ticker_${structureLabel}` as keyof ComparisonParams;
  const s0Key = `S0_${structureLabel}` as keyof ComparisonParams;
  const strikePutKey = `strike_put_pct_${structureLabel}` as keyof ComparisonParams;
  const strikeCallKey = `strike_call_pct_${structureLabel}` as keyof ComparisonParams;
  const expirationKey = `expiration_date_${structureLabel}` as keyof ComparisonParams;
  const barrierKey = `barrier_pct_${structureLabel}` as keyof ComparisonParams;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Estrutura {structureLabel}</CardTitle>
        <CardDescription>Parâmetros da estrutura {structureLabel}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Ticker</Label>
            <Input
              value={(params[tickerKey] as string) || ""}
              onChange={(e) =>
                onChange({ ...params, [tickerKey]: e.target.value.toUpperCase() })
              }
              placeholder="ex: PETR4"
            />
          </div>
          <div className="space-y-2">
            <Label>Preço Inicial (S0)</Label>
            <Input
              type="number"
              step="0.01"
              value={(params[s0Key] as number) || 0}
              onChange={(e) =>
                onChange({ ...params, [s0Key]: parseFloat(e.target.value) || 0 })
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
              value={(params[strikePutKey] as number) || 0}
              onChange={(e) =>
                onChange({ ...params, [strikePutKey]: parseFloat(e.target.value) || 0 })
              }
              placeholder="ex: 90.0"
            />
          </div>
          <div className="space-y-2">
            <Label>Strike Call (% do S0)</Label>
            <Input
              type="number"
              step="0.1"
              value={(params[strikeCallKey] as number) || 0}
              onChange={(e) =>
                onChange({ ...params, [strikeCallKey]: parseFloat(e.target.value) || 0 })
              }
              placeholder="ex: 107.5"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label>Data de Vencimento (DD-MM-YYYY)</Label>
            <Input
              value={(params[expirationKey] as string) || ""}
              onChange={(e) =>
                onChange({ ...params, [expirationKey]: e.target.value })
              }
              placeholder="ex: 12-03-2026"
            />
          </div>
          <div className="space-y-2">
            <Label>Barreira Up&In (% do S0)</Label>
            <Input
              type="number"
              step="0.1"
              value={(params[barrierKey] as number) || 0}
              onChange={(e) =>
                onChange({ ...params, [barrierKey]: parseFloat(e.target.value) || 0 })
              }
              placeholder="ex: 144.0"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

