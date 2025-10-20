"use client";

import { useState, useEffect } from 'react';
import {
  Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle
} from "@/components/ui/card";
import {
  Select, SelectContent, SelectItem, SelectTrigger, SelectValue
} from "@/components/ui/select";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Alert, AlertDescription } from '@/components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';

import { fetchStockCointegration, fetchCurrencyCointegration, CointegrationItem } from '@/__api__/cointegrationService';
import PairTradingView from './PairTradingView';
import RecentSignals from './RecentSignals';

interface PairTradingProps {
  defaultType?: 'stocks' | 'currencies';
  defaultPeriod?: 'last_6_months' | 'last_12_months';
}

const PairTrading: React.FC<PairTradingProps> = ({
  defaultType = 'stocks',
  defaultPeriod = 'last_6_months'
}) => {
  const [assetType, setAssetType] = useState<'stocks' | 'currencies'>(defaultType);
  const [period, setPeriod] = useState<'last_6_months' | 'last_12_months'>(defaultPeriod);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [cointegrationData, setCointegrationData] = useState<any>(null);
  const [activeTab, setActiveTab] = useState<string>("pairs");
  
  // Selected pair for detailed view
  const [selectedPair, setSelectedPair] = useState<{asset1: string, asset2: string} | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const data = assetType === 'stocks'
          ? await fetchStockCointegration(period)
          : await fetchCurrencyCointegration(period);
        
        setCointegrationData(data);
      } catch (err) {
        console.error(`Error fetching ${assetType} cointegration data:`, err);
        setError(`Falha ao carregar dados de cointegração de ${assetType === 'stocks' ? 'ações' : 'moedas'}. Tente novamente mais tarde.`);
      } finally {
        setLoading(false);
      }
    };
    
    fetchData();
  }, [assetType, period]);

  const handleAssetTypeChange = (value: 'stocks' | 'currencies') => {
    setAssetType(value);
    setSelectedPair(null); // Reset selected pair when changing asset type
  };

  const handlePeriodChange = (value: 'last_6_months' | 'last_12_months') => {
    setPeriod(value);
    setSelectedPair(null); // Reset selected pair when changing period
  };

  const handlePairSelect = (pair: CointegrationItem) => {
    setSelectedPair({
      asset1: pair.asset1,
      asset2: pair.asset2
    });
  };

  // Filter cointegrated pairs
  const cointegratedPairs = cointegrationData?.[period]?.results?.filter(
    (pair: CointegrationItem) => pair.cointegrated
  ) || [];

  return (
    <div className="space-y-4">
      <Tabs defaultValue={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4">
          <TabsTrigger value="pairs">Pares Cointegrados</TabsTrigger>
          <TabsTrigger value="recent">Sinais Recentes</TabsTrigger>
        </TabsList>
        
        <TabsContent value="pairs">
          <Card>
            <CardHeader>
              <CardTitle>Análise de Pair Trading</CardTitle>
              <CardDescription>
                Analise pares cointegrados para oportunidades de arbitragem estatística
              </CardDescription>
              
              <div className="flex flex-col sm:flex-row gap-4 mt-4">
                <Select
                  value={assetType}
                  onValueChange={(value: 'stocks' | 'currencies') => handleAssetTypeChange(value)}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Tipo de Ativo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="stocks">Ações</SelectItem>
                    <SelectItem value="currencies">Moedas</SelectItem>
                  </SelectContent>
                </Select>
                
                <Select
                  value={period}
                  onValueChange={(value: 'last_6_months' | 'last_12_months') => handlePeriodChange(value)}
                >
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Período de Tempo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="last_6_months">Últimos 6 Meses</SelectItem>
                    <SelectItem value="last_12_months">Últimos 12 Meses</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardHeader>
            
            <CardContent>
              {error && (
                <Alert variant="destructive" className="mb-4">
                  <AlertCircle className="h-4 w-4" />
                  <AlertDescription>{error}</AlertDescription>
                </Alert>
              )}
              
              {loading ? (
                <div className="space-y-2">
                  <Skeleton className="h-[400px] w-full" />
                </div>
              ) : (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-lg font-medium mb-2">Pares Cointegrados</h3>
                    <p className="text-sm text-muted-foreground mb-4">
                      Encontrados {cointegratedPairs.length} pares cointegrados de {cointegrationData?.[period]?.results?.length || 0} combinações totais ({
                        cointegrationData?.[period]?.summary?.cointegrated_percentage?.toFixed(2) || 0
                      }%)
                    </p>
                    
                    {cointegratedPairs.length > 0 ? (
                      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
                        {cointegratedPairs.slice(0, 9).map((pair: CointegrationItem, index: number) => (
                          <Card 
                            key={index} 
                            className="cursor-pointer hover:shadow-md transition-shadow"
                            onClick={() => handlePairSelect(pair)}
                          >
                            <CardContent className="p-4">
                              <div className="flex items-center justify-between mb-2">
                                <h4 className="font-medium">{pair.asset1}/{pair.asset2}</h4>
                                <Badge variant="default">Cointegrado</Badge>
                              </div>
                              <div className="space-y-1 text-sm text-muted-foreground">
                                <div className="flex justify-between">
                                  <span>Valor P:</span>
                                  <span>{pair.p_value?.toFixed(4) || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Beta:</span>
                                  <span>{pair.beta?.toFixed(3) || 'N/A'}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Meia-Vida:</span>
                                  <span>{pair.half_life ? Math.round(pair.half_life) : 'N/A'} dias</span>
                                </div>
                              </div>
                            </CardContent>
                          </Card>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-8">
                        <p className="text-muted-foreground">Nenhum par cointegrado encontrado para os critérios selecionados.</p>
                      </div>
                    )}
                  </div>
                  
                  {selectedPair && (
                    <div className="mt-6">
                      <h3 className="text-lg font-medium mb-4">Detalhes do Par: {selectedPair.asset1} / {selectedPair.asset2}</h3>
                      <PairTradingView 
                        asset1={selectedPair.asset1} 
                        asset2={selectedPair.asset2} 
                        period={period}
                      />
                    </div>
                  )}
                </div>
              )}
            </CardContent>
            
            <CardFooter className="flex flex-col items-start">
              <div className="text-sm text-muted-foreground">
                <p className="font-medium mb-1">Sobre Pair Trading</p>
                <p>
                  Pair trading é uma estratégia neutra ao mercado que combina uma posição comprada com uma posição vendida em um par de instrumentos altamente correlacionados. 
                  Quando a correlação enfraquece (spread aumenta), a estratégia opera na suposição de que os preços retornarão à sua norma estatística.
                </p>
              </div>
            </CardFooter>
          </Card>
        </TabsContent>
        
        <TabsContent value="recent">
          <RecentSignals />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PairTrading;