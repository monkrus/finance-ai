import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from './index';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  overview: () => [...dashboardKeys.all, 'overview'] as const,
  market: () => [...dashboardKeys.all, 'market'] as const,
  news: () => [...dashboardKeys.all, 'news'] as const,
  ai: () => [...dashboardKeys.all, 'ai'] as const,
};

// Both the overview summary and the KPI row derive from the same
// /dashboard/overview payload. They share one query key + fetcher so react-query
// makes a single request and each hook maps its slice via `select`.
export function useDashboardOverview() {
  return useQuery({
    queryKey: dashboardKeys.overview(),
    queryFn: dashboardApi.getOverviewSection,
    select: dashboardApi.mapOverview,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useKPIs() {
  return useQuery({
    queryKey: dashboardKeys.overview(),
    queryFn: dashboardApi.getOverviewSection,
    select: dashboardApi.mapKPIs,
    staleTime: 1000 * 60 * 5,
  });
}

export function useMarketOverview() {
  return useQuery({
    queryKey: dashboardKeys.market(),
    queryFn: dashboardApi.getMarketOverview,
    staleTime: 1000 * 30, // 30 seconds for market data
  });
}

export function useDashboardNews() {
  return useQuery({
    queryKey: dashboardKeys.news(),
    queryFn: dashboardApi.getNews,
    staleTime: 1000 * 60 * 5,
  });
}

export function useAIInsights() {
  return useQuery({
    queryKey: dashboardKeys.ai(),
    queryFn: dashboardApi.getAIInsights,
    staleTime: 1000 * 60 * 60, // 1 hour for AI insights
  });
}
