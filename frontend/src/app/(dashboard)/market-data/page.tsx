import { assetsData, marketIndicesData } from '@/data/mock-data';

import { ChartCard } from '@/components/Finance/ChartCard';
import { MarketDataTable } from '@/components/Finance/MarketDataTable';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

export default function MarketDataPage() {
  return (
    <div className='space-y-6'>
      <div>
        <h1 className='text-2xl font-bold tracking-tight'>Market Data</h1>
        <p className='text-muted-foreground'>
          Access real-time market data, charts, and analytics.
        </p>
      </div>

      {/* Market Index Charts */}
      <div className='grid gap-4 md:grid-cols-2'>
        {marketIndicesData.slice(0, 2).map((index) => (
          <ChartCard
            key={index.id}
            title={index.name}
            value={index.value}
            change={index.change}
            changePercent={index.changePercent}
            initialTimePeriod='1M'
            startValue={index.value - index.change}
          />
        ))}
      </div>
      {/* Market Data Tabs */}
      <Tabs defaultValue='stocks'>
        <div className='flex items-center justify-between'>
          <TabsList>
            <TabsTrigger value='stocks'>Stocks</TabsTrigger>
            <TabsTrigger value='crypto'>Crypto</TabsTrigger>
            <TabsTrigger value='forex'>Forex</TabsTrigger>
            <TabsTrigger value='commodities'>Commodities</TabsTrigger>
          </TabsList>
        </div>

        <TabsContent value='stocks' className='mt-4'>
          <MarketDataTable
            data={assetsData.filter((asset) => asset.type === 'stock')}
          />
        </TabsContent>

        <TabsContent value='crypto' className='mt-4'>
          <MarketDataTable
            data={assetsData.filter((asset) => asset.type === 'crypto')}
          />
        </TabsContent>

        <TabsContent value='forex' className='mt-4'>
          <Card>
            <CardHeader>
              <CardTitle>Forex Data</CardTitle>
              <CardDescription>
                Foreign exchange market data is not available in the demo.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>Upgrade to QuantTrade Pro to access real-time forex data.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value='commodities' className='mt-4'>
          <Card>
            <CardHeader>
              <CardTitle>Commodities Data</CardTitle>
              <CardDescription>
                Commodities market data is not available in the demo.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <p>
                Upgrade to QuantTrade Pro to access real-time commodities data.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
