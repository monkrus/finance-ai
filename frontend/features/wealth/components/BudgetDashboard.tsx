"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useBudgetSummary, useBudgetCategories } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { AlertCircle, Target, Wallet } from 'lucide-react';

export function BudgetDashboard() {
  const { data: summary, isLoading: isLoadingSummary, isError: isErrorSummary, refetch: refetchSummary } = useBudgetSummary();
  const { data: categories, isLoading: isLoadingCats, isError: isErrorCats, refetch: refetchCats } = useBudgetCategories();

  if (isErrorSummary || isErrorCats) {
    return <WidgetError title="Budget Error" message="Failed to load budget data." onRetry={() => { refetchSummary(); refetchCats(); }} />;
  }

  const formatCurrency = (v: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

  return (
    <div className="space-y-8">
      {/* High level metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard 
          title="Total Budget" 
          amount={summary?.totalBudget} 
          icon={<Target />} 
          loading={isLoadingSummary} 
        />
        <MetricCard 
          title="Total Spent" 
          amount={summary?.totalSpent} 
          icon={<Wallet />} 
          loading={isLoadingSummary} 
          subtitle={`${summary?.utilizationPercent.toFixed(1)}% Utilized`}
        />
        <MetricCard 
          title="Remaining" 
          amount={summary?.remaining} 
          icon={<AlertCircle />} 
          loading={isLoadingSummary} 
          highlight={summary?.remaining && summary.remaining < 0 ? 'destructive' : 'emerald'}
        />
      </div>

      {/* Utilization progress */}
      <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
        <CardHeader>
          <CardTitle className="text-lg font-semibold">Category Breakdown</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6 p-6 pt-0">
          {isLoadingCats || !categories ? (
            Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="flex justify-between"><Skeleton className="h-4 w-24" /><Skeleton className="h-4 w-16" /></div>
                <Skeleton className="h-2 w-full rounded-full" />
              </div>
            ))
          ) : (
            categories.map((cat, i) => {
              const pct = Math.min(100, Math.max(0, (cat.spent / cat.allocated) * 100)) || 0;
              return (
                <motion.div 
                  key={cat.name}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="space-y-2"
                >
                  <div className="flex justify-between items-center text-sm font-medium">
                    <span className="text-foreground">{cat.name}</span>
                    <span className="text-muted-foreground">{formatCurrency(cat.spent)} / {formatCurrency(cat.allocated)}</span>
                  </div>
                  <div className="h-2 bg-muted/50 rounded-full overflow-hidden flex">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${pct}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className={cn(
                        "h-full rounded-full",
                        cat.status === 'over' ? "bg-destructive" :
                        cat.status === 'under' ? "bg-emerald-500" : "bg-indigo-500"
                      )}
                    />
                  </div>
                  <div className="flex justify-between text-xs text-muted-foreground">
                    <span>{pct.toFixed(1)}% used</span>
                    <span className={cn(cat.status === 'over' && "text-destructive font-bold")}>
                      {cat.remaining < 0 ? `${formatCurrency(Math.abs(cat.remaining))} Over` : `${formatCurrency(cat.remaining)} Left`}
                    </span>
                  </div>
                </motion.div>
              );
            })
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function MetricCard({ title, amount, icon, loading, subtitle, highlight }: any) {
  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="p-2 bg-muted/50 rounded-lg text-muted-foreground border border-white/5">
            {React.cloneElement(icon, { className: 'w-5 h-5' })}
          </div>
        </div>
        <div className="text-sm font-medium text-muted-foreground mb-1">{title}</div>
        {loading || amount === undefined ? (
          <Skeleton className="h-8 w-32 mt-2" />
        ) : (
          <div className="flex items-end justify-between">
            <div className={cn(
              "text-3xl font-bold tracking-tight",
              highlight === 'destructive' ? 'text-destructive' : highlight === 'emerald' ? 'text-emerald-500' : 'text-foreground'
            )}>
              {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount)}
            </div>
            {subtitle && <div className="text-sm text-muted-foreground mb-1">{subtitle}</div>}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
