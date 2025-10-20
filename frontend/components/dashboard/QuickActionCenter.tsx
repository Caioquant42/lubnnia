"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Search, 
  TrendingUp, 
  BarChart3, 
  Target, 
  Zap, 
  Activity,
  Eye,
  Calculator,
  ArrowRight,
  Play
} from "lucide-react";
import Link from "next/link";

interface QuickActionCenterProps {
  className?: string;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: React.ReactNode;
  href: string;
  category: "trading" | "analysis" | "screening" | "strategy";
  badge?: string;
  isNew?: boolean;
}

export default function QuickActionCenter({ className }: QuickActionCenterProps) {
  const [activeCategory, setActiveCategory] = useState<string>("all");

  const quickActions: QuickAction[] = [
    {
      id: "screener",
      title: "Market Screener",
      description: "Find stocks matching your criteria",
      icon: <Search className="h-4 w-4" />,
      href: "/screener",
      category: "screening",
      badge: "Most Used"
    },
    {
      id: "pairs-trading",
      title: "Pairs Trading",
      description: "52 active signals available",
      icon: <TrendingUp className="h-4 w-4" />,
      href: "/pairs-trading",
      category: "trading",
      badge: "52 Signals"
    },
    {
      id: "volatility-analysis",
      title: "Volatility Analysis",
      description: "IV percentiles and term structure",
      icon: <Activity className="h-4 w-4" />,
      href: "/volatility",
      category: "analysis"
    },
    {
      id: "options-strategies",
      title: "Options Strategies",
      description: "Covered calls & collar opportunities",
      icon: <Target className="h-4 w-4" />,
      href: "/options/strategies",
      category: "strategy",
      badge: "Hot"
    },
    {
      id: "rrg-analysis",
      title: "RRG Analysis",
      description: "Relative rotation graphs",
      icon: <BarChart3 className="h-4 w-4" />,
      href: "/rrg",
      category: "analysis",
      isNew: true
    },
    {
      id: "portfolio-optimizer",
      title: "Portfolio Optimizer",
      description: "Risk-adjusted allocations",
      icon: <Calculator className="h-4 w-4" />,
      href: "/portfolio/optimizer",
      category: "strategy"
    },
    {
      id: "watchlist",
      title: "Watchlist Manager",
      description: "Track your favorite stocks",
      icon: <Eye className="h-4 w-4" />,
      href: "/watchlist",
      category: "screening"
    },
    {
      id: "backtest",
      title: "Strategy Backtest",
      description: "Test your trading strategies",
      icon: <Play className="h-4 w-4" />,
      href: "/backtest",
      category: "strategy",
      isNew: true
    }
  ];

  const categories = [
    { id: "all", name: "All", count: quickActions.length },
    { id: "trading", name: "Trading", count: quickActions.filter(a => a.category === "trading").length },
    { id: "analysis", name: "Analysis", count: quickActions.filter(a => a.category === "analysis").length },
    { id: "screening", name: "Screening", count: quickActions.filter(a => a.category === "screening").length },
    { id: "strategy", name: "Strategy", count: quickActions.filter(a => a.category === "strategy").length }
  ];

  const filteredActions = activeCategory === "all" 
    ? quickActions 
    : quickActions.filter(action => action.category === activeCategory);

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "trading":
        return <TrendingUp className="h-3 w-3" />;
      case "analysis":
        return <BarChart3 className="h-3 w-3" />;
      case "screening":
        return <Search className="h-3 w-3" />;
      case "strategy":
        return <Target className="h-3 w-3" />;
      default:
        return <Zap className="h-3 w-3" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "trading":
        return "bg-green-100 text-green-700 border-green-200";
      case "analysis":
        return "bg-blue-100 text-blue-700 border-blue-200";
      case "screening":
        return "bg-purple-100 text-purple-700 border-purple-200";
      case "strategy":
        return "bg-orange-100 text-orange-700 border-orange-200";
      default:
        return "bg-gray-100 text-gray-700 border-gray-200";
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Quick Action Center
            </CardTitle>
            <CardDescription>Jump to your most-used tools and analyses</CardDescription>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {/* Category Filters */}
        <div className="flex flex-wrap gap-2 mb-6">
          {categories.map((category) => (
            <Button
              key={category.id}
              variant={activeCategory === category.id ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveCategory(category.id)}
              className="text-xs"
            >
              <span className="flex items-center gap-1">
                {getCategoryIcon(category.id)}
                {category.name}
                <Badge variant="secondary" className="ml-1 text-xs px-1 py-0">
                  {category.count}
                </Badge>
              </span>
            </Button>
          ))}
        </div>

        {/* Quick Actions Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {filteredActions.map((action) => (
            <Link key={action.id} href={action.href}>
              <div className="group p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-3 flex-1">
                    <div className={`p-2 rounded-md ${getCategoryColor(action.category)}`}>
                      {action.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="text-sm font-medium truncate">{action.title}</h4>
                        {action.isNew && (
                          <Badge variant="default" className="text-xs px-1 py-0">
                            New
                          </Badge>
                        )}
                      </div>
                      <p className="text-xs text-muted-foreground mb-2">
                        {action.description}
                      </p>
                      {action.badge && (
                        <Badge variant="outline" className="text-xs">
                          {action.badge}
                        </Badge>
                      )}
                    </div>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity ml-2" />
                </div>
              </div>
            </Link>
          ))}
        </div>

        {filteredActions.length === 0 && (
          <div className="text-center py-8">
            <Search className="h-8 w-8 text-muted-foreground mx-auto mb-2" />
            <p className="text-sm text-muted-foreground">
              No actions found in this category
            </p>
          </div>
        )}

        {/* Quick Stats */}
        <div className="mt-6 pt-4 border-t">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-sm font-medium">52</div>
              <div className="text-xs text-muted-foreground">Active Signals</div>
            </div>
            <div>
              <div className="text-sm font-medium">1,247</div>
              <div className="text-xs text-muted-foreground">Screened Stocks</div>
            </div>
            <div>
              <div className="text-sm font-medium">8</div>
              <div className="text-xs text-muted-foreground">Strategy Tools</div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
