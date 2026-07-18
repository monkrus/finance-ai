"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { usePortfolioImpact } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { AlertTriangle, TrendingUp, ShieldAlert, Zap } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import Link from 'next/link';

export function PortfolioImpact() {
  const { data, isLoading, isError, refetch } = usePortfolioImpact();

  if (isError) {
    return <WidgetError title="Impact Error" message="Failed to load portfolio impact." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
        <CardHeader className="pb-2">
          <CardTitle className="text-lg font-semibold">Portfolio Alerts</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex gap-3">
              <Skeleton className="h-8 w-8 rounded-full shrink-0" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-3 w-1/2" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (data.length === 0) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg text-center p-6">
        <ShieldAlert className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
        <p className="text-muted-foreground text-sm">No critical news affecting your portfolio today.</p>
      </Card>
    );
  }

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
      <CardHeader className="pb-4 border-b border-white/5">
        <CardTitle className="text-lg font-semibold flex items-center">
          <AlertTriangle className="h-5 w-5 mr-2 text-amber-500" />
          Portfolio Impact
        </CardTitle>
      </CardHeader>
      <CardContent className="p-0">
        <div className="divide-y divide-border/50">
          {data.map(alert => (
            <Link key={alert.id} href={`/news/article/${alert.articleId}`} className="block p-4 hover:bg-accent/30 transition-colors group">
              <div className="flex gap-3">
                <div className="shrink-0 mt-1">
                  {alert.type === 'risk' ? (
                    <TrendingDown className={`h-5 w-5 ${alert.severity === 'high' ? 'text-destructive' : 'text-amber-500'}`} />
                  ) : (
                    <TrendingUp className="h-5 w-5 text-emerald-500" />
                  )}
                </div>
                <div className="flex-1">
                  <div className="flex justify-between items-start mb-1">
                    <div className="flex gap-1 flex-wrap">
                      {alert.affectedHoldings.map(ticker => (
                        <span key={ticker} className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400">
                          {ticker}
                        </span>
                      ))}
                    </div>
                    <span className="text-[10px] text-muted-foreground whitespace-nowrap ml-2">
                      {formatDistanceToNow(new Date(alert.publishedAt))}
                    </span>
                  </div>
                  <h4 className="text-sm font-semibold group-hover:text-indigo-400 transition-colors leading-snug mb-1">
                    {alert.headline}
                  </h4>
                  <p className="text-xs text-muted-foreground line-clamp-2">
                    {alert.summary}
                  </p>
                </div>
              </div>
            </Link>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// Dummy component just to satisfy import in the above if missing
const TrendingDown = ({ className }: { className?: string }) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><polyline points="22 17 13.5 8.5 8.5 13.5 2 7"></polyline><polyline points="16 17 22 17 22 11"></polyline></svg>
);
