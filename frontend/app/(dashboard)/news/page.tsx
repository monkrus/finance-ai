import { Metadata } from 'next';
import { NewsFeed } from '@/features/news/components/NewsFeed';
import { PortfolioImpact } from '@/features/news/components/PortfolioImpact';

export const metadata: Metadata = {
  title: 'News Intelligence | FinPilot AI',
  description: 'AI-curated market news and portfolio impact analysis.',
};

export default function NewsPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="mb-4">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight mb-2">News Intelligence</h1>
        <p className="text-muted-foreground text-lg">Curated market news, AI sentiment analysis, and portfolio impact.</p>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        <div className="xl:col-span-2 space-y-6">
          <NewsFeed />
        </div>
        
        <div className="space-y-6">
          <PortfolioImpact />
          {/* We can add other sidebar elements here like Trending Tickers, Market Summary etc. */}
        </div>
      </div>
    </div>
  );
}
