"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useDashboardNews } from '@/features/dashboard/api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { Badge } from '@/components/ui/badge';

export function PortfolioNews() {
  const { data, isLoading, isError, refetch } = useDashboardNews();

  if (isError) {
    return <WidgetError title="Portfolio News Error" message="Failed to load related news." onRetry={refetch} />;
  }

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Portfolio News</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 overflow-auto">
        {isLoading || !data ? (
          <div className="space-y-4">
            {Array.from({length: 4}).map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-12 w-12 rounded-lg" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-4">
            {data.map((item) => (
              <div key={item.id} className="flex flex-col space-y-1 p-3 rounded-lg hover:bg-accent/50 transition-colors border border-border/50">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-sm line-clamp-1">{item.title}</h4>
                  {item.importance === 'high' && <Badge variant="destructive" className="ml-2 text-[10px]">IMPORTANT</Badge>}
                </div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground mt-1">
                  <span className={cn(
                    "px-1.5 py-0.5 rounded-sm font-semibold tracking-wider text-[9px] uppercase",
                    item.sentiment === 'positive' ? "bg-emerald-500/10 text-emerald-500" :
                    item.sentiment === 'negative' ? "bg-destructive/10 text-destructive" :
                    "bg-muted text-muted-foreground"
                  )}>
                    {item.sentiment}
                  </span>
                  <span>•</span>
                  <span>{new Date(item.publishedAt).toLocaleDateString()}</span>
                  <span>•</span>
                  <span>{item.source}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
