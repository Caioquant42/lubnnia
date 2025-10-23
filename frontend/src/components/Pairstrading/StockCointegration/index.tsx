'use client';

import { AlertCircle } from 'lucide-react';
import { useEffect, useState } from 'react';

import {
  CointegrationData,
  fetchStockCointegration,
} from '__api__/cointegrationService';

import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

import { CointegrationTable } from '../CointegrationTable';

export function StockCointegration() {
  const [data, setData] = useState<CointegrationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState<'last_6_months' | 'last_12_months'>(
    'last_6_months'
  );

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        const result = await fetchStockCointegration(period);
        setData(result);
      } catch (err) {
        console.error('Error fetching stock cointegration data:', err);
        setError('Failed to load cointegration data. Please try again later.');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [period]);
  // Helper function to safely get summary values
  const getSummaryValue = (
    period: 'last_6_months' | 'last_12_months',
    field: string,
    defaultValue: any = 'N/A'
  ) => {
    if (
      !data ||
      !data[period] ||
      !data[period]?.summary ||
      data[period]?.summary?.[field] === undefined
    ) {
      return defaultValue;
    }
    return data[period]?.summary?.[field];
  };

  // Helper function to format percentages safely
  const formatPercentage = (value: any) => {
    return typeof value === 'number' ? `${value.toFixed(2)}%` : 'N/A';
  };

  return (
    <div className='space-y-6'>
      {error && (
        <Alert variant='destructive'>
          <AlertCircle className='h-4 w-4' />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
        <Card>
          <CardHeader>
            <CardTitle>Cointegration Analysis</CardTitle>
            <CardDescription>
              Statistical relationship between stock pairs
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className='text-sm text-muted-foreground'>
              Cointegration helps identify pairs of assets that move together
              over time, making them suitable candidates for long-short
              strategies. These pairs tend to revert to their mean relationship
              even when individual prices are non-stationary.
            </p>
          </CardContent>
        </Card>
        <Card className='md:col-span-2'>
          <CardHeader>
            <CardTitle>Cointegration Summary</CardTitle>
            <CardDescription>
              Statistical overview of analyzed pairs
            </CardDescription>
          </CardHeader>
          <CardContent>
            {loading ? (
              <p>Loading summary data...</p>
            ) : (
              data && (
                <div className='grid grid-cols-2 gap-4'>
                  <div>
                    <h3 className='text-lg font-medium'>Last 6 Months</h3>
                    <div className='mt-2 space-y-1'>
                      <p>
                        Total pairs:{' '}
                        {getSummaryValue('last_6_months', 'total_pairs')}
                      </p>
                      <p>
                        Cointegrated pairs:{' '}
                        {getSummaryValue('last_6_months', 'cointegrated_pairs')}
                        (
                        {formatPercentage(
                          getSummaryValue(
                            'last_6_months',
                            'cointegrated_percentage',
                            null
                          )
                        )}
                        )
                      </p>
                      <p>
                        Non-cointegrated:{' '}
                        {getSummaryValue(
                          'last_6_months',
                          'non_cointegrated_pairs'
                        )}
                        (
                        {formatPercentage(
                          getSummaryValue(
                            'last_6_months',
                            'non_cointegrated_percentage',
                            null
                          )
                        )}
                        )
                      </p>
                    </div>
                  </div>
                  <div>
                    <h3 className='text-lg font-medium'>Last 12 Months</h3>
                    <div className='mt-2 space-y-1'>
                      <p>
                        Total pairs:{' '}
                        {getSummaryValue('last_12_months', 'total_pairs')}
                      </p>
                      <p>
                        Cointegrated pairs:{' '}
                        {getSummaryValue(
                          'last_12_months',
                          'cointegrated_pairs'
                        )}
                        (
                        {formatPercentage(
                          getSummaryValue(
                            'last_12_months',
                            'cointegrated_percentage',
                            null
                          )
                        )}
                        )
                      </p>
                      <p>
                        Non-cointegrated:{' '}
                        {getSummaryValue(
                          'last_12_months',
                          'non_cointegrated_pairs'
                        )}
                        (
                        {formatPercentage(
                          getSummaryValue(
                            'last_12_months',
                            'non_cointegrated_percentage',
                            null
                          )
                        )}
                        )
                      </p>
                    </div>
                  </div>
                </div>
              )
            )}
          </CardContent>
        </Card>{' '}
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Stock Cointegration Analysis</CardTitle>
          <CardDescription>
            Pairs showing statistical evidence of cointegration
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className='text-center py-8'>
              <p className='text-muted-foreground'>Loading data...</p>
            </div>
          ) : (
            <CointegrationTable
              data={
                data && data[period]
                  ? {
                      cointegration: {
                        results: data[period]?.pairs || [],
                        summary: data[period]?.summary || {
                          total_pairs: 0,
                          cointegrated_pairs: 0,
                          cointegrated_percentage: 0,
                        },
                      },
                    }
                  : null
              }
              onPairSelect={(asset1, asset2) => {
                // Handle pair selection if needed
                console.log(`Selected pair: ${asset1}/${asset2}`);
              }}
            />
          )}
        </CardContent>
      </Card>
    </div>
  );
}
