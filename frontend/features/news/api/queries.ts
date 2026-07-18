import { useQuery, useInfiniteQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import {
  NewsFeedResponse,
  ArticleDetail,
  EventTimelineItem,
  EntityGraph,
  SentimentTrendData,
  PortfolioImpactAlert,
  AISummary
} from '../types';

interface FeedParams {
  category?: string;
  ticker?: string;
  search?: string;
  isPortfolio?: boolean;
}

export function useNewsFeed(params: FeedParams = {}) {
  return useInfiniteQuery({
    queryKey: ['news', 'feed', params],
    queryFn: async ({ pageParam = '' }) => {
      const searchParams = new URLSearchParams();
      if (pageParam) searchParams.append('cursor', pageParam);
      if (params.category) searchParams.append('category', params.category);
      if (params.ticker) searchParams.append('ticker', params.ticker);
      if (params.search) searchParams.append('search', params.search);
      if (params.isPortfolio) searchParams.append('isPortfolio', 'true');

      const res = await apiClient.get<NewsFeedResponse>(`/api/v1/news/feed?${searchParams.toString()}`);
      return res.data;
    },
    getNextPageParam: (lastPage) => lastPage.nextCursor || undefined,
    initialPageParam: '',
    staleTime: 60 * 1000,
  });
}

export function useArticleDetail(id: string) {
  return useQuery({
    queryKey: ['news', 'article', id],
    queryFn: async () => {
      const res = await apiClient.get<ArticleDetail>(`/api/v1/news/article/${id}`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useEventTimeline(ticker?: string) {
  return useQuery({
    queryKey: ['news', 'timeline', ticker],
    queryFn: async () => {
      const url = ticker ? `/api/v1/news/company/${ticker}/timeline` : `/api/v1/news/timeline`;
      const res = await apiClient.get<EventTimelineItem[]>(url);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useEntityGraph(id: string) {
  return useQuery({
    queryKey: ['news', 'entities', id],
    queryFn: async () => {
      const res = await apiClient.get<EntityGraph>(`/api/v1/news/entities/${id}`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useSentimentTrend(ticker?: string, timeframe: 'daily'|'weekly'|'monthly' = 'daily') {
  return useQuery({
    queryKey: ['news', 'sentiment', ticker, timeframe],
    queryFn: async () => {
      const url = ticker 
        ? `/api/v1/news/company/${ticker}/sentiment?timeframe=${timeframe}` 
        : `/api/v1/news/sentiment?timeframe=${timeframe}`;
      const res = await apiClient.get<SentimentTrendData[]>(url);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function usePortfolioImpact() {
  return useQuery({
    queryKey: ['news', 'portfolio-impact'],
    queryFn: async () => {
      const res = await apiClient.get<PortfolioImpactAlert[]>('/api/v1/news/portfolio-impact');
      return res.data;
    },
    staleTime: 60 * 1000,
  });
}

// For company specific AI summary across multiple recent articles
export function useCompanyAISummary(ticker: string) {
  return useQuery({
    queryKey: ['news', 'company', ticker, 'ai-summary'],
    queryFn: async () => {
      const res = await apiClient.get<AISummary>(`/api/v1/news/company/${ticker}/ai-summary`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}
