export interface PortfolioSummary {
  totalValue: number;
  dailyChange: number;
  dailyChangePercent: number;
  totalReturn: number;
  totalReturnPercent: number;
  unrealizedGain: number;
  realizedGain: number;
  beta: number;
  diversificationScore: number;
  holdingsCount: number;
}

export interface Holding {
  id: string;
  ticker: string;
  companyName: string;
  quantity: number;
  averageCost: number;
  currentPrice: number;
  marketValue: number;
  weight: number;
  dailyChangePercent: number;
  totalReturnPercent: number;
  unrealizedPL: number;
  sector: string;
  industry: string;
  country: string;
  currency: string;
}

export interface PortfolioPerformanceData {
  date: string;
  portfolioValue: number;
  benchmarkValue: number;
}

export interface AllocationData {
  name: string;
  value: number;
  color?: string;
}

export interface Transaction {
  id: string;
  date: string;
  ticker: string;
  type: 'buy' | 'sell' | 'dividend' | 'split';
  quantity: number;
  price: number;
  total: number;
  status: 'completed' | 'pending' | 'failed';
}

export interface BenchmarkMetrics {
  alpha: number;
  trackingError: number;
  beta: number;
  relativeReturn: number;
}
