"use client";

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { useGlobalMarkets } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { AreaChart, Area, ResponsiveContainer, YAxis } from 'recharts';
import { cn } from '@/lib/utils';
import { ArrowDownRight, ArrowUpRight } from 'lucide-react';
import { motion } from 'framer-motion';

export function GlobalMarkets() {
  const { data, isLoading, isError, refetch } = useGlobalMarkets();

  if (isError) {
    return (
      <div className="w-full">
        <WidgetError title="Global Markets Error" message="Failed to load indices." onRetry={refetch} />
      </div>
    );
  }

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item = {
    hidden: { opacity: 0, x: -20 },
    show: { opacity: 1, x: 0, transition: { type: "spring" } }
  };

  if (isLoading || !data) {
    return (
      <div className="flex gap-4 overflow-x-auto pb-4 snap-x">
        {Array.from({ length: 5 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-64 flex-shrink-0 rounded-xl" />
        ))}
      </div>
    );
  }

  return (
    <motion.div 
      variants={container as any}
      initial="hidden"
      animate="show"
      className="flex gap-4 overflow-x-auto pb-4 snap-x scrollbar-hide"
    >
      {data.map((index, i) => {
        const isPositive = index.changePercent >= 0;
        const color = isPositive ? '#10b981' : '#ef4444';
        const chartData = index.sparkline?.map((val, idx) => ({ time: idx, value: val })) || [];

        return (
          <motion.div key={i} variants={item as any} className="snap-start">
            <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg hover:bg-card/80 transition-colors w-64 shrink-0 overflow-hidden">
              <CardContent className="p-4 flex flex-col justify-between h-full relative">
                <div className="flex justify-between items-start z-10 relative">
                  <div>
                    <h3 className="font-semibold text-sm text-muted-foreground">{index.name}</h3>
                    <div className="text-xl font-bold mt-1">
                      {new Intl.NumberFormat('en-US').format(index.price)}
                    </div>
                  </div>
                  <div className={cn(
                    "flex items-center text-xs font-medium px-2 py-1 rounded-full",
                    isPositive ? "bg-emerald-500/10 text-emerald-500" : "bg-destructive/10 text-destructive"
                  )}>
                    {isPositive ? <ArrowUpRight className="h-3 w-3 mr-1" /> : <ArrowDownRight className="h-3 w-3 mr-1" />}
                    {Math.abs(index.changePercent).toFixed(2)}%
                  </div>
                </div>
                
                <div className="absolute bottom-0 left-0 right-0 h-16 opacity-30 pointer-events-none">
                  {chartData.length > 0 && (
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={chartData}>
                        <defs>
                          <linearGradient id={`grad-${index.symbol}`} x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor={color} stopOpacity={1}/>
                            <stop offset="95%" stopColor={color} stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <YAxis domain={['auto', 'auto']} hide />
                        <Area type="monotone" dataKey="value" stroke={color} fill={`url(#grad-${index.symbol})`} strokeWidth={2} />
                      </AreaChart>
                    </ResponsiveContainer>
                  )}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        );
      })}
    </motion.div>
  );
}
