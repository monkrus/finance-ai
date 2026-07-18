"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useSentimentTrend } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { cn } from '@/lib/utils';

export function SentimentTrend({ ticker }: { ticker?: string }) {
  const [timeframe, setTimeframe] = useState<'daily'|'weekly'|'monthly'>('daily');
  const { data, isLoading, isError, refetch } = useSentimentTrend(ticker, timeframe);

  if (isError) {
    return <WidgetError title="Sentiment Error" message="Failed to load sentiment trend." onRetry={refetch} />;
  }

  const chartData = data?.map(d => ({
    date: new Date(d.date).toLocaleDateString(undefined, { month: 'short', day: 'numeric' }),
    score: d.score,
    positive: d.positive,
    negative: d.negative
  })) || [];

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2 flex flex-row items-center justify-between border-b border-white/5">
        <CardTitle className="text-lg font-semibold">Sentiment Trend</CardTitle>
        <div className="flex bg-muted/30 p-1 rounded-md">
          {['daily', 'weekly', 'monthly'].map(tf => (
            <button
              key={tf}
              onClick={() => setTimeframe(tf as any)}
              className={cn(
                "px-2 py-1 text-xs font-medium rounded-sm transition-colors capitalize",
                timeframe === tf ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
              )}
            >
              {tf}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="flex-1 w-full min-h-0 relative p-4 pt-0">
        {isLoading || !data ? (
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <Skeleton className="h-full w-full rounded-md" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 20, right: 0, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                  <stop offset="50%" stopColor="#3b82f6" stopOpacity={0.1}/>
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0.3}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
              <YAxis 
                stroke="#888888" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false} 
                domain={[-1, 1]}
                tickFormatter={(v) => (v === 0 ? 'Neutral' : v > 0 ? 'Bull' : 'Bear')} 
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '0.5rem' }}
                itemStyle={{ color: 'var(--foreground)' }}
                labelStyle={{ color: 'var(--muted-foreground)', marginBottom: '4px' }}
                formatter={(value: any) => [Number(value).toFixed(2), 'Sentiment Score']}
              />
              <Area type="monotone" dataKey="score" stroke="#4f46e5" fillOpacity={1} fill="url(#colorScore)" />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
