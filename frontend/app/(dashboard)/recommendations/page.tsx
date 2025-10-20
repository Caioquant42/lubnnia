import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import { TrendingUp, ArrowRight, Globe, DollarSign, Euro, TrendingDown, BarChart3 } from "lucide-react";

export default function RecommendationsPage() {
  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-4">
        <h1 className="text-4xl font-bold tracking-tight bg-gradient-to-r from-blue-600 to-green-600 bg-clip-text text-transparent">
          Recomendações de Analistas
        </h1>
        <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
          Acesse análises especializadas e recomendações de especialistas para diferentes mercados globais. 
          Tome decisões informadas baseadas em dados confiáveis.
        </p>
      </div>

      {/* Market Overview Cards */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {/* Brazil Market */}
        <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-l-4 border-l-green-500">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg">
              <div className="p-2 bg-green-100 rounded-lg group-hover:bg-green-200 transition-colors">
                <TrendingUp className="h-5 w-5 text-green-600" />
              </div>
              Brasil
            </CardTitle>
            <CardDescription className="text-sm">
              Mercado brasileiro - IBOV, B3
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Ativos Analisados:</span>
                <span className="font-medium">150+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Analistas:</span>
                <span className="font-medium">25+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Atualização:</span>
                <span className="font-medium">Diária</span>
              </div>
            </div>
            <Link href="/recommendations/brasil">
              <Button variant="outline" className="w-full group-hover:bg-green-50 group-hover:border-green-300 transition-colors">
                Ver Recomendações
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
          </CardContent>
        </Card>

        {/* US Market */}
        <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg">
              <div className="p-2 bg-blue-100 rounded-lg group-hover:bg-blue-200 transition-colors">
                <DollarSign className="h-5 w-5 text-blue-600" />
              </div>
              Estados Unidos
            </CardTitle>
            <CardDescription className="text-sm">
              S&P 500, NASDAQ, DOW
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Ativos Analisados:</span>
                <span className="font-medium">500+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Analistas:</span>
                <span className="font-medium">50+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Atualização:</span>
                <span className="font-medium">Tempo Real</span>
              </div>
            </div>
            <Button variant="outline" className="w-full group-hover:bg-blue-50 group-hover:border-blue-300 transition-colors" disabled>
              Em Breve
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </CardContent>
        </Card>

        {/* European Market */}
        <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-l-4 border-l-purple-500">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg">
              <div className="p-2 bg-purple-100 rounded-lg group-hover:bg-purple-200 transition-colors">
                <Euro className="h-5 w-5 text-purple-600" />
              </div>
              Europa
            </CardTitle>
            <CardDescription className="text-sm">
              STOXX, FTSE, DAX
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Ativos Analisados:</span>
                <span className="font-medium">300+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Analistas:</span>
                <span className="font-medium">30+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Atualização:</span>
                <span className="font-medium">Diária</span>
              </div>
            </div>
            <Button variant="outline" className="w-full group-hover:bg-purple-50 group-hover:border-purple-300 transition-colors" disabled>
              Em Breve
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </CardContent>
        </Card>

        {/* Global Market */}
        <Card className="group hover:shadow-lg transition-all duration-300 hover:-translate-y-1 border-l-4 border-l-orange-500">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-3 text-lg">
              <div className="p-2 bg-orange-100 rounded-lg group-hover:bg-orange-200 transition-colors">
                <Globe className="h-5 w-5 text-orange-600" />
              </div>
              Mercados Emergentes
            </CardTitle>
            <CardDescription className="text-sm">
              BRICS, Ásia, América Latina
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Ativos Analisados:</span>
                <span className="font-medium">200+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Analistas:</span>
                <span className="font-medium">20+</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Atualização:</span>
                <span className="font-medium">Semanal</span>
              </div>
            </div>
            <Button variant="outline" className="w-full group-hover:bg-orange-50 group-hover:border-orange-300 transition-colors" disabled>
              Em Breve
              <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Features Section */}
      <div className="space-y-6">
        <h2 className="text-2xl font-semibold text-center">Por que usar nossas recomendações?</h2>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          <Card className="text-center p-6 hover:shadow-md transition-shadow">
            <div className="mx-auto w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <BarChart3 className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="font-semibold mb-2">Análise Quantitativa</h3>
            <p className="text-sm text-muted-foreground">
              Dados baseados em modelos matemáticos e análise técnica avançada
            </p>
          </Card>
          
          <Card className="text-center p-6 hover:shadow-md transition-shadow">
            <div className="mx-auto w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <TrendingUp className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="font-semibold mb-2">Atualizações em Tempo Real</h3>
            <p className="text-sm text-muted-foreground">
              Informações sempre atualizadas para tomar as melhores decisões
            </p>
          </Card>
          
          <Card className="text-center p-6 hover:shadow-md transition-shadow">
            <div className="mx-auto w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mb-4">
              <TrendingDown className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="font-semibold mb-2">Gestão de Risco</h3>
            <p className="text-sm text-muted-foreground">
              Análise de risco integrada para proteger seu capital
            </p>
          </Card>
        </div>
      </div>

      {/* CTA Section */}
      <div className="text-center space-y-4 p-8 bg-gradient-to-r from-blue-50 to-green-50 rounded-lg border">
        <h2 className="text-2xl font-semibold">Comece a usar hoje mesmo</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Junte-se a milhares de investidores que já confiam em nossas análises para tomar decisões mais informadas no mercado.
        </p>
        <div className="flex gap-4 justify-center">
          <Button size="lg" className="bg-green-600 hover:bg-green-700">
            Começar Teste Grátis
          </Button>
          <Button variant="outline" size="lg">
            Agendar Demo
          </Button>
        </div>
      </div>
    </div>
  );
}