"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEarnings } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';

export function EarningsTimeline({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useEarnings(ticker);

  if (isError) {
    return <WidgetError title="Earnings Error" message="Failed to load earnings data." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px]">
        <CardContent className="p-6 h-full flex flex-col justify-end">
          <div className="flex gap-4 items-end h-full w-full opacity-50">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex-1 flex gap-1 items-end h-full">
                <Skeleton className="w-1/2" style={{ height: `${Math.random() * 60 + 20}%` }} />
                <Skeleton className="w-1/2 bg-indigo-500/20" style={{ height: `${Math.random() * 60 + 20}%` }} />
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    );
  }

  // Format data for Recharts
  const chartData = data.slice(0, 4).reverse().map(d => ({
    date: new Date(d.date).toLocaleDateString(undefined, { month: 'short', year: '2-digit' }),
    actual: d.epsActual,
    estimate: d.epsEstimate,
    surprise: d.surprisePercent
  }));

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Earnings (EPS)</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 w-full min-h-0 relative p-4 pt-0">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 0, left: -20, bottom: 0 }}>
            <XAxis dataKey="date" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
            <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val}`} />
            <Tooltip
              contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '0.5rem' }}
              itemStyle={{ color: 'var(--foreground)' }}
              formatter={(value: any, name) => [`$${value.toFixed(2)}`, String(name).charAt(0).toUpperCase() + String(name).slice(1)]}
            />
            <ReferenceLine y={0} stroke="#334155" />
            <Bar dataKey="estimate" fill="#475569" radius={[4, 4, 0, 0]} name="Estimate" />
            <Bar dataKey="actual" fill="#4f46e5" radius={[4, 4, 0, 0]} name="Actual" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
