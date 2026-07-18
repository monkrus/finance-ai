import { Metadata } from 'next';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { SentimentTrend } from '@/features/news/charts/SentimentTrend';
import { EventTimeline } from '@/features/news/timeline/EventTimeline';
import { NewsFeed } from '@/features/news/components/NewsFeed';
import { PortfolioImpact } from '@/features/news/components/PortfolioImpact';

export async function generateMetadata({ params }: { params: Promise<{ ticker: string }> }): Promise<Metadata> {
  const p = await params;
  return {
    title: `${p.ticker.toUpperCase()} News Intelligence | FinPilot AI`,
  };
}

export default async function CompanyNewsPage({ params }: { params: Promise<{ ticker: string }> }) {
  const p = await params;
  const ticker = p.ticker.toUpperCase();

  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="flex items-center gap-4 mb-2">
        <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
          <Link href="/news">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">{ticker} Intelligence</h1>
          <p className="text-muted-foreground">News, Sentiment, and Events for {ticker}</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <SentimentTrend ticker={ticker} />
        <EventTimeline ticker={ticker} />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8 mt-4">
        <div className="xl:col-span-2 space-y-6">
          <h2 className="text-xl font-bold tracking-tight">Latest Stories</h2>
          <NewsFeed /> {/* In a real app we'd pass ticker={ticker} to filter */}
        </div>
        
        <div className="space-y-6">
          <PortfolioImpact />
        </div>
      </div>
    </div>
  );
}
