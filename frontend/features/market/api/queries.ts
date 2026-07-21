import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/services/api';
import {
  MarketIndex,
  MarketBreadth,
  SectorPerformance,
  TechnicalIndicators,
  FinancialStatement,
  FinancialRatios,
  ValuationData,
  EarningsData,
  AnalystRatings,
  PeerComparison,
  AIResearchThesis,
} from '../types';
import {
  CompanyProfileDTO,
  StockQuoteDTO,
  HistoricalPriceSeriesDTO,
  MarketIndexDTO,
  CompanySearchResultDTO,
  MarketNewsDTO,
  adaptCompanyProfile,
  adaptQuote,
  adaptHistoricalSeries,
  adaptMarketIndex,
  adaptSearchResult,
  adaptCompanyNews,
} from './adapters';

// The backend serves all market data under /api/v1/market-data/* (not /market/*).
const BASE = '/api/v1/market-data';

/* ============================================================= *
 * Reconnected in Sprint 1 (real backend endpoints + adapters)
 * ============================================================= */

// Global Indices — GET /market-data/indices
export function useGlobalMarkets() {
  return useQuery({
    queryKey: ['market', 'global'],
    queryFn: async () => {
      const res = await apiClient.get<MarketIndexDTO[]>(`${BASE}/indices`);
      return res.data.map(adaptMarketIndex);
    },
    staleTime: 60 * 1000,
  });
}

// Company Search — GET /market-data/search?query=
export function useStockSearch(query: string) {
  return useQuery({
    queryKey: ['market', 'search', query],
    queryFn: async () => {
      if (!query) return [];
      const res = await apiClient.get<CompanySearchResultDTO[]>(
        `${BASE}/search?query=${encodeURIComponent(query)}`
      );
      return res.data.map(adaptSearchResult);
    },
    enabled: query.length > 1,
    staleTime: 5 * 60 * 1000,
  });
}

// Company Profile — GET /market-data/profile/{ticker}
export function useCompanyProfile(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'profile'],
    queryFn: async () => {
      const res = await apiClient.get<CompanyProfileDTO>(`${BASE}/profile/${ticker}`);
      return adaptCompanyProfile(res.data);
    },
    staleTime: 60 * 60 * 1000,
  });
}

// Live Quote — GET /market-data/quote/{ticker}
export function useQuote(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'quote'],
    queryFn: async () => {
      const res = await apiClient.get<StockQuoteDTO>(`${BASE}/quote/${ticker}`);
      return adaptQuote(res.data);
    },
    staleTime: 30 * 1000,
  });
}

// Historical Price Chart — GET /market-data/historical/{ticker}
// `range` is retained for the UI selector + query cache key; the backend returns
// the full series and range-windowing is deferred to Sprint 2 (from_date/to_date).
export function usePriceData(ticker: string, range: string = '1Y') {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'price', range],
    queryFn: async () => {
      const res = await apiClient.get<HistoricalPriceSeriesDTO>(`${BASE}/historical/${ticker}`);
      return adaptHistoricalSeries(res.data);
    },
    staleTime: 60 * 1000,
  });
}

// Company News — GET /market-data/news/{ticker}
export function useCompanyNews(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'news'],
    queryFn: async () => {
      const res = await apiClient.get<MarketNewsDTO[]>(`${BASE}/news/${ticker}`);
      return res.data.map(adaptCompanyNews);
    },
    staleTime: 5 * 60 * 1000,
  });
}

/* ============================================================= *
 * Not yet reconnected — no backend endpoint exists yet.
 * Prefix corrected to /market-data so nothing targets the dead
 * /market/* router; these resolve to their existing error/empty
 * states until the backend is built in Sprint 2.
 * ============================================================= */

export function useMarketBreadth() {
  return useQuery({
    queryKey: ['market', 'breadth'],
    queryFn: async () => {
      const res = await apiClient.get<MarketBreadth>(`${BASE}/breadth`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useSectorPerformance() {
  return useQuery({
    queryKey: ['market', 'sectors'],
    queryFn: async () => {
      const res = await apiClient.get<SectorPerformance[]>(`${BASE}/sectors`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useTrendingStocks() {
  return useQuery({
    queryKey: ['market', 'trending'],
    queryFn: async () => {
      const res = await apiClient.get<MarketIndex[]>(`${BASE}/trending`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useTechIndicators(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'indicators'],
    queryFn: async () => {
      const res = await apiClient.get<TechnicalIndicators>(`${BASE}/company/${ticker}/indicators`);
      return res.data;
    },
    staleTime: 5 * 60 * 1000,
  });
}

export function useFinancialStatements(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'financials'],
    queryFn: async () => {
      const res = await apiClient.get<{ income: FinancialStatement[], balance: FinancialStatement[], cashflow: FinancialStatement[] }>(`${BASE}/company/${ticker}/financials`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useFinancialRatios(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'ratios'],
    queryFn: async () => {
      const res = await apiClient.get<FinancialRatios>(`${BASE}/company/${ticker}/ratios`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useValuation(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'valuation'],
    queryFn: async () => {
      const res = await apiClient.get<ValuationData>(`${BASE}/company/${ticker}/valuation`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useEarnings(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'earnings'],
    queryFn: async () => {
      const res = await apiClient.get<EarningsData[]>(`${BASE}/company/${ticker}/earnings`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useAnalystRatings(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'analysts'],
    queryFn: async () => {
      const res = await apiClient.get<AnalystRatings>(`${BASE}/company/${ticker}/analysts`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function usePeerComparison(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'peers'],
    queryFn: async () => {
      const res = await apiClient.get<PeerComparison[]>(`${BASE}/company/${ticker}/peers`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}

export function useAIResearch(ticker: string) {
  return useQuery({
    queryKey: ['market', 'company', ticker, 'ai-research'],
    queryFn: async () => {
      const res = await apiClient.get<AIResearchThesis>(`${BASE}/company/${ticker}/ai-research`);
      return res.data;
    },
    staleTime: 24 * 60 * 60 * 1000,
  });
}
