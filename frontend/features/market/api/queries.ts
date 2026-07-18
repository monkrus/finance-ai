import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import {
  MarketIndex,
  MarketBreadth,
  SectorPerformance,
  StockSearchResult,
  CompanyProfile,
  PriceData,
  TechnicalIndicators,
  FinancialStatement,
  FinancialRatios,
  ValuationData,
  EarningsData,
  AnalystRatings,
  PeerComparison,
  AIResearchThesis
} from '../types';
import { NewsItem } from '@/features/dashboard/types';

// Market Overview (Module 2)
export function useGlobalMarkets() {
  return useQuery({
    queryKey: ['market', 'global'],
    queryFn: async () => {
      const res = await apiClient.get<MarketIndex[]>('/api/v1/market/global');
      return res.data;
    },
    staleTime: 60 * 1000,
  });
}

export function useMarketBreadth() {
  return useQuery({
    queryKey: ['market', 'breadth'],
    queryFn: async () => {
      const res = await apiClient.get<MarketBreadth>('/api/v1/market/breadth');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useSectorPerformance() {
  return useQuery({
    queryKey: ['market', 'sectors'],
    queryFn: async () => {
      const res = await apiClient.get<SectorPerformance[]>('/api/v1/market/sectors');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useTrendingStocks() {
  return useQuery({
    queryKey: ['market', 'trending'],
    queryFn: async () => {
      const res = await apiClient.get<MarketIndex[]>('/api/v1/market/trending');
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

// Search (Module 2)
export function useStockSearch(query: string) {
  return useQuery({
    queryKey: ['market', 'search', query],
    queryFn: async () => {
      if (!query) return [];
      const res = await apiClient.get<StockSearchResult[]>(`/api/v1/market/search?q=${encodeURIComponent(query)}`);
      return res.data;
    },
    enabled: query.length > 1,
    staleTime: 5 * 60 * 1000,
  });
}

// Company Specific (Modules 2, 6, 8, 10)
export function useCompanyProfile(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'profile'],
    queryFn: async () => {
      const res = await apiClient.get<CompanyProfile>(`/api/v1/market/company/${ticker}/profile`);
      return res.data;
    },
    staleTime: 60 * 60 * 1000,
  });
}

export function usePriceData(ticker: string, range: string = '1Y') {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'price', range],
    queryFn: async () => {
      const res = await apiClient.get<PriceData[]>(`/api/v1/market/company/${ticker}/price?range=${range}`);
      return res.data;
    },
    staleTime: 60 * 1000,
  });
}

export function useTechIndicators(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'indicators'],
    queryFn: async () => {
      const res = await apiClient.get<TechnicalIndicators>(`/api/v1/market/company/${ticker}/indicators`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useFinancialStatements(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'financials'],
    queryFn: async () => {
      const res = await apiClient.get<{ income: FinancialStatement[], balance: FinancialStatement[], cashflow: FinancialStatement[] }>(`/api/v1/market/company/${ticker}/financials`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useFinancialRatios(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'ratios'],
    queryFn: async () => {
      const res = await apiClient.get<FinancialRatios>(`/api/v1/market/company/${ticker}/ratios`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useValuation(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'valuation'],
    queryFn: async () => {
      const res = await apiClient.get<ValuationData>(`/api/v1/market/company/${ticker}/valuation`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useEarnings(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'earnings'],
    queryFn: async () => {
      const res = await apiClient.get<EarningsData[]>(`/api/v1/market/company/${ticker}/earnings`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useAnalystRatings(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'analysts'],
    queryFn: async () => {
      const res = await apiClient.get<AnalystRatings>(`/api/v1/market/company/${ticker}/analysts`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function usePeerComparison(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'peers'],
    queryFn: async () => {
      const res = await apiClient.get<PeerComparison[]>(`/api/v1/market/company/${ticker}/peers`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useCompanyNews(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'news'],
    queryFn: async () => {
      const res = await apiClient.get<NewsItem[]>(`/api/v1/market/company/${ticker}/news`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useAIResearch(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'ai-research'],
    queryFn: async () => {
      const res = await apiClient.get<AIResearchThesis>(`/api/v1/market/company/${ticker}/ai-research`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}
