// News Architecture Types

export interface NewsArticle {
  id: string;
  headline: string;
  summary: string;
  source: string;
  url: string;
  publishedAt: string;
  author?: string;
  imageUrl?: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  importance: number; // 1-10
  tickers: string[];
  categories: string[];
  isBreaking: boolean;
  readingTimeMin: number;
}

export interface NewsFeedResponse {
  articles: NewsArticle[];
  nextCursor?: string;
  totalResults: number;
}

export interface AISummary {
  executiveSummary: string;
  bullishSignals: string[];
  bearishSignals: string[];
  opportunities: string[];
  risks: string[];
  keyTakeaways: string[];
  portfolioImpact: string;
  importance: number;
  confidence: number;
}

export interface ArticleDetail extends NewsArticle {
  content: string; // HTML or Markdown
  aiSummary: AISummary;
  entities: Entity[];
  relatedStories: NewsArticle[];
}

export interface EventTimelineItem {
  id: string;
  date: string;
  type: 'Earnings' | 'Dividend' | 'M&A' | 'Launch' | 'Guidance' | 'SEC' | 'Regulatory' | 'Macro' | 'Other';
  title: string;
  description: string;
  sentiment: 'positive' | 'negative' | 'neutral';
}

export interface Entity {
  id: string;
  name: string;
  type: 'Company' | 'Person' | 'Country' | 'Product' | 'Regulator' | 'Industry';
  relevance: number;
}

export interface EntityRelationship {
  sourceId: string;
  targetId: string;
  type: string;
  strength: number;
}

export interface EntityGraph {
  nodes: Entity[];
  links: EntityRelationship[];
}

export interface SentimentTrendData {
  date: string;
  positive: number;
  neutral: number;
  negative: number;
  score: number; // -1 to 1
}

export interface PortfolioImpactAlert {
  id: string;
  articleId: string;
  headline: string;
  severity: 'high' | 'medium' | 'low';
  type: 'risk' | 'opportunity';
  affectedHoldings: string[]; // tickers
  summary: string;
  publishedAt: string;
}
