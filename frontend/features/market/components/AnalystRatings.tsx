"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useAnalystRatings } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

export function AnalystRatings({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useAnalystRatings(ticker);

  if (isError) {
    return <WidgetError title="Ratings Error" message="Failed to load analyst ratings." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px]">
        <CardContent className="p-6 h-full flex items-center justify-center">
          <Skeleton className="h-48 w-48 rounded-full" />
        </CardContent>
      </Card>
    );
  }

  const pieData = [
    { name: 'Buy', value: data.buy, color: '#10b981' }, // emerald
    { name: 'Hold', value: data.hold, color: '#f59e0b' }, // amber
    { name: 'Sell', value: data.sell, color: '#ef4444' }  // red
  ].filter(d => d.value > 0);

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Analyst Consensus</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 w-full min-h-0 relative p-4 flex flex-col sm:flex-row items-center">
        <div className="w-full sm:w-1/2 h-48 sm:h-full relative">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={pieData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={70}
                paddingAngle={5}
                dataKey="value"
                stroke="none"
              >
                {pieData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ backgroundColor: 'var(--card)', borderColor: 'var(--border)', borderRadius: '0.5rem' }}
                itemStyle={{ color: 'var(--foreground)' }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="absolute inset-0 flex items-center justify-center pointer-events-none flex-col">
            <span className="text-xl font-bold">{data.buy + data.hold + data.sell}</span>
            <span className="text-[10px] text-muted-foreground uppercase">Ratings</span>
          </div>
        </div>

        <div className="w-full sm:w-1/2 flex flex-col justify-center space-y-4 pl-0 sm:pl-4 mt-4 sm:mt-0">
          <div className="p-3 rounded-lg bg-muted/30 border border-white/5 text-center">
            <div className="text-xs text-muted-foreground mb-1">Consensus</div>
            <div className={`font-bold text-lg ${
              data.consensus.includes('Buy') ? 'text-emerald-500' :
              data.consensus.includes('Sell') ? 'text-destructive' :
              'text-amber-500'
            }`}>{data.consensus}</div>
          </div>
          
          <div className="space-y-2 text-sm">
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">High Target</span>
              <span className="font-medium text-emerald-500">${data.targetHigh.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Mean Target</span>
              <span className="font-medium">${data.targetMean.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-muted-foreground">Low Target</span>
              <span className="font-medium text-destructive">${data.targetLow.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
