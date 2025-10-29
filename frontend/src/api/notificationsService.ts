import recommendationsApi from './recommendationsApi';
import { fetchStocksVariationData, StockVariationData } from './variationApi';
import { fetchStocksVolatilityData, StockVolatilityData } from './volatilityApi';

export interface RealTimeNotification {
  id: string;
  type: 'recommendation' | 'variation' | 'volatility' | 'info';
  title: string;
  message: string;
  read: boolean;
  timestamp: Date;
  symbol?: string;
  value?: number;
  change?: number;
  severity: 'low' | 'medium' | 'high';
  category: 'ibov' | 'variation' | 'volatility' | 'system';
}

export interface NotificationsSummary {
  total: number;
  unread: number;
  byCategory: {
    recommendation: number;
    variation: number;
    volatility: number;
    info: number;
  };
}

class NotificationsService {
  private notifications: RealTimeNotification[] = [];
  private lastUpdate: Date | null = null;
  private updateInterval: number = 5 * 60 * 1000; // 5 minutes

  /**
   * Fetch all real-time notifications from various data sources
   */
  async fetchRealTimeNotifications(): Promise<RealTimeNotification[]> {
    try {
      // Check if we need to update (avoid too frequent API calls)
      const now = new Date();
      if (this.lastUpdate && (now.getTime() - this.lastUpdate.getTime()) < this.updateInterval) {
        return this.notifications;
      }

      // Fetch data from multiple sources in parallel
      const [ibovData, variationData, volatilityData] = await Promise.allSettled([
        recommendationsApi.getIbovAnalysis(),
        fetchStocksVariationData({ sort_by: 'variation', sort_order: 'desc', limit: 20 }),
        fetchStocksVolatilityData({ sort_by: 'iv_ewma_ratio', sort_order: 'desc', limit: 20 })
      ]);

      const newNotifications: RealTimeNotification[] = [];

      // Process IBOV recommendations (top 3 strong buy recommendations)
      if (ibovData.status === 'fulfilled' && ibovData.value?.data?.results) {
        const strongBuyStocks = ibovData.value.data.results
          .filter((stock: any) => stock.recommendationKey === 'strong_buy')
          .slice(0, 3);

        strongBuyStocks.forEach((stock: any, index: number) => {
          newNotifications.push({
            id: `ibov_${stock.ticker}_${Date.now()}_${index}`,
            type: 'recommendation',
            title: `Compra Forte: ${stock.ticker}`,
            message: `${stock.ticker} com recomendação de compra forte. Retorno esperado: ${(stock.return_target_consensus * 100).toFixed(1)}%. Preço atual: R$ ${stock.currentPrice?.toFixed(2) || 'N/A'}`,
            read: false,
            timestamp: new Date(Date.now() - (index + 1) * 10 * 60 * 1000), // Stagger timestamps
            symbol: stock.ticker,
            value: stock.return_target_consensus,
            change: stock.return_target_consensus * 100,
            severity: 'high',
            category: 'ibov'
          });
        });
      }

      // Process stock variations (top positive and negative variations)
      if (variationData.status === 'fulfilled' && variationData.value?.results) {
        const topPositive = variationData.value.results
          .filter((stock: StockVariationData) => stock.variation > 0)
          .slice(0, 2);

        const topNegative = variationData.value.results
          .filter((stock: StockVariationData) => stock.variation < 0)
          .slice(0, 2);

        // Add positive variations
        topPositive.forEach((stock: StockVariationData, index: number) => {
          newNotifications.push({
            id: `variation_pos_${stock.symbol}_${Date.now()}_${index}`,
            type: 'variation',
            title: `Alta Expressiva: ${stock.symbol}`,
            message: `${stock.symbol} subiu ${stock.variation.toFixed(2)}% hoje. Preço atual: R$ ${stock.close?.toFixed(2) || 'N/A'}`,
            read: false,
            timestamp: new Date(Date.now() - (index + 1) * 15 * 60 * 1000),
            symbol: stock.symbol,
            value: stock.close,
            change: stock.variation,
            severity: stock.variation > 5 ? 'high' : 'medium',
            category: 'variation'
          });
        });

        // Add negative variations
        topNegative.forEach((stock: StockVariationData, index: number) => {
          newNotifications.push({
            id: `variation_neg_${stock.symbol}_${Date.now()}_${index}`,
            type: 'variation',
            title: `Queda Expressiva: ${stock.symbol}`,
            message: `${stock.symbol} caiu ${Math.abs(stock.variation).toFixed(2)}% hoje. Preço atual: R$ ${stock.close?.toFixed(2) || 'N/A'}`,
            read: false,
            timestamp: new Date(Date.now() - (index + 1) * 20 * 60 * 1000),
            symbol: stock.symbol,
            value: stock.close,
            change: stock.variation,
            severity: Math.abs(stock.variation) > 5 ? 'high' : 'medium',
            category: 'variation'
          });
        });
      }

      // Process volatility alerts (stocks with highest IV/EWMA ratios)
      if (volatilityData.status === 'fulfilled' && volatilityData.value?.results) {
        const highVolatilityStocks = volatilityData.value.results
          .filter((stock: StockVolatilityData) => 
            stock.iv_ewma_ratio > 1.5 && stock.iv_1y_percentile > 80
          )
          .slice(0, 3);

        highVolatilityStocks.forEach((stock: StockVolatilityData, index: number) => {
          newNotifications.push({
            id: `volatility_${stock.symbol}_${Date.now()}_${index}`,
            type: 'volatility',
            title: `Alta Volatilidade: ${stock.symbol}`,
            message: `${stock.symbol} com IV elevada: ${stock.iv_current.toFixed(1)}% (percentil ${stock.iv_1y_percentile.toFixed(0)}). Razão IV/EWMA: ${stock.iv_ewma_ratio.toFixed(2)}`,
            read: false,
            timestamp: new Date(Date.now() - (index + 1) * 25 * 60 * 1000),
            symbol: stock.symbol,
            value: stock.iv_current,
            change: stock.iv_ewma_ratio,
            severity: stock.iv_1y_percentile > 90 ? 'high' : 'medium',
            category: 'volatility'
          });
        });
      }

      // Add system info notifications
      newNotifications.push({
        id: `system_market_update_${Date.now()}`,
        type: 'info',
        title: 'Atualização de Mercado',
        message: 'Dados de mercado atualizados com as últimas recomendações, variações e indicadores de volatilidade.',
        read: false,
        timestamp: new Date(Date.now() - 30 * 60 * 1000), // 30 minutes ago
        severity: 'low',
        category: 'system'
      });

      // Sort notifications by timestamp (newest first)
      this.notifications = newNotifications.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
      this.lastUpdate = now;

      return this.notifications;
    } catch (error) {
      console.error('Error fetching real-time notifications:', error);
      // Return cached notifications if available, otherwise return empty array
      return this.notifications.length > 0 ? this.notifications : [];
    }
  }

