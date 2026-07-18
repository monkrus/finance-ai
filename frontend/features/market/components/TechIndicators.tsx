"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useTechIndicators } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Activity, TrendingUp, BarChart2, Waves } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export function TechIndicators({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useTechIndicators(ticker);

  if (isError) {
    return <WidgetError title="Indicators Error" message="Failed to load technicals." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  const indicators = [
    {
      label: 'RSI (14)',
      value: data.rsi.toFixed(2),
      status: data.rsi > 70 ? 'Overbought' : data.rsi < 30 ? 'Oversold' : 'Neutral',
      statusColor: data.rsi > 70 ? 'text-destructive' : data.rsi < 30 ? 'text-emerald-500' : 'text-muted-foreground',
      icon: <Activity className="h-4 w-4" />
    },
    {
      label: 'MACD (12,26)',
      value: data.macd.value.toFixed(2),
      status: data.macd.hist > 0 ? 'Bullish' : 'Bearish',
      statusColor: data.macd.hist > 0 ? 'text-emerald-500' : 'text-destructive',
      icon: <TrendingUp className="h-4 w-4" />
    },
    {
      label: 'Bollinger Bands',
      value: `W: ${((data.bollingerBands.upper - data.bollingerBands.lower) / data.bollingerBands.middle * 100).toFixed(1)}%`,
      status: 'Volatility',
      statusColor: 'text-indigo-400',
      icon: <Waves className="h-4 w-4" />
    },
    {
      label: 'ADX (14)',
      value: data.adx.toFixed(2),
      status: data.adx > 25 ? 'Strong Trend' : 'Weak Trend',
      statusColor: data.adx > 25 ? 'text-emerald-500' : 'text-muted-foreground',
      icon: <BarChart2 className="h-4 w-4" />
    }
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {indicators.map((ind, i) => (
        <motion.div
          key={ind.label}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.1 }}
        >
          <Card className="bg-card/40 backdrop-blur-md border-white/5 shadow-sm">
            <CardHeader className="p-4 pb-2 flex flex-row items-center justify-between space-y-0">
              <CardTitle className="text-xs font-medium text-muted-foreground">{ind.label}</CardTitle>
              <div className="text-muted-foreground opacity-50">{ind.icon}</div>
            </CardHeader>
            <CardContent className="p-4 pt-0">
              <div className="text-xl font-bold">{ind.value}</div>
              <div className={cn("text-xs font-medium mt-1", ind.statusColor)}>
                {ind.status}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  );
}
