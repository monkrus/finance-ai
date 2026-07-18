'use client';

import React from 'react';
import { useKPIs } from '../api/queries';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetSkeleton } from '../components/WidgetSkeleton';
import { WidgetError } from '../components/WidgetError';
import { WidgetGridItem } from '../components/WidgetGrid';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'motion/react';

export function KPIWidget() {
  const { data: kpis, isLoading, isError, refetch } = useKPIs();

  if (isLoading) return (
    <>
      <WidgetGridItem><WidgetSkeleton /></WidgetGridItem>
      <WidgetGridItem><WidgetSkeleton /></WidgetGridItem>
      <WidgetGridItem><WidgetSkeleton /></WidgetGridItem>
      <WidgetGridItem><WidgetSkeleton /></WidgetGridItem>
    </>
  );

  if (isError || !kpis) return (
    <WidgetGridItem colSpan={4}>
      <WidgetError onRetry={refetch} />
    </WidgetGridItem>
  );

  return (
    <>
      {kpis.map((kpi, index) => {
        const isUp = kpi.trend === 'up';
        const isDown = kpi.trend === 'down';
        
        let formattedValue = kpi.value.toString();
        if (kpi.format === 'currency') {
          formattedValue = new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(kpi.value);
        }

        return (
          <WidgetGridItem key={kpi.id} index={index}>
            <WidgetCard premium>
              <div className="flex flex-col h-full justify-between p-2">
                <div className="text-sm font-medium text-muted-foreground">{kpi.label}</div>
                <div className="mt-4 flex items-end justify-between">
                  <div className="text-3xl font-bold tracking-tight">{formattedValue}</div>
                  
                  <div className={cn(
                    "flex items-center text-sm font-medium",
                    isUp ? "text-emerald-500" : isDown ? "text-destructive" : "text-muted-foreground"
                  )}>
                    {isUp && <TrendingUp className="mr-1 h-4 w-4" />}
                    {isDown && <TrendingDown className="mr-1 h-4 w-4" />}
                    {!isUp && !isDown && <Minus className="mr-1 h-4 w-4" />}
                    
                    {kpi.format === 'currency' 
                      ? new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', signDisplay: 'always' }).format(kpi.delta)
                      : `${kpi.delta > 0 ? '+' : ''}${kpi.delta}%`
                    }
                  </div>
                </div>
              </div>
            </WidgetCard>
          </WidgetGridItem>
        );
      })}
    </>
  );
}