  /**
   * Get notifications summary
   */
  getNotificationsSummary(): NotificationsSummary {
    const total = this.notifications.length;
    const unread = this.notifications.filter(n => !n.read).length;
    
    const byCategory = {
      recommendation: this.notifications.filter(n => n.category === 'ibov').length,
      variation: this.notifications.filter(n => n.category === 'variation').length,
      volatility: this.notifications.filter(n => n.category === 'volatility').length,
      info: this.notifications.filter(n => n.category === 'system').length
    };

    return { total, unread, byCategory };
  }

  /**
   * Mark notification as read
   */
  markAsRead(notificationId: string): void {
    const notification = this.notifications.find(n => n.id === notificationId);
    if (notification) {
      notification.read = true;
    }
  }

  /**
   * Mark all notifications as read
   */
  markAllAsRead(): void {
    this.notifications.forEach(notification => {
      notification.read = true;
    });
  }

  /**
   * Get notifications by category
   */
  getNotificationsByCategory(category: 'ibov' | 'variation' | 'volatility' | 'system'): RealTimeNotification[] {
    return this.notifications.filter(n => n.category === category);
  }

  /**
   * Get unread notifications count
   */
  getUnreadCount(): number {
    return this.notifications.filter(n => !n.read).length;
  }

  /**
   * Clear old notifications (older than 24 hours)
   */
  clearOldNotifications(): void {
    const twentyFourHoursAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
    this.notifications = this.notifications.filter(n => n.timestamp > twentyFourHoursAgo);
  }
}

// Export singleton instance
export const notificationsService = new NotificationsService();
export default notificationsService; 