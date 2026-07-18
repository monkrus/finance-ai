/**
 * Market API adapter layer.
 *
 * The backend (`/api/v1/market-data/*`) returns snake_case payloads shaped by
 * the Pydantic models in `backend/app/market_data/models.py`. The presentation
 * components consume the camelCase view models declared in `../types`.
 *
 * All translation between the two lives here so the query hooks stay thin and
 * the components never see a backend shape. Every mapper is a pure function and
 * defaults missing/optional fields so a partial backend response can never crash
 * a component (e.g. `.replace()` on a null website, or `/ 1e9` on a null cap).
 */
import {
  CompanyProfile,
  Quote,
  PriceData,
  MarketIndex,
  StockSearchResult,
} from '../types';
import { NewsItem } from '@/features/dashboard/types';

/* ------------------------------------------------------------------ *
 * Backend DTO shapes (snake_case) — mirror backend/app/market_data/models.py
 * ------------------------------------------------------------------ */

export interface CompanyProfileDTO {
  ticker: string;
  company_name: string;
  currency?: string | null;
  exchange?: string | null;
  industry?: string | null;
  sector?: string | null;
  website?: string | null;
  description?: string | null;
  ceo?: string | null;
  market_cap?: number | null;
  beta?: number | null;
  price?: number | null;
  image?: string | null;
  is_actively_trading?: boolean | null;
}

export interface StockQuoteDTO {
  ticker: string;
  price: number;
  change?: number | null;
  change_percent?: number | null;
  day_low?: number | null;
  day_high?: number | null;
  year_low?: number | null;
  year_high?: number | null;
  market_cap?: number | null;
  volume?: number | null;
  avg_volume?: number | null;
  exchange?: string | null;
  timestamp?: number | null;
}

export interface HistoricalPriceDTO {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  adj_close?: number | null;
  volume: number;
}

export interface HistoricalPriceSeriesDTO {
  ticker: string;
  prices: HistoricalPriceDTO[];
}

export interface MarketIndexDTO {
  symbol: string;
  name: string;
  price: number;
  change?: number | null;
  change_percent?: number | null;
}

export interface CompanySearchResultDTO {
  ticker: string;
  name?: string | null;
  exchange?: string | null;
}

export interface MarketNewsDTO {
  id: string;
  symbol: string;
  title: string;
  published_at: string;
  source: string;
  url: string;
  summary?: string | null;
}

/* ------------------------------------------------------------------ *
 * Mappers (DTO -> view model)
 * ------------------------------------------------------------------ */

export function adaptCompanyProfile(dto: CompanyProfileDTO): CompanyProfile {
  return {
    ticker: dto.ticker,
    companyName: dto.company_name,
    description: dto.description ?? '',
    logo: dto.image ?? '',
    exchange: dto.exchange ?? '',
    industry: dto.industry ?? '',
    sector: dto.sector ?? '',
    ceo: dto.ceo ?? '',
    // Not provided by the backend market-data profile; default so the
    // presentation components render without crashing.
    employees: 0,
    headquarters: '',
    website: dto.website ?? '',
    marketCap: dto.market_cap ?? 0,
    enterpriseValue: 0,
  };
}

export function adaptQuote(dto: StockQuoteDTO): Quote {
  return {
    ticker: dto.ticker,
    price: dto.price,
    change: dto.change ?? 0,
    changePercent: dto.change_percent ?? 0,
    dayLow: dto.day_low ?? 0,
    dayHigh: dto.day_high ?? 0,
    yearLow: dto.year_low ?? 0,
    yearHigh: dto.year_high ?? 0,
    marketCap: dto.market_cap ?? 0,
    volume: dto.volume ?? 0,
    avgVolume: dto.avg_volume ?? 0,
    exchange: dto.exchange ?? '',
    timestamp: dto.timestamp ?? 0,
  };
}

export function adaptHistoricalSeries(dto: HistoricalPriceSeriesDTO): PriceData[] {
  return (dto.prices ?? []).map((p) => ({
    time: p.date,
    open: p.open,
    high: p.high,
    low: p.low,
    close: p.close,
    volume: p.volume,
  }));
}

function trendFrom(changePercent: number): MarketIndex['trend'] {
  if (changePercent > 0) return 'up';
  if (changePercent < 0) return 'down';
  return 'neutral';
}

export function adaptMarketIndex(dto: MarketIndexDTO): MarketIndex {
  const changePercent = dto.change_percent ?? 0;
  return {
    symbol: dto.symbol,
    name: dto.name,
    price: dto.price,
    change: dto.change ?? 0,
    changePercent,
    // The market-data indices endpoint has no intraday series; the component
    // guards on length and simply omits the sparkline when empty.
    sparkline: [],
    trend: trendFrom(changePercent),
  };
}

export function adaptSearchResult(dto: CompanySearchResultDTO): StockSearchResult {
  return {
    symbol: dto.ticker,
    name: dto.name ?? '',
    exchange: dto.exchange ?? '',
    type: 'Stock',
  };
}

export function adaptCompanyNews(dto: MarketNewsDTO): NewsItem {
  return {
    id: dto.id,
    title: dto.title,
    summary: dto.summary ?? '',
    source: dto.source,
    url: dto.url,
    publishedAt: dto.published_at,
    // The market-data news feed carries no sentiment/importance scoring;
    // default to neutral so the badge renders consistently.
    sentiment: 'neutral',
    importance: 'medium',
  };
}
