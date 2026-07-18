"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAICoach } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Sparkles, Target, PiggyBank, TrendingUp, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

export function AICoachCard() {
  const { data, isLoading, isError, refetch } = useAICoach();

  if (isError) {
    return <WidgetError title="AI Coach Error" message="Failed to load recommendations." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-lg relative overflow-hidden h-[500px]">
        <CardHeader>
          <CardTitle className="text-lg font-semibold flex items-center">
            <Sparkles className="h-5 w-5 mr-2 text-indigo-400" />
            FinPilot AI Coach
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="flex gap-4">
              <Skeleton className="h-10 w-10 rounded-full shrink-0" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-5 w-3/4" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-5/6" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  const getIcon = (type: string) => {
    switch(type) {
      case 'budget': return <AlertCircle className="h-5 w-5 text-amber-500" />;
      case 'saving': return <PiggyBank className="h-5 w-5 text-emerald-500" />;
      case 'retirement': return <TrendingUp className="h-5 w-5 text-indigo-500" />;
      case 'goal': return <Target className="h-5 w-5 text-fuchsia-500" />;
      default: return <Sparkles className="h-5 w-5 text-blue-500" />;
    }
  };

  return (
    <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-lg relative overflow-hidden h-[500px] flex flex-col">
      <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-[80px] pointer-events-none -translate-y-1/2 translate-x-1/3" />
      
      <CardHeader className="pb-4 border-b border-white/5 relative z-10">
        <CardTitle className="text-lg font-semibold flex items-center">
          <Sparkles className="h-5 w-5 mr-2 text-indigo-400" />
          FinPilot AI Coach
        </CardTitle>
      </CardHeader>
      
      <CardContent className="p-0 flex-1 overflow-y-auto custom-scrollbar relative z-10">
        <div className="divide-y divide-border/50">
          {data.map((rec, i) => (
            <motion.div 
              key={rec.id}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.1 }}
              className="p-5 hover:bg-white/5 transition-colors group"
            >
              <div className="flex gap-4">
                <div className="shrink-0 mt-1 bg-background p-2 rounded-xl shadow-sm border border-white/5 group-hover:scale-110 transition-transform">
                  {getIcon(rec.type)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="text-sm font-semibold">{rec.title}</h4>
                    {rec.impact === 'high' && (
                      <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-500">
                        High Impact
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-muted-foreground leading-relaxed">
                    {rec.description}
                  </p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
