"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAIInsights } from '@/features/dashboard/api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Sparkles } from 'lucide-react';
import { cn } from '@/lib/utils';

export function PortfolioAIInsights() {
  const { data, isLoading, isError, refetch } = useAIInsights();

  if (isError) {
    return <WidgetError title="AI Error" message="Failed to load AI insights." onRetry={refetch} />;
  }

  return (
    <Card className="col-span-full lg:col-span-2 bg-gradient-to-br from-indigo-900/40 via-background to-background backdrop-blur-lg border-indigo-500/20 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2 flex flex-row items-center space-y-0">
        <Sparkles className="h-5 w-5 text-indigo-400 mr-2" />
        <CardTitle className="text-lg font-semibold text-indigo-100">AI Portfolio Health & Strategy</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 overflow-auto">
        {isLoading || !data ? (
          <div className="space-y-4 pt-2">
            {Array.from({length: 3}).map((_, i) => (
              <div key={i} className="space-y-2">
                <Skeleton className="h-5 w-1/3" />
                <Skeleton className="h-16 w-full" />
              </div>
            ))}
          </div>
        ) : (
          <div className="space-y-6 pt-2">
            {data.map((insight) => (
              <div key={insight.id} className="relative pl-6 before:absolute before:left-0 before:top-2 before:h-2 before:w-2 before:rounded-full before:bg-indigo-500">
                <h4 className="font-medium text-sm text-indigo-200 mb-1">{insight.title}</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  {insight.description}
                </p>
                <div className="flex items-center gap-4 mt-2 text-xs">
                  <span className={cn(
                    "px-2 py-0.5 rounded-full font-medium bg-background border",
                    insight.category === 'market' ? "border-orange-500/30 text-orange-400" :
                    insight.category === 'portfolio' ? "border-emerald-500/30 text-emerald-400" :
                    "border-indigo-500/30 text-indigo-400"
                  )}>
                    {insight.category.toUpperCase()}
                  </span>
                  <span className="text-muted-foreground opacity-70">
                    Confidence: {(insight.confidence * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
