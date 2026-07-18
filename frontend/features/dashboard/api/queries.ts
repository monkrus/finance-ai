import { useQuery } from '@tanstack/react-query';
import { dashboardApi } from './index';

export const dashboardKeys = {
  all: ['dashboard'] as const,
  overview: () => [...dashboardKeys.all, 'overview'] as const,
  kpis: () => [...dashboardKeys.all, 'kpis'] as const,
  market: () => [...dashboardKeys.all, 'market'] as const,
  news: () => [...dashboardKeys.all, 'news'] as const,
  ai: () => [...dashboardKeys.all, 'ai'] as const,
};

export function useDashboardOverview() {
  return useQuery({
    queryKey: dashboardKeys.overview(),
    queryFn: dashboardApi.getOverview,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
}

export function useKPIs() {
  return useQuery({
    queryKey: dashboardKeys.kpis(),
    queryFn: dashboardApi.getKPIs,
    staleTime: 1000 * 60 * 2,
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
