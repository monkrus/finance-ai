// Market Architecture Types

export interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  sparkline: number[];
  trend: 'up' | 'down' | 'neutral';
}

export interface MarketBreadth {
  advancing: number;
  declining: number;
  unchanged: number;
  newHighs: number;
  newLows: number;
}

export interface SectorPerformance {
  sector: string;
  performance: number;
}

export interface StockSearchResult {
  symbol: string;
  name: string;
  exchange: string;
  type: string;
}

export interface CompanyProfile {
  ticker: string;
  companyName: string;
  description: string;
  logo: string;
  exchange: string;
  industry: string;
  sector: string;
  ceo: string;
  employees: number;
  headquarters: string;
  website: string;
  marketCap: number;
  enterpriseValue: number;
}

export interface PriceData {
  time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface TechnicalIndicators {
  rsi: number;
  macd: { value: number; signal: number; hist: number };
  sma20: number;
  sma50: number;
  sma200: number;
  ema20: number;
  vwap: number;
  atr: number;
  adx: number;
  bollingerBands: { upper: number; middle: number; lower: number };
}

export interface FinancialStatement {
  year: number;
  quarter?: number;
  revenue: number;
  costOfRevenue: number;
  grossProfit: number;
  operatingExpenses: number;
  operatingIncome: number;
  netIncome: number;
  eps: number;
}

export interface FinancialRatios {
  pe: number;
  pb: number;
  peg: number;
  evToEbitda: number;
  roe: number;
  roa: number;
  roic: number;
  currentRatio: number;
  quickRatio: number;
  debtToEquity: number;
  grossMargin: number;
  ebitdaMargin: number;
  netMargin: number;
  revenueGrowth: number;
  epsGrowth: number;
}

export interface ValuationData {
  intrinsicValueDCF: number;
  intrinsicValueDDM: number;
  fairValueLower: number;
  fairValueUpper: number;
  currentPrice: number;
}

export interface EarningsData {
  date: string;
  epsEstimate: number;
  epsActual: number;
  revenueEstimate: number;
  revenueActual: number;
  surprisePercent: number;
}

export interface AnalystRatings {
  buy: number;
  hold: number;
  sell: number;
  consensus: 'Buy' | 'Hold' | 'Sell' | 'Strong Buy' | 'Strong Sell';
  targetHigh: number;
  targetLow: number;
  targetMean: number;
}

export interface PeerComparison {
  symbol: string;
  companyName: string;
  price: number;
  marketCap: number;
  revenue: number;
  pe: number;
  roe: number;
  grossMargin: number;
}

export interface AIResearchThesis {
  executiveSummary: string;
  bullCase: string[];
  bearCase: string[];
  keyRisks: string[];
  competitiveAdvantages: string[];
  catalysts: string[];
  investmentThesis: string;
}
