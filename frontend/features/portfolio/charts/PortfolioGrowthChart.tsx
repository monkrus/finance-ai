"use client";

import React from 'react';
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { usePortfolioPerformance } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';

export function PortfolioGrowthChart() {
  const { data, isLoading, isError, refetch } = usePortfolioPerformance('1Y');

  if (isError) {
    return <WidgetError title="Growth Chart Error" message="Failed to load performance data." onRetry={refetch} />;
  }

  return (
    <Card className="col-span-full lg:col-span-2 bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Portfolio Growth</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 w-full px-2 pb-4">
        {isLoading || !data ? (
          <div className="h-full w-full flex items-end space-x-2 p-4">
            {Array.from({length: 12}).map((_, i) => (
              <Skeleton key={i} className="w-full" style={{ height: `${Math.random() * 80 + 20}%` }} />
            ))}
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis 
                dataKey="date" 
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(val) => {
                  const date = new Date(val);
                  return `${date.toLocaleString('default', { month: 'short' })} ${date.getDate()}`;
                }}
              />
              <YAxis 
                stroke="#888888"
                fontSize={12}
                tickLine={false}
                axisLine={false}
                tickFormatter={(value) => `$${(value / 1000)}k`}
                domain={['auto', 'auto']}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'var(--card)',
                  borderColor: 'var(--border)',
                  borderRadius: '0.5rem',
                  boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)'
                }}
                itemStyle={{ color: 'var(--foreground)' }}
                labelFormatter={(label) => new Date(label).toLocaleDateString()}
                formatter={(value: any) => [new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value), 'Value']}
              />
              <Area
                type="monotone"
                dataKey="portfolioValue"
                stroke="#4f46e5"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorValue)"
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </CardContent>
    </Card>
  );
}
