// Dashboard Architecture Types

export interface WidgetProps {
  id: string;
  title: string;
  className?: string;
}

export interface KPI {
  id: string;
  label: string;
  value: number;
  delta: number; // percentage change
  trend: 'up' | 'down' | 'neutral';
  format?: 'currency' | 'percentage' | 'number';
}

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  url: string;
  publishedAt: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  importance: 'high' | 'medium' | 'low';
}

export interface MarketIndex {
  symbol: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
}

export interface AIInsight {
  id: string;
  title: string;
  description: string;
  category: 'portfolio' | 'market' | 'wealth';
  timestamp: string;
  confidence: number;
}

export interface DashboardState {
  netWorth: number;
  netWorthChange: number;
  portfolioValue: number;
  portfolioChange: number;
  cashBalance: number;
  wealthScore: number;
}
