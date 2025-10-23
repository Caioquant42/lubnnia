import { Badge } from '@/components/ui/badge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

interface PairStatisticsProps {
  stats: {
    p_value?: number;
    beta?: number;
    correlation?: number;
    half_life?: number;
    mean?: number;
    std_dev?: number;
    sharpe_ratio?: number;
    max_drawdown?: number;
    num_trades?: number;
    win_rate?: number;
    profit_factor?: number;
    [key: string]: any;
  };
  asset1: string;
  asset2: string;
}

const PairStatistics: React.FC<PairStatisticsProps> = ({
  stats,
  asset1,
  asset2,
}) => {
  // Format numbers properly
  const formatNumber = (
    num: number | undefined,
    precision: number = 4
  ): string => {
    if (num === undefined || num === null) return 'N/A';

    // For percentages
    if (Math.abs(num) < 0.01) {
      return num.toFixed(precision);
    }

    return num.toFixed(2);
  };

  // Determine cointegration status based on p-value
  const getCointStatus = () => {
    if (stats?.p_value === undefined) return 'Unknown';
    return stats.p_value < 0.05 ? 'Cointegrated' : 'Not Cointegrated';
  };
  // Get appropriate badge variant
  const getCointBadge = () => {
    if (stats?.p_value === undefined) return 'secondary';
    return stats.p_value < 0.05 ? 'default' : 'destructive';
  };

  return (
    <div className='space-y-4'>
      <div className='flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between'>
        <h3 className='text-lg font-medium'>
          Pair Statistics: {asset1}/{asset2}
        </h3>
        <Badge variant={getCointBadge()}>{getCointStatus()}</Badge>
      </div>

      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Metric</TableHead>
            <TableHead className='text-right'>Value</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          <TableRow>
            <TableCell>P-Value</TableCell>
            <TableCell className='text-right'>
              {formatNumber(stats?.p_value)}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Beta</TableCell>
            <TableCell className='text-right'>
              {formatNumber(stats?.beta)}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Correlation</TableCell>
            <TableCell className='text-right'>
              {formatNumber(stats?.correlation)}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Half-Life (Days)</TableCell>
            <TableCell className='text-right'>
              {stats?.half_life ? Math.round(stats.half_life) : 'N/A'}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Mean</TableCell>
            <TableCell className='text-right'>
              {formatNumber(stats?.mean)}
            </TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Standard Deviation</TableCell>
            <TableCell className='text-right'>
              {formatNumber(stats?.std_dev)}
            </TableCell>
          </TableRow>
          {stats?.sharpe_ratio !== undefined && (
            <TableRow>
              <TableCell>Sharpe Ratio</TableCell>
              <TableCell className='text-right'>
                {formatNumber(stats.sharpe_ratio)}
              </TableCell>
            </TableRow>
          )}
          {stats?.max_drawdown !== undefined && (
            <TableRow>
              <TableCell>Max Drawdown</TableCell>
              <TableCell className='text-right'>
                {formatNumber(stats.max_drawdown, 2)}%
              </TableCell>
            </TableRow>
          )}
          {stats?.num_trades !== undefined && (
            <TableRow>
              <TableCell>Number of Trades</TableCell>
              <TableCell className='text-right'>{stats.num_trades}</TableCell>
            </TableRow>
          )}
          {stats?.win_rate !== undefined && (
            <TableRow>
              <TableCell>Win Rate</TableCell>
              <TableCell className='text-right'>
                {formatNumber(stats.win_rate * 100, 2)}%
              </TableCell>
            </TableRow>
          )}
          {stats?.profit_factor !== undefined && (
            <TableRow>
              <TableCell>Profit Factor</TableCell>
              <TableCell className='text-right'>
                {formatNumber(stats.profit_factor)}
              </TableCell>
            </TableRow>
          )}
        </TableBody>
      </Table>

      <div className='text-sm text-muted-foreground mt-2'>
        <p>
          P-value &lt; 0.05 indicates the assets are likely cointegrated, making
          them suitable for pair trading.
        </p>
      </div>
    </div>
  );
};

export { PairStatistics };
