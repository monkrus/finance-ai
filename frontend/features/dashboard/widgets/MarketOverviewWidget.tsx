'use client';

import React from 'react';
import { useMarketOverview } from '../api/queries';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetSkeleton } from '../components/WidgetSkeleton';
import { WidgetError } from '../components/WidgetError';
import { WidgetGridItem } from '../components/WidgetGrid';
import { cn } from '@/lib/utils';
import { LineChart, Line, ResponsiveContainer, YAxis } from 'recharts';

// Mock sparkline data
const generateSparkline = (trend: 'up' | 'down') => {
  const data = [];
  let val = 100;
  for (let i = 0; i < 20; i++) {
    val += (Math.random() - (trend === 'up' ? 0.3 : 0.7)) * 10;
    data.push({ value: val });
  }
  return data;
};

export function MarketOverviewWidget() {
  const { data: markets, isLoading, isError, refetch } = useMarketOverview();

  if (isLoading) return <WidgetGridItem colSpan={2}><WidgetSkeleton /></WidgetGridItem>;
  if (isError || !markets) return <WidgetGridItem colSpan={2}><WidgetError onRetry={refetch} /></WidgetGridItem>;

  return (
    <WidgetGridItem colSpan={2}>
      <WidgetCard title="Market Overview" description="Major indices performance">
        <div className="flex flex-col space-y-4 pt-2">
          {markets.map((market) => {
            const isUp = market.change >= 0;
            const sparklineData = generateSparkline(isUp ? 'up' : 'down');
            
            return (
              <div key={market.symbol} className="flex items-center justify-between p-3 rounded-lg bg-background/40 hover:bg-background/60 transition-colors">
                <div className="flex flex-col">
                  <span className="font-semibold">{market.symbol}</span>
                  <span className="text-xs text-muted-foreground">{market.name}</span>
                </div>
                
                <div className="h-10 w-24 opacity-60">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={sparklineData}>
                      <YAxis domain={['dataMin', 'dataMax']} hide />
                      <Line 
                        type="monotone" 
                        dataKey="value" 
                        stroke={isUp ? "#10b981" : "#ef4444"} 
                        strokeWidth={2} 
                        dot={false} 
                        isAnimationActive={false} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                <div className="flex flex-col items-end">
                  <span className="font-medium">{market.price.toFixed(2)}</span>
                  <span className={cn("text-xs font-medium", isUp ? "text-emerald-500" : "text-destructive")}>
                    {isUp ? '+' : ''}{market.change.toFixed(2)} ({isUp ? '+' : ''}{market.changePercent.toFixed(2)}%)
                  </span>
                </div>
              </div>
            );
          })}
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
