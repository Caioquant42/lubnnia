"use client";

import { useState, useEffect } from "react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from "@/components/ui/tabs";
import {
  Table,
  TableBody,
  TableCaption,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { Slider } from "@/components/ui/slider";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { 
  Download,
  RefreshCcw,
  Search,
  Calendar,
  Plus,
  X,
  ArrowUpDown,
  Info
} from "lucide-react";
import { Switch } from "@/components/ui/switch";
import RRGChart from "@/components/charts/RRGChart";
import { 
  RRGDataPoint, 
  RRGResponse,
  fetchRRGData, 
  getAvailableRRGDates,
  fetchRRGQuadrantData
} from "@/__api__/rrgApi";

// Sector mapping for color coding (simplified for demo)
const SECTOR_MAPPING: Record<string, string> = {
  "BBDC": "Financials",
  "ITUB": "Financials",
  "BBAS": "Financials",
  "PETR": "Energy",
  "VALE": "Materials",
  "MGLU": "Consumer Discretionary",
  "RENT": "Industrials",
  "WEGE": "Industrials",
  "CSAN": "Energy",
  "ABEV": "Consumer Staples",
  // Add more mappings as needed
};

// Get sector based on symbol prefix
const getSectorForSymbol = (symbol: string): string => {
  for (const [prefix, sector] of Object.entries(SECTOR_MAPPING)) {
    if (symbol.startsWith(prefix)) {
      return sector;
    }
  }
  return "Other";
};

export default function RRGPage() {
  // State for chart data and filters
  const [allData, setAllData] = useState<RRGDataPoint[]>([]);
  const [filteredData, setFilteredData] = useState<RRGDataPoint[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Filters state
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>([]);
  const [availableDates, setAvailableDates] = useState<string[]>([]);
  const [selectedDate, setSelectedDate] = useState<string>("");
  const [selectedQuadrant, setSelectedQuadrant] = useState<string>("all");
  const [minRSRatio, setMinRSRatio] = useState<number | null>(null);
  const [maxRSRatio, setMaxRSRatio] = useState<number | null>(null);
  const [minRSMomentum, setMinRSMomentum] = useState<number | null>(null);
  const [maxRSMomentum, setMaxRSMomentum] = useState<number | null>(null);
  
  // Visualization options
  const [showTrail, setShowTrail] = useState<boolean>(true);
  const [trailLength, setTrailLength] = useState<number>(5);
  const [colorBySector, setColorBySector] = useState<boolean>(false);
  
  // Table view state
  const [activeTab, setActiveTab] = useState<string>("chart");
  const [sortBy, setSortBy] = useState<keyof RRGDataPoint>("symbol");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("asc");
  
  // Chart settings
  const [chartWidth, setChartWidth] = useState<number>(800);
  const [chartHeight, setChartHeight] = useState<number>(600);

  // Quadrant stats
  const [quadrantStats, setQuadrantStats] = useState<{
    leading: number;
    weakening: number;
    lagging: number;
    improving: number;
  }>({
    leading: 0,
    weakening: 0,
    lagging: 0,
    improving: 0
  });

  // Initial data loading
  useEffect(() => {
    async function loadInitialData() {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch available dates for the date filter
        const dates = await getAvailableRRGDates();
        setAvailableDates(dates);
        
        if (dates.length > 0) {
          // Select the most recent date
          const mostRecentDate = dates[dates.length - 1];
          setSelectedDate(mostRecentDate);
          
          // Fetch data for the most recent date
          const response = await fetchRRGData({ date: mostRecentDate, limit: 500 });
          setAllData(response.results);
          setFilteredData(response.results);
          
          // Calculate quadrant statistics
          updateQuadrantStats(response.results);
        }
      } catch (err) {
        console.error("Error loading initial RRG data:", err);
        setError("Failed to load RRG data. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }
    
    loadInitialData();
    
    // Adjust chart dimensions based on window size
    function updateChartDimensions() {
      const width = Math.min(window.innerWidth - 100, 1000);
      const height = Math.min(window.innerHeight - 300, 800);
      setChartWidth(width);
      setChartHeight(height);
    }
    
    updateChartDimensions();
    window.addEventListener("resize", updateChartDimensions);
    
    return () => {
      window.removeEventListener("resize", updateChartDimensions);
    };
  }, []);

  // Update quadrant statistics
  const updateQuadrantStats = (data: RRGDataPoint[]) => {
    const stats = {
      leading: 0,
      weakening: 0,
      lagging: 0,
      improving: 0
    };
    
    data.forEach(item => {
      if (item.quadrant in stats) {
        stats[item.quadrant as keyof typeof stats]++;
      }
    });
    
    setQuadrantStats(stats);
  };

  // Apply filters to data
  useEffect(() => {
    let filtered = [...allData];
    
    // Filter by search term
    if (searchTerm) {
      filtered = filtered.filter(item => 
        item.symbol.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Filter by quadrant
    if (selectedQuadrant && selectedQuadrant !== "all") {
      filtered = filtered.filter(item => item.quadrant === selectedQuadrant);
    }
    
    // Filter by RS Ratio range
    if (minRSRatio !== null) {
      filtered = filtered.filter(item => item.rs_ratio >= minRSRatio);
    }
    if (maxRSRatio !== null) {
      filtered = filtered.filter(item => item.rs_ratio <= maxRSRatio);
    }
    
    // Filter by RS Momentum range
    if (minRSMomentum !== null) {
      filtered = filtered.filter(item => item.rs_momentum >= minRSMomentum);
    }
    if (maxRSMomentum !== null) {
      filtered = filtered.filter(item => item.rs_momentum <= maxRSMomentum);
    }
    
    // Update the filtered data
    setFilteredData(filtered);
    updateQuadrantStats(filtered);
  }, [
    allData,
    searchTerm,
    selectedQuadrant,
    minRSRatio,
    maxRSRatio,
    minRSMomentum,
    maxRSMomentum
  ]);

  // Date selection handler
  const handleDateChange = async (date: string) => {
    try {
      setIsLoading(true);
      setSelectedDate(date);
      
      // Fetch data for the selected date
      const response = await fetchRRGData({ date, limit: 500 });
      setAllData(response.results);
      setFilteredData(response.results);
      updateQuadrantStats(response.results);
    } catch (err) {
      console.error("Error loading data for date:", date, err);
      setError(`Failed to load data for ${date}. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle clicking on a data point
  const handlePointClick = (point: RRGDataPoint) => {
    // Toggle selection of the symbol
    if (selectedSymbols.includes(point.symbol)) {
      setSelectedSymbols(prev => prev.filter(sym => sym !== point.symbol));
    } else {
      setSelectedSymbols(prev => [...prev, point.symbol]);
    }
  };

  // Sort table data
  const handleSort = (column: keyof RRGDataPoint) => {
    if (sortBy === column) {
      // Toggle sort order if same column
      setSortOrder(prev => prev === "asc" ? "desc" : "asc");
    } else {
      // Set new column and default to ascending
      setSortBy(column);
      setSortOrder("asc");
    }
  };

  // Get sorted data for table
  const getSortedData = () => {
    return [...filteredData].sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortOrder === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      if (typeof aValue === 'string' && typeof bValue === 'string') {
        return sortOrder === 'asc' 
          ? aValue.localeCompare(bValue) 
          : bValue.localeCompare(aValue);
      }
      
      return 0;
    });
  };

  // Load quadrant data
  const loadQuadrantData = async (quadrant: string) => {
    try {
      setIsLoading(true);
      setSelectedQuadrant(quadrant);
      
      if (quadrant === "all") {
        // Reset filters and load all data
        const response = await fetchRRGData({ date: selectedDate, limit: 500 });
        setAllData(response.results);
        setFilteredData(response.results);
      } else {
        // Load specific quadrant data
        const response = await fetchRRGQuadrantData(
          quadrant as 'leading' | 'weakening' | 'lagging' | 'improving', 
          100
        );
        setAllData(response.results);
        setFilteredData(response.results);
      }
      
      updateQuadrantStats(allData);
    } catch (err) {
      console.error(`Error loading ${quadrant} quadrant data:`, err);
      setError(`Failed to load ${quadrant} data. Please try again.`);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle adding a symbol to selected symbols
  const handleAddSymbol = (symbol: string) => {
    if (!selectedSymbols.includes(symbol)) {
      setSelectedSymbols(prev => [...prev, symbol]);
    }
  };

  // Handle removing a symbol from selected symbols
  const handleRemoveSymbol = (symbol: string) => {
    setSelectedSymbols(prev => prev.filter(sym => sym !== symbol));
  };

  // Export chart as SVG
  const exportChart = () => {
    const svgElement = document.querySelector('svg');
    if (!svgElement) return;
    
    const svgData = new XMLSerializer().serializeToString(svgElement);
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `RRG_Chart_${selectedDate}.svg`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };
  
  // Export data as CSV
  const exportData = () => {
    const headers = "Symbol,Date,RS_Ratio,RS_Momentum,Quadrant\n";
    const csvContent = filteredData.map(item => 
      `${item.symbol},${item.date},${item.rs_ratio},${item.rs_momentum},${item.quadrant}`
    ).join("\n");
    
    const blob = new Blob([headers + csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.href = url;
    link.download = `RRG_Data_${selectedDate}.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="container mx-auto py-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Relative Rotation Graph (RRG)</h1>
          <p className="text-gray-500">
            Visualize relative strength and momentum of stocks
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={exportChart}
            disabled={isLoading || filteredData.length === 0}
          >
            <Download className="h-4 w-4 mr-2" /> Export Chart
          </Button>
          <Button
            variant="outline"
            onClick={exportData}
            disabled={isLoading || filteredData.length === 0}
          >
            <Download className="h-4 w-4 mr-2" /> Export Data
          </Button>
        </div>
      </div>

      {/* Date Selector */}
      <div className="mb-6">
        <Label>Select Date</Label>
        <div className="flex gap-2 mt-1">
          <Select
            value={selectedDate}
            onValueChange={handleDateChange}
            disabled={isLoading || availableDates.length === 0}
          >
            <SelectTrigger className="w-44">
              <SelectValue placeholder="Select date" />
            </SelectTrigger>
            <SelectContent>
              {availableDates.map((date) => (
                <SelectItem key={date} value={date}>
                  {date}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Button
            variant="secondary"
            onClick={() => {
              if (availableDates.length > 0) {
                handleDateChange(availableDates[availableDates.length - 1]);
              }
            }}
            disabled={isLoading || availableDates.length === 0}
          >
            <RefreshCcw className="h-4 w-4 mr-2" /> Latest
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* Filters sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <Card className="p-4">
            <h2 className="text-xl font-semibold mb-4">Filters</h2>
            
            <div className="space-y-4">
              {/* Search */}
              <div>
                <Label htmlFor="search">Search Symbol</Label>
                <div className="flex items-center mt-1">
                  <Input
                    id="search"
                    placeholder="PETR4, VALE3..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full"
                  />
                  <Search className="h-4 w-4 ml-2 text-gray-400" />
                </div>
              </div>
              
              {/* Quadrant filter */}
              <div>
                <Label>Quadrant</Label>
                <Select value={selectedQuadrant} onValueChange={loadQuadrantData}>
                  <SelectTrigger>
                    <SelectValue placeholder="All Quadrants" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Quadrants</SelectItem>
                    <SelectItem value="leading">Leading</SelectItem>
                    <SelectItem value="weakening">Weakening</SelectItem>
                    <SelectItem value="lagging">Lagging</SelectItem>
                    <SelectItem value="improving">Improving</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              
              {/* RS Ratio range */}
              <div>
                <div className="flex justify-between mb-1">
                  <Label>RS Ratio Range</Label>
                  <div className="text-xs text-gray-500">
                    {minRSRatio !== null ? minRSRatio.toFixed(2) : "Min"} - {maxRSRatio !== null ? maxRSRatio.toFixed(2) : "Max"}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Input 
                    type="number"
                    placeholder="Min"
                    value={minRSRatio !== null ? minRSRatio : ''}
                    onChange={(e) => setMinRSRatio(e.target.value ? parseFloat(e.target.value) : null)}
                    className="w-1/2"
                  />
                  <Input 
                    type="number"
                    placeholder="Max"
                    value={maxRSRatio !== null ? maxRSRatio : ''}
                    onChange={(e) => setMaxRSRatio(e.target.value ? parseFloat(e.target.value) : null)}
                    className="w-1/2"
                  />
                </div>
              </div>
              
              {/* RS Momentum range */}
              <div>
                <div className="flex justify-between mb-1">
                  <Label>RS Momentum Range</Label>
                  <div className="text-xs text-gray-500">
                    {minRSMomentum !== null ? minRSMomentum.toFixed(2) : "Min"} - {maxRSMomentum !== null ? maxRSMomentum.toFixed(2) : "Max"}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Input 
                    type="number"
                    placeholder="Min"
                    value={minRSMomentum !== null ? minRSMomentum : ''}
                    onChange={(e) => setMinRSMomentum(e.target.value ? parseFloat(e.target.value) : null)}
                    className="w-1/2"
                  />
                  <Input 
                    type="number"
                    placeholder="Max"
                    value={maxRSMomentum !== null ? maxRSMomentum : ''}
                    onChange={(e) => setMaxRSMomentum(e.target.value ? parseFloat(e.target.value) : null)}
                    className="w-1/2"
                  />
                </div>
              </div>
              
              {/* Chart options */}
              <Separator className="my-4" />
              <h3 className="font-medium">Chart Options</h3>
              
              <div className="flex items-center justify-between">
                <Label htmlFor="show-trail">Show Trail</Label>
                <Switch 
                  id="show-trail"
                  checked={showTrail}
                  onCheckedChange={setShowTrail}
                />
              </div>
              
              {showTrail && (
                <div>
                  <div className="flex justify-between mb-1">
                    <Label>Trail Length</Label>
                    <span className="text-xs text-gray-500">{trailLength}</span>
                  </div>
                  <Slider 
                    min={2} 
                    max={10} 
                    step={1} 
                    value={[trailLength]} 
                    onValueChange={(value) => setTrailLength(value[0])}
                  />
                </div>
              )}
              
              <div className="flex items-center justify-between">
                <Label htmlFor="color-by-sector">Color by Sector</Label>
                <Switch 
                  id="color-by-sector"
                  checked={colorBySector}
                  onCheckedChange={setColorBySector}
                />
              </div>
            </div>
            
            {/* Quadrant statistics */}
            <div className="mt-6">
              <h3 className="font-medium mb-2">Quadrant Statistics</h3>
              <div className="grid grid-cols-2 gap-2">
                <div className="bg-green-50 p-2 rounded">
                  <div className="text-xs text-gray-600">Leading</div>
                  <div className="text-lg font-semibold text-green-700">
                    {quadrantStats.leading}
                  </div>
                </div>
                <div className="bg-orange-50 p-2 rounded">
                  <div className="text-xs text-gray-600">Weakening</div>
                  <div className="text-lg font-semibold text-orange-700">
                    {quadrantStats.weakening}
                  </div>
                </div>
                <div className="bg-red-50 p-2 rounded">
                  <div className="text-xs text-gray-600">Lagging</div>
                  <div className="text-lg font-semibold text-red-700">
                    {quadrantStats.lagging}
                  </div>
                </div>
                <div className="bg-yellow-50 p-2 rounded">
                  <div className="text-xs text-gray-600">Improving</div>
                  <div className="text-lg font-semibold text-yellow-700">
                    {quadrantStats.improving}
                  </div>
                </div>
              </div>
            </div>
            
            {/* Selected symbols list */}
            <div className="mt-6">
              <h3 className="font-medium mb-2">Selected Symbols ({selectedSymbols.length})</h3>
              <div className="flex flex-wrap gap-1">
                {selectedSymbols.length > 0 ? (
                  selectedSymbols.map(symbol => (
                    <Badge key={symbol} className="flex items-center gap-1">
                      {symbol}
                      <X
                        className="h-3 w-3 cursor-pointer"
                        onClick={() => handleRemoveSymbol(symbol)}
                      />
                    </Badge>
                  ))
                ) : (
                  <div className="text-sm text-gray-500">
                    No symbols selected. Click on data points to select.
                  </div>
                )}
              </div>
              
              {selectedSymbols.length > 0 && (
                <Button
                  variant="outline"
                  className="w-full mt-2"
                  onClick={() => setSelectedSymbols([])}
                >
                  Clear All
                </Button>
              )}
            </div>
          </Card>
        </div>

        {/* Main content */}
        <div className="lg:col-span-3">
          <Card className="p-4">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="mb-4">
                <TabsTrigger value="chart">Chart View</TabsTrigger>
                <TabsTrigger value="table">Table View</TabsTrigger>
              </TabsList>
              
              <div className="mb-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold">
                    {selectedQuadrant === 'all' 
                      ? 'All Stocks' 
                      : `${selectedQuadrant.charAt(0).toUpperCase() + selectedQuadrant.slice(1)} Stocks`}
                  </h2>
                  <div className="text-sm text-gray-500">
                    Showing {filteredData.length} results
                  </div>
                </div>
              </div>
              
              <TabsContent value="chart" className="mt-0">
                {isLoading ? (
                  <div className="flex justify-center items-center h-96">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
                  </div>
                ) : error ? (
                  <div className="flex justify-center items-center h-96">
                    <div className="text-red-500">{error}</div>
                  </div>
                ) : filteredData.length === 0 ? (
                  <div className="flex justify-center items-center h-96">
                    <div className="text-gray-500">No data available for the selected filters.</div>
                  </div>
                ) : (
                  <div className="relative">
                    <RRGChart 
                      data={filteredData}
                      width={chartWidth}
                      height={chartHeight}
                      onPointClick={handlePointClick}
                      selectedSymbols={selectedSymbols}
                      showTrail={showTrail}
                      trailLength={trailLength}
                    />
                    
                    <div className="absolute top-2 right-2 bg-white/80 backdrop-blur-sm p-2 rounded shadow text-xs">
                      <div className="font-bold mb-1">Date: {selectedDate}</div>
                      <div className="grid grid-cols-2 gap-x-4">
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                          <span>Leading</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 bg-orange-500 rounded-full"></div>
                          <span>Weakening</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 bg-red-500 rounded-full"></div>
                          <span>Lagging</span>
                        </div>
                        <div className="flex items-center gap-1">
                          <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                          <span>Improving</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </TabsContent>
              
              <TabsContent value="table" className="mt-0">
                {isLoading ? (
                  <div className="flex justify-center items-center h-96">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900"></div>
                  </div>
                ) : error ? (
                  <div className="flex justify-center items-center h-96">
                    <div className="text-red-500">{error}</div>
                  </div>
                ) : filteredData.length === 0 ? (
                  <div className="flex justify-center items-center h-96">
                    <div className="text-gray-500">No data available for the selected filters.</div>
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <Table>
                      <TableHeader>
                        <TableRow>
                          <TableHead className="w-12"></TableHead>
                          <TableHead>
                            <button 
                              className="flex items-center"
                              onClick={() => handleSort('symbol')}
                            >
                              Symbol
                              {sortBy === 'symbol' && (
                                <ArrowUpDown className={`ml-1 h-3 w-3 ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
                              )}
                            </button>
                          </TableHead>
                          <TableHead>
                            <button 
                              className="flex items-center"
                              onClick={() => handleSort('rs_ratio')}
                            >
                              RS Ratio
                              {sortBy === 'rs_ratio' && (
                                <ArrowUpDown className={`ml-1 h-3 w-3 ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
                              )}
                            </button>
                          </TableHead>
                          <TableHead>
                            <button 
                              className="flex items-center"
                              onClick={() => handleSort('rs_momentum')}
                            >
                              RS Momentum
                              {sortBy === 'rs_momentum' && (
                                <ArrowUpDown className={`ml-1 h-3 w-3 ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
                              )}
                            </button>
                          </TableHead>
                          <TableHead>
                            <button 
                              className="flex items-center"
                              onClick={() => handleSort('quadrant')}
                            >
                              Quadrant
                              {sortBy === 'quadrant' && (
                                <ArrowUpDown className={`ml-1 h-3 w-3 ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
                              )}
                            </button>
                          </TableHead>
                          <TableHead>
                            <button 
                              className="flex items-center"
                              onClick={() => handleSort('date')}
                            >
                              Date
                              {sortBy === 'date' && (
                                <ArrowUpDown className={`ml-1 h-3 w-3 ${sortOrder === 'desc' ? 'rotate-180' : ''}`} />
                              )}
                            </button>
                          </TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {getSortedData().map((item, index) => (
                          <TableRow key={`${item.symbol}-${index}`}>
                            <TableCell>
                              {selectedSymbols.includes(item.symbol) ? (
                                <Button 
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => handleRemoveSymbol(item.symbol)}
                                >
                                  <X className="h-4 w-4" />
                                </Button>
                              ) : (
                                <Button 
                                  variant="ghost"
                                  size="icon"
                                  className="h-6 w-6"
                                  onClick={() => handleAddSymbol(item.symbol)}
                                >
                                  <Plus className="h-4 w-4" />
                                </Button>
                              )}
                            </TableCell>
                            <TableCell className="font-medium">{item.symbol}</TableCell>
                            <TableCell>{item.rs_ratio.toFixed(2)}</TableCell>
                            <TableCell>{item.rs_momentum.toFixed(2)}</TableCell>
                            <TableCell>
                              <Badge className={`
                                ${item.quadrant === 'leading' ? 'bg-green-500' : ''}
                                ${item.quadrant === 'weakening' ? 'bg-orange-500' : ''}
                                ${item.quadrant === 'lagging' ? 'bg-red-500' : ''}
                                ${item.quadrant === 'improving' ? 'bg-yellow-500' : ''}
                              `}>
                                {item.quadrant.charAt(0).toUpperCase() + item.quadrant.slice(1)}
                              </Badge>
                            </TableCell>
                            <TableCell>{item.date}</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </div>
                )}
              </TabsContent>
            </Tabs>
          </Card>
        </div>
      </div>
    </div>
  );
}