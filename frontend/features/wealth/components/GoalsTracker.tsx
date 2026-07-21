"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useFinancialGoals } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Target, Plus, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';

export function GoalsTracker() {
  const { data, isLoading, isError, refetch } = useFinancialGoals();

  if (isError) {
    return <WidgetError title="Goals Error" message="Failed to load goals." onRetry={refetch} />;
  }

  const formatCurrency = (v: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg min-h-[500px]">
      <CardHeader className="pb-4 border-b border-white/5 flex flex-row items-center justify-between">
        <CardTitle className="text-lg font-semibold flex items-center">
          <Target className="h-5 w-5 mr-2 text-indigo-400" />
          Active Goals
        </CardTitle>
        <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700 h-8">
          <Plus className="h-4 w-4 mr-1" /> New Goal
        </Button>
      </CardHeader>
      
      <CardContent className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AnimatePresence>
            {isLoading || !data ? (
              Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="bg-card/40 border border-white/5 p-5 rounded-2xl space-y-4">
                  <div className="flex justify-between"><Skeleton className="h-5 w-32" /><Skeleton className="h-5 w-10" /></div>
                  <Skeleton className="h-8 w-40" />
                  <Skeleton className="h-2 w-full rounded-full" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              ))
            ) : data.length === 0 ? (
              <div className="col-span-1 md:col-span-2 py-12 text-center text-muted-foreground">
                <Target className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>No active financial goals.</p>
                <Button variant="link" className="text-indigo-400 mt-2">Create your first goal</Button>
              </div>
            ) : (
              data.map((goal, i) => {
                const pct = Math.min(100, Math.max(0, (goal.currentAmount / goal.targetAmount) * 100)) || 0;
                
                return (
                  <motion.div 
                    key={goal.id}
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.1 }}
                    className="bg-card/40 border border-white/5 p-5 rounded-2xl hover:bg-white/5 transition-colors relative overflow-hidden group"
                  >
                    {/* Goal category specific glow */}
                    <div className={cn(
                      "absolute top-0 right-0 w-32 h-32 rounded-full blur-3xl pointer-events-none opacity-20 -translate-y-1/2 translate-x-1/2 transition-opacity group-hover:opacity-40",
                      goal.category === 'Retirement' ? 'bg-indigo-500' :
                      goal.category === 'Emergency' ? 'bg-emerald-500' :
                      goal.category === 'House' ? 'bg-amber-500' : 'bg-blue-500'
                    )} />

                    <div className="flex justify-between items-start mb-4 relative z-10">
                      <div>
                        <h4 className="font-semibold text-lg">{goal.name}</h4>
                        <span className="text-[10px] uppercase tracking-wider text-muted-foreground">{goal.category}</span>
                      </div>
                      <span className={cn(
                        "text-xs font-bold px-2 py-1 rounded-full bg-muted/50",
                        pct >= 100 ? "text-emerald-500" : pct >= 50 ? "text-indigo-400" : "text-foreground"
                      )}>
                        {pct.toFixed(0)}%
                      </span>
                    </div>

                    <div className="mb-4 relative z-10">
                      <div className="flex items-end gap-2 mb-1">
                        <span className="text-2xl font-bold tracking-tight text-foreground">{formatCurrency(goal.currentAmount)}</span>
                        <span className="text-sm text-muted-foreground pb-1">/ {formatCurrency(goal.targetAmount)}</span>
                      </div>
                    </div>

                    <div className="h-2 bg-muted/50 rounded-full overflow-hidden mb-4 relative z-10">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${pct}%` }}
                        transition={{ duration: 1, ease: "easeOut", delay: i * 0.1 + 0.2 }}
                        className={cn(
                          "h-full rounded-full",
                          pct >= 100 ? "bg-emerald-500" : "bg-indigo-500"
                        )}
                      />
                    </div>

                    <div className="flex justify-between items-center text-xs text-muted-foreground relative z-10 border-t border-border/50 pt-3 mt-4">
                      <div className="flex items-center">
                        <Calendar className="h-3 w-3 mr-1" />
                        Target: {new Date(goal.targetDate).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
                      </div>
                      <div>
                        +{formatCurrency(goal.monthlyContribution)}/mo
                      </div>
                    </div>
                  </motion.div>
                );
              })
            )}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}
