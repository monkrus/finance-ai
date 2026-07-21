import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import {
  PortfolioSummary,
  Holding,
  PortfolioPerformanceData,
  AllocationData,
  Transaction,
  BenchmarkMetrics
} from '../types';

/**
 * The backend exposes portfolios as REST resources:
 *   GET /api/v1/portfolios/                  -> Portfolio[] (with holdings + transactions)
 *   GET /api/v1/portfolios/{id}/holdings     -> Holding[] (hydrated with market data)
 *   GET /api/v1/portfolios/{id}/analytics    -> { performance, allocation, risk }
 *
 * These adapters map that resource model onto the shapes the portfolio widgets
 * consume, keeping the mapping in the API layer so components stay unchanged.
 */

interface BackendHolding {
  id: number;
  ticker_symbol: string;
  asset_type: string;
  quantity: number;
  average_buy_price: number;
  cost_basis: number;
  realized_gain_loss: number;
  current_price: number | null;
  market_value: number | null;
  unrealized_gain_loss: number | null;
  unrealized_gain_loss_pct: number | null;
  weight: number | null;
  sector: string | null;
  industry: string | null;
  country: string | null;
  currency: string | null;
}

interface BackendTransaction {
  id: number;
  portfolio_id: number;
  holding_id: number | null;
  transaction_type: string;
  execution_date: string;
  quantity: number;
  price_per_unit: number;
  total_amount: number;
}

interface BackendPortfolio {
  id: number;
  name: string;
  holdings: BackendHolding[];
  transactions: BackendTransaction[];
}

interface BackendAnalytics {
  performance: {
    portfolio_value: number;
    total_unrealized_gl: number;
    total_realized_gl: number;
    total_return_pct: number;
    daily_return_pct: number | null;
  };
  allocation: {
    asset_allocation: Record<string, number>;
    sector_allocation: Record<string, number>;
    industry_allocation: Record<string, number>;
    country_allocation: Record<string, number>;
    top_holdings: { ticker: string; weight: number }[];
    diversification_score: number;
  };
  risk: { portfolio_beta: number };
}

const portfolioKeys = {
  primary: ['portfolio', 'primary'] as const,
  analytics: (id: number | null) => ['portfolio', 'analytics', id] as const,
};

/** The user's primary (first) portfolio, or null when they have none yet. */
function usePrimaryPortfolio() {
  return useQuery({
    queryKey: portfolioKeys.primary,
    queryFn: async () => {
      const res = await apiClient.get<BackendPortfolio[]>('/api/v1/portfolios/');
      return (res.data ?? [])[0] ?? null;
    },
    staleTime: 60 * 1000,
  });
}

/**
 * Dependent queries are disabled until the primary portfolio resolves, and a
 * disabled query reports isLoading=false. Without folding the parent's loading
 * state in, widgets would briefly render an empty state instead of a skeleton.
 */
function withParentLoading<T extends { isLoading: boolean }>(
  query: T,
  parentLoading: boolean,
  enabled: boolean
): T {
  return { ...query, isLoading: parentLoading || (enabled && query.isLoading) };
}

function useAnalytics() {
  const primary = usePrimaryPortfolio();
  const id = primary.data?.id ?? null;
  const query = useQuery({
    queryKey: portfolioKeys.analytics(id),
    enabled: id !== null,
    staleTime: 60 * 1000,
    queryFn: async () => {
      const res = await apiClient.get<BackendAnalytics>(`/api/v1/portfolios/${id}/analytics`);
      return res.data;
    },
  });
  return withParentLoading(query, primary.isLoading, id !== null);
}

export function usePortfolioSummary() {
  const analytics = useAnalytics();
  const { data: portfolio } = usePrimaryPortfolio();

  // Once analytics settles with no portfolio, return a zeroed summary (not
  // undefined) so OverviewCards renders its $0 empty state instead of an
  // infinite skeleton.
  const emptySummary: PortfolioSummary = {
    totalValue: 0,
    dailyChange: 0,
    dailyChangePercent: 0,
    totalReturn: 0,
    totalReturnPercent: 0,
    unrealizedGain: 0,
    realizedGain: 0,
    beta: 0,
    diversificationScore: 0,
    holdingsCount: 0,
  };

  return {
    ...analytics,
    data: analytics.data
      ? ({
          totalValue: analytics.data.performance.portfolio_value,
          dailyChange: 0,
          dailyChangePercent: analytics.data.performance.daily_return_pct ?? 0,
          totalReturn:
            analytics.data.performance.total_unrealized_gl +
            analytics.data.performance.total_realized_gl,
          totalReturnPercent: analytics.data.performance.total_return_pct,
          unrealizedGain: analytics.data.performance.total_unrealized_gl,
          realizedGain: analytics.data.performance.total_realized_gl,
          beta: analytics.data.risk.portfolio_beta,
          // Engine returns full float precision; the score is displayed as a
          // "x / 100" figure, so round for presentation.
          diversificationScore: Number(analytics.data.allocation.diversification_score.toFixed(1)),
          holdingsCount: portfolio?.holdings.length ?? 0,
        } as PortfolioSummary)
      : analytics.isLoading
        ? undefined
        : emptySummary,
  };
}

