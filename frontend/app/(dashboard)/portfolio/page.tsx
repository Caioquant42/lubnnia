import { DollarSign, PiggyBank, Banknote, Wallet } from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import ChartCard from "@/components/finance/ChartCard";
import StatCard from "@/components/finance/StatCard";
import AllocationChart from "@/components/finance/AllocationChart";
import PortfolioTable from "@/components/finance/PortfolioTable";
import { portfolioData } from "@/data/mock-data";

export default function PortfolioPage() {
  // Calculate total cost basis
  const totalCostBasis = portfolioData.positions.reduce(
    (total, position) => total + position.costBasis,
    0
  );
  
  // Calculate total P&L
  const totalPnL = portfolioData.positions.reduce(
    (total, position) => total + position.pnl,
    0
  );
  
  // Calculate total P&L percent
  const totalPnLPercent = (totalPnL / totalCostBasis) * 100;
  
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Portfolio</h1>
        <p className="text-muted-foreground">
          Manage and track your investment portfolio performance.
        </p>
      </div>
      
      {/* Portfolio Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Value"
          value={portfolioData.totalValue}
          change={portfolioData.pnlTodayPercent}
          icon={<PiggyBank className="h-4 w-4" />}
        />
        <StatCard
          title="Total P&L"
          value={totalPnL}
          change={totalPnLPercent}
          icon={<DollarSign className="h-4 w-4" />}
        />
        <StatCard
          title="Cash Balance"
          value={portfolioData.cashBalance}
          trend="neutral"
          icon={<Wallet className="h-4 w-4" />}
        />
        <StatCard
          title="Cost Basis"
          value={totalCostBasis}
          trend="neutral"
          icon={<Banknote className="h-4 w-4" />}
        />
      </div>
      
      {/* Portfolio Performance Chart and Allocation */}
      <div className="grid gap-6 md:grid-cols-3">
        <ChartCard
          className="md:col-span-2"
          title="Portfolio Performance"
          value={portfolioData.totalValue}
          change={portfolioData.pnlToday}
          changePercent={portfolioData.pnlTodayPercent}
          initialTimePeriod="1M"
          startValue={portfolioData.totalValue - portfolioData.pnlToday}
          volatility={0.01}
        />
        
        <AllocationChart positions={portfolioData.positions} />
      </div>
      
      {/* Portfolio Positions */}
      <PortfolioTable positions={portfolioData.positions} />
    </div>
  );
}