"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAIResearch } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Sparkles, TrendingUp, TrendingDown, ShieldAlert, Zap } from 'lucide-react';

export function AIResearchReport({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useAIResearch(ticker);

  if (isError) {
    return <WidgetError title="AI Research Error" message="Failed to generate AI thesis." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg border-t-2 border-t-indigo-500">
        <CardContent className="p-6 space-y-6">
          <Skeleton className="h-24 w-full" />
          <div className="grid grid-cols-2 gap-4">
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg border-t-2 border-t-indigo-500 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-3xl pointer-events-none -translate-y-1/2 translate-x-1/3" />
      
      <CardHeader className="pb-4 border-b border-white/5 relative z-10">
        <CardTitle className="text-lg font-semibold flex items-center">
          <Sparkles className="h-5 w-5 mr-2 text-indigo-400" />
          FinPilot AI Thesis
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-6 relative z-10 space-y-6">
        <div>
          <h3 className="text-sm font-semibold text-muted-foreground mb-2 uppercase tracking-wider">Executive Summary</h3>
          <p className="text-sm leading-relaxed">{data.executiveSummary}</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-emerald-500/5 border border-emerald-500/20 rounded-lg p-4">
            <h3 className="text-sm font-bold text-emerald-500 mb-3 flex items-center">
              <TrendingUp className="h-4 w-4 mr-2" /> Bull Case
            </h3>
            <ul className="space-y-2">
              {data.bullCase.map((point, i) => (
                <li key={i} className="text-sm flex items-start">
                  <span className="text-emerald-500 mr-2">•</span> {point}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-destructive/5 border border-destructive/20 rounded-lg p-4">
            <h3 className="text-sm font-bold text-destructive mb-3 flex items-center">
              <TrendingDown className="h-4 w-4 mr-2" /> Bear Case
            </h3>
            <ul className="space-y-2">
              {data.bearCase.map((point, i) => (
                <li key={i} className="text-sm flex items-start">
                  <span className="text-destructive mr-2">•</span> {point}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center">
              <Zap className="h-4 w-4 mr-2 text-amber-500" /> Catalysts
            </h3>
            <ul className="space-y-2">
              {data.catalysts.map((point, i) => (
                <li key={i} className="text-sm flex items-start">
                  <span className="text-amber-500 mr-2">→</span> {point}
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center">
              <ShieldAlert className="h-4 w-4 mr-2 text-rose-500" /> Key Risks
            </h3>
            <ul className="space-y-2">
              {data.keyRisks.map((point, i) => (
                <li key={i} className="text-sm flex items-start">
                  <span className="text-rose-500 mr-2">⚠</span> {point}
                </li>
              ))}
            </ul>
          </div>
        </div>

        <div className="pt-4 border-t border-border/50">
          <h3 className="text-sm font-semibold text-muted-foreground mb-2 uppercase tracking-wider">Investment Thesis</h3>
          <div className="p-4 bg-muted/30 rounded-lg border border-white/5 italic text-sm text-muted-foreground">
            "{data.investmentThesis}"
          </div>
        </div>

      </CardContent>
    </Card>
  );
}