export function usePortfolioHoldings() {
  const primary = usePrimaryPortfolio();
  const id = primary.data?.id ?? null;

  const query = useQuery({
    queryKey: ['portfolio', 'holdings', id],
    enabled: id !== null,
    staleTime: 60 * 1000,
    queryFn: async (): Promise<Holding[]> => {
      const res = await apiClient.get<BackendHolding[]>(`/api/v1/portfolios/${id}/holdings`);
      return (res.data ?? []).map((h) => ({
        id: String(h.id),
        ticker: h.ticker_symbol,
        // The holdings resource carries no company name; the ticker is the
        // authoritative identifier available.
        companyName: h.ticker_symbol,
        quantity: h.quantity,
        averageCost: h.average_buy_price,
        currentPrice: h.current_price ?? h.average_buy_price,
        marketValue: h.market_value ?? 0,
        weight: h.weight ?? 0,
        dailyChangePercent: 0,
        totalReturnPercent: h.unrealized_gain_loss_pct ?? 0,
        unrealizedPL: h.unrealized_gain_loss ?? 0,
        sector: h.sector ?? 'Unknown',
        industry: h.industry ?? 'Unknown',
        country: h.country ?? 'Unknown',
        currency: h.currency ?? 'USD',
      }));
    },
  });

  return withParentLoading(query, primary.isLoading, id !== null);
}

export function usePortfolioPerformance(range: string = '1Y') {
  const primary = usePrimaryPortfolio();
  const analytics = useAnalytics();
  const id = primary.data?.id ?? null;
  const currentValue = analytics.data?.performance.portfolio_value;

  const query = useQuery({
    queryKey: ['portfolio', 'performance', id, range, currentValue],
    enabled: id !== null && currentValue !== undefined,
    staleTime: 5 * 60 * 1000,
    queryFn: async (): Promise<PortfolioPerformanceData[]> => {
      const res = await apiClient.get<BackendPortfolio>(`/api/v1/portfolios/${id}`);
      const txs = [...(res.data?.transactions ?? [])].sort(
        (a, b) => +new Date(a.execution_date) - +new Date(b.execution_date)
      );

      // Invested capital accumulated from the portfolio's real transactions,
      // ending at its current market value. (The chart plots portfolioValue.)
      let cumulative = 0;
      const series: PortfolioPerformanceData[] = txs.map((t) => {
        cumulative += t.total_amount ?? 0;
        return {
          date: new Date(t.execution_date).toISOString().slice(0, 10),
          portfolioValue: Number(cumulative.toFixed(2)),
          benchmarkValue: 0,
        };
      });

      series.push({
        date: new Date().toISOString().slice(0, 10),
        portfolioValue: Number((currentValue ?? 0).toFixed(2)),
        benchmarkValue: 0,
      });

      return series;
    },
  });

  const result = withParentLoading(query, primary.isLoading || analytics.isLoading, id !== null);
  // When settled with no portfolio, expose an empty series (not undefined) so the
  // growth chart renders an empty state rather than a perpetual skeleton.
  return { ...result, data: result.isLoading ? result.data : (result.data ?? []) };
}

export function usePortfolioAllocation(
  type: 'asset' | 'sector' | 'industry' | 'country' = 'asset'
) {
  const analytics = useAnalytics();

  const key = `${type}_allocation` as keyof BackendAnalytics['allocation'];
  const raw = analytics.data?.allocation?.[key] as Record<string, number> | undefined;

  return {
    ...analytics,
    data: raw
      ? (Object.entries(raw).map(([name, weight]) => ({
          name,
          // Backend weights are fractions (0..1); the chart displays percentages.
          value: Number((weight * 100).toFixed(2)),
        })) as AllocationData[])
      // Settled with no portfolio -> empty allocation (not undefined) so the
      // doughnut/heatmap render an empty state instead of a perpetual skeleton.
      : analytics.isLoading
        ? undefined
        : ([] as AllocationData[]),
  };
}

export function usePortfolioTransactions() {
  const primary = usePrimaryPortfolio();
  const id = primary.data?.id ?? null;

  const query = useQuery({
    queryKey: ['portfolio', 'transactions', id],
    enabled: id !== null,
    staleTime: 2 * 60 * 1000,
    queryFn: async (): Promise<Transaction[]> => {
      const res = await apiClient.get<BackendPortfolio>(`/api/v1/portfolios/${id}`);
      const holdingTicker = new Map<number, string>(
        (res.data?.holdings ?? []).map((h) => [h.id, h.ticker_symbol])
      );

      return (res.data?.transactions ?? []).map((t) => ({
        id: String(t.id),
        date: t.execution_date,
        ticker: t.holding_id ? holdingTicker.get(t.holding_id) ?? '—' : '—',
        type: (t.transaction_type ?? '').toLowerCase() as Transaction['type'],
        quantity: t.quantity,
        price: t.price_per_unit,
        total: t.total_amount,
        status: 'completed',
      }));
    },
  });

  return withParentLoading(query, primary.isLoading, id !== null);
}

export function useBenchmarkMetrics() {
  const analytics = useAnalytics();

  return {
    ...analytics,
    data: analytics.data
      ? ({
          // Only beta is computed by the risk engine today; alpha, tracking
          // error and relative return need a benchmark return series the
          // backend does not currently expose.
          alpha: 0,
          trackingError: 0,
          beta: analytics.data.risk.portfolio_beta,
          relativeReturn: 0,
        } as BenchmarkMetrics)
      : undefined,
  };
}
