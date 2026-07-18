"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useCompanyNews } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { ExternalLink, Clock } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';

export function CompanyNews({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useCompanyNews(ticker);

  if (isError) {
    return <WidgetError title="News Error" message="Failed to load news." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
        <CardContent className="p-6 space-y-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="space-y-2">
              <Skeleton className="h-4 w-3/4" />
              <Skeleton className="h-3 w-1/4" />
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[600px] flex flex-col">
      <CardHeader className="pb-4 border-b border-white/5">
        <CardTitle className="text-lg font-semibold flex items-center">
          Latest News
          <span className="ml-2 px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 text-xs">{data.length}</span>
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0 overflow-y-auto flex-1 custom-scrollbar">
        <div className="divide-y divide-border/50">
          {data.map((news) => (
            <a 
              key={news.id} 
              href={news.url} 
              target="_blank" 
              rel="noreferrer"
              className="block p-4 hover:bg-accent/30 transition-colors group"
            >
              <div className="flex justify-between items-start mb-2">
                <span className={`text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded ${
                  news.sentiment === 'positive' ? 'bg-emerald-500/10 text-emerald-500' :
                  news.sentiment === 'negative' ? 'bg-destructive/10 text-destructive' :
                  'bg-muted text-muted-foreground'
                }`}>
                  {news.sentiment}
                </span>
                <span className="text-xs text-muted-foreground flex items-center">
                  <Clock className="h-3 w-3 mr-1" />
                  {formatDistanceToNow(new Date(news.publishedAt), { addSuffix: true })}
                </span>
              </div>
              <h4 className="text-sm font-semibold mb-1 group-hover:text-indigo-400 transition-colors line-clamp-2">
                {news.title}
              </h4>
              <p className="text-xs text-muted-foreground line-clamp-2 mb-2">
                {news.summary}
              </p>
              <div className="flex justify-between items-center text-xs">
                <span className="text-indigo-400 font-medium">{news.source}</span>
                <ExternalLink className="h-3 w-3 text-muted-foreground group-hover:text-indigo-400" />
              </div>
            </a>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
