import { apiClient } from '@/services/api';
import {
  DashboardState,
  KPI,
  MarketIndex,
  NewsItem,
  AIInsight
} from '../types';

/**
 * The backend exposes every dashboard section under /api/v1/dashboard/* and
 * returns a generic widget envelope: { widgets: WidgetSchema[] }.
 * This module adapts that envelope into the domain shapes the dashboard
 * widgets consume, keeping the mapping in the API layer so the presentation
 * components stay unchanged.
 */
interface WidgetSchema {
  title: string;
  subtitle: string | null;
  value: unknown;
  formatted_value: string | null;
  change: number | null;
  change_percent: number | null;
  trend: string | null;
  status: string | null;
  priority: number | null;
  icon: string | null;
  color: string | null;
  last_updated: string;
  metadata: Record<string, unknown> | null;
}

interface WidgetSection {
  widgets: WidgetSchema[];
}

async function getSection(path: string): Promise<WidgetSchema[]> {
  const res = await apiClient.get<WidgetSection>(path);
  return res.data?.widgets ?? [];
}

function toNumber(value: unknown): number {
  if (typeof value === 'number') return Number.isFinite(value) ? value : 0;
  const parsed = parseFloat(String(value ?? '').replace(/[^0-9.-]/g, ''));
  return Number.isFinite(parsed) ? parsed : 0;
}

function toTrend(trend: string | null): KPI['trend'] {
  if (trend === 'up') return 'up';
  if (trend === 'down') return 'down';
  return 'neutral';
}

function findWidget(widgets: WidgetSchema[], title: string): WidgetSchema | undefined {
  return widgets.find((w) => w.title.toLowerCase() === title.toLowerCase());
}

/** Infer a display format from the backend's pre-formatted value. */
function inferFormat(widget: WidgetSchema): KPI['format'] {
  const formatted = widget.formatted_value ?? '';
  if (formatted.includes('$')) return 'currency';
  if (formatted.includes('%')) return 'percentage';
  return 'number';
}

// The overview KPIs and the overview summary are both derived from the same
// /dashboard/overview payload. Fetch it once (raw widgets) and let each hook map
// what it needs via react-query `select`, so the endpoint is not requested twice.
function mapOverview(widgets: WidgetSchema[]): DashboardState {
  const netWorth = findWidget(widgets, 'Net Worth');
  const portfolio = findWidget(widgets, 'Total Portfolio Value');
  const health = findWidget(widgets, 'Financial Health');
  const cash = findWidget(widgets, 'Cash Balance');

  return {
    netWorth: toNumber(netWorth?.value),
    netWorthChange: netWorth?.change_percent ?? 0,
    portfolioValue: toNumber(portfolio?.value),
    portfolioChange: portfolio?.change_percent ?? 0,
    cashBalance: toNumber(cash?.value),
    wealthScore: toNumber(health?.value),
  };
}

function mapKPIs(widgets: WidgetSchema[]): KPI[] {
  return widgets.map((w) => ({
    id: w.title,
    label: w.title,
    value: toNumber(w.value),
    delta: w.change_percent ?? 0,
    trend: toTrend(w.trend),
    format: inferFormat(w),
  }));
}

export const dashboardApi = {
  // Raw overview section — shared by the overview and KPI hooks (single fetch).
  getOverviewSection: (): Promise<WidgetSchema[]> => getSection('/api/v1/dashboard/overview'),
  mapOverview,
  mapKPIs,

  getMarketOverview: async (): Promise<MarketIndex[]> => {
    const widgets = await getSection('/api/v1/dashboard/market');
    return widgets.map((w) => ({
      // Backend titles market widgets as "<SYMBOL> Index".
      symbol: w.title.replace(/\s+Index$/i, ''),
      name: w.subtitle ?? w.title,
      price: toNumber(w.value),
      change: w.change ?? 0,
      changePercent: w.change_percent ?? 0,
    }));
  },

  getNews: async (): Promise<NewsItem[]> => {
    const widgets = await getSection('/api/v1/dashboard/news');
    return widgets.map((w, i) => ({
      id: `${w.title}-${i}`,
      title: w.subtitle ?? w.title,
      summary: w.formatted_value ?? '',
      source: w.title,
      url: typeof w.metadata?.url === 'string' ? (w.metadata.url as string) : '#',
      publishedAt: w.last_updated,
      sentiment:
        w.status === 'success' ? 'positive' : w.status === 'danger' ? 'negative' : 'neutral',
      importance: (w.priority ?? 0) > 1 ? 'high' : (w.priority ?? 0) === 1 ? 'medium' : 'low',
    }));
  },

  getAIInsights: async (): Promise<AIInsight[]> => {
    const widgets = await getSection('/api/v1/dashboard/insights');
    return widgets.map((w, i) => ({
      id: `${w.title}-${i}`,
      title: w.title,
      description: String(w.value ?? w.formatted_value ?? ''),
      category: 'market',
      timestamp: w.last_updated,
      confidence:
        typeof w.metadata?.confidence === 'number' ? (w.metadata.confidence as number) : 0.8,
    }));
  },
};
