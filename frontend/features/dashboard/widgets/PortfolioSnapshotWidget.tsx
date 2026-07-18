'use client';

import React from 'react';
import Link from 'next/link';
import { useDashboardOverview } from '../api/queries';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetSkeleton } from '../components/WidgetSkeleton';
import { WidgetError } from '../components/WidgetError';
import { WidgetGridItem } from '../components/WidgetGrid';
import { cn } from '@/lib/utils';
import { PieChart, ArrowRight } from 'lucide-react';

export function PortfolioSnapshotWidget() {
  const { data: overview, isLoading, isError, refetch } = useDashboardOverview();

  if (isLoading) return <WidgetGridItem colSpan={2} rowSpan={2}><WidgetSkeleton /></WidgetGridItem>;
  if (isError || !overview) return <WidgetGridItem colSpan={2} rowSpan={2}><WidgetError onRetry={refetch} /></WidgetGridItem>;

  const portfolioValue = overview.portfolioValue ?? 0;
  const dailyChange = overview.portfolioChange ?? 0;
  const hasInvestments = portfolioValue > 0;

  return (
    <WidgetGridItem colSpan={2} rowSpan={2}>
      <WidgetCard title="Portfolio Snapshot" description="Asset allocation and performance">
        <div className="flex flex-col h-full space-y-6 pt-4">
          <div className="flex items-end justify-between">
            <div>
              <div className="text-sm font-medium text-muted-foreground mb-1">Total Value</div>
              <div className="text-3xl font-bold tracking-tight">
                {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(portfolioValue)}
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-muted-foreground mb-1">Daily Change</div>
              <div className={cn('text-lg font-semibold', dailyChange < 0 ? 'text-destructive' : 'text-emerald-500')}>
                {dailyChange > 0 ? '+' : ''}{dailyChange}%
              </div>
            </div>
          </div>

          {/* Allocation and holdings are not carried by the dashboard overview
              endpoint, so this widget never fabricates them. A funded user is
              pointed to the Portfolio page (which shows real allocation and
              holdings); a new user sees an empty state. */}
          <div className="flex-1 flex flex-col items-center justify-center text-center py-8 text-muted-foreground">
            <PieChart className="h-9 w-9 mb-3 opacity-40" />
            {hasInvestments ? (
              <>
                <p className="text-sm font-medium text-foreground">
                  View your full allocation and holdings
                </p>
                <Link
                  href="/portfolio"
                  className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Open Portfolio <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </>
            ) : (
              <>
                <p className="text-sm font-medium text-foreground">You don&apos;t have any investments yet.</p>
                <p className="text-xs mt-1">Add holdings to see your allocation here.</p>
                <Link
                  href="/portfolio"
                  className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                >
                  Go to Portfolio <ArrowRight className="h-3.5 w-3.5" />
                </Link>
              </>
            )}
          </div>
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
