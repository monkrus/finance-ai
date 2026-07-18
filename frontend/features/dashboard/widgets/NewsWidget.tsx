'use client';

import React from 'react';
import { useDashboardNews } from '../api/queries';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetSkeleton } from '../components/WidgetSkeleton';
import { WidgetError } from '../components/WidgetError';
import { WidgetGridItem } from '../components/WidgetGrid';
import { Newspaper } from 'lucide-react';

export function NewsWidget() {
  const { data: news, isLoading, isError, refetch } = useDashboardNews();

  if (isLoading) return <WidgetGridItem colSpan={2}><WidgetSkeleton /></WidgetGridItem>;
  if (isError || !news) return <WidgetGridItem colSpan={2}><WidgetError onRetry={refetch} /></WidgetGridItem>;

  return (
    <WidgetGridItem colSpan={2}>
      <WidgetCard 
        title="Market News" 
        description="Latest headlines impacting your portfolio"
        headerAction={<Newspaper className="h-5 w-5 text-muted-foreground" />}
      >
        <div className="flex flex-col space-y-4 pt-2">
          {news.map((item) => (
            <div key={item.id} className="flex flex-col space-y-1 pb-4 border-b border-border last:border-0 last:pb-0">
              <div className="flex justify-between items-start">
                <a href={item.url} className="text-sm font-medium hover:underline hover:text-primary transition-colors line-clamp-2 pr-4">
                  {item.title}
                </a>
                <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium whitespace-nowrap ${
                  item.sentiment === 'positive' ? 'bg-emerald-500/10 text-emerald-500' :
                  item.sentiment === 'negative' ? 'bg-destructive/10 text-destructive' :
                  'bg-muted text-muted-foreground'
                }`}>
                  {item.sentiment.toUpperCase()}
                </span>
              </div>
              <p className="text-xs text-muted-foreground line-clamp-2">{item.summary}</p>
              <div className="flex items-center text-[10px] text-muted-foreground space-x-2 pt-1">
                <span className="font-medium text-foreground/70">{item.source}</span>
                <span>•</span>
                <span>{new Date(item.publishedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                {item.importance === 'high' && (
                  <>
                    <span>•</span>
                    <span className="text-destructive font-semibold">IMPORTANT</span>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
