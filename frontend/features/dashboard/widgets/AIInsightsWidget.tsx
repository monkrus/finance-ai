'use client';

import React from 'react';
import { useAIInsights } from '../api/queries';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetSkeleton } from '../components/WidgetSkeleton';
import { WidgetError } from '../components/WidgetError';
import { WidgetGridItem } from '../components/WidgetGrid';
import { Sparkles, ArrowRight } from 'lucide-react';

export function AIInsightsWidget() {
  const { data: insights, isLoading, isError, refetch } = useAIInsights();

  if (isLoading) return <WidgetGridItem colSpan={2}><WidgetSkeleton /></WidgetGridItem>;
  if (isError || !insights || insights.length === 0) return <WidgetGridItem colSpan={2}><WidgetError onRetry={refetch} /></WidgetGridItem>;

  const primaryInsight = insights[0];

  return (
    <WidgetGridItem colSpan={2}>
      <WidgetCard 
        premium 
        className="bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-background border-indigo-500/20"
      >
        <div className="flex flex-col h-full justify-between p-2">
          <div className="flex items-center space-x-2 text-indigo-500 mb-4">
            <Sparkles className="h-5 w-5" />
            <h3 className="font-semibold tracking-tight">FinPilot AI Insight</h3>
          </div>
          
          <div className="space-y-2 mb-6">
            <h4 className="text-lg font-medium leading-tight">{primaryInsight.title}</h4>
            <p className="text-sm text-muted-foreground leading-relaxed">
              {primaryInsight.description}
            </p>
          </div>
          
          <div className="flex items-center justify-between mt-auto">
            <span className="text-xs font-medium px-2.5 py-1 rounded-full bg-indigo-500/10 text-indigo-500 uppercase tracking-wider">
              {primaryInsight.category}
            </span>
            
            <button className="text-xs font-medium text-indigo-500 hover:text-indigo-400 flex items-center transition-colors">
              Explore Analysis <ArrowRight className="ml-1 h-3 w-3" />
            </button>
          </div>
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
