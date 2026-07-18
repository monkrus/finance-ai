"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useNetWorthSummary, useNetWorthHistory } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { cn } from '@/lib/utils';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { motion } from 'framer-motion';

export function NetWorthChart() {
  const [range, setRange] = useState('1Y');
  
  const { data: summary, isLoading: isLoadingSummary } = useNetWorthSummary();
  const { data: history, isLoading: isLoadingHistory, isError, refetch } = useNetWorthHistory(range);

  if (isError) {
    return <WidgetError title="Net Worth Error" message="Failed to load history." onRetry={refetch} />;
  }

  const formatCurrency = (val: number) => 
    new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(val);

  return (
    <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-2xl overflow-hidden">
      <CardHeader className="pb-0 border-b border-white/5 relative z-10 bg-card/40">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 pb-6">
          <div>
            <CardTitle className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-2">
              Total Net Worth
            </CardTitle>
            {isLoadingSummary || !summary ? (
              <Skeleton className="h-10 w-48" />
            ) : (
              <div className="flex items-end gap-4">
                <motion.div 
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="text-4xl md:text-5xl font-bold tracking-tight text-white"
                >
                  {formatCurrency(summary.netWorth)}
                </motion.div>
                <div className={cn(
                  "flex items-center text-sm font-medium px-2 py-1 rounded-full mb-1",
                  summary.trend === 'up' ? "bg-emerald-500/10 text-emerald-500" :
                  summary.trend === 'down' ? "bg-destructive/10 text-destructive" :
                  "bg-muted text-muted-foreground"
                )}>
                  {summary.trend === 'up' ? <TrendingUp className="w-3 h-3 mr-1" /> :
                   summary.trend === 'down' ? <TrendingDown className="w-3 h-3 mr-1" /> :
                   <Minus className="w-3 h-3 mr-1" />}
                  {summary.changePercent > 0 ? '+' : ''}{summary.changePercent.toFixed(2)}%
                </div>
              </div>
            )}
          </div>

          <div className="flex bg-muted/30 p-1 rounded-lg">
            {['1M', '3M', 'YTD', '1Y', 'ALL'].map(r => (
              <button
                key={r}
                onClick={() => setRange(r)}
                className={cn(
                  "px-4 py-1.5 text-xs font-medium rounded-md transition-colors",
                  range === r ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/20" : "text-muted-foreground hover:text-foreground hover:bg-white/5"
                )}
              >
                {r}
              </button>
            ))}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="p-0 h-[400px] relative">
        {isLoadingHistory || !history ? (
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <Skeleton className="h-[300px] w-full rounded-xl" />
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={history} margin={{ top: 20, right: 0, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorNetWorth" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="date" 
                tickFormatter={(val) => new Date(val).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                stroke="#ffffff40" 
                fontSize={12} 
                tickLine={false} 
                axisLine={false}
                minTickGap={30}
                dy={10}
              />
              <YAxis 
                hide 
                domain={['dataMin - 10000', 'dataMax + 10000']} 
              />
              <Tooltip
                contentStyle={{ backgroundColor: 'rgba(9, 9, 11, 0.9)', borderColor: 'rgba(255,255,255,0.1)', borderRadius: '12px', backdropFilter: 'blur(8px)' }}
                itemStyle={{ color: '#fff', fontWeight: 600 }}
                labelStyle={{ color: '#a1a1aa', marginBottom: '8px' }}
                formatter={(value: any) => [formatCurrency(Number(value)), 'Net Worth']}
                labelFormatter={(label) => new Date(label).toLocaleDateString(undefined, { year: 'numeric', month: 'long', day: 'numeric' })}
              />
              <Area 
                type="monotone" 
                dataKey="netWorth" 
                stroke="#8b5cf6" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorNetWorth)" 
                animationDuration={1500}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
