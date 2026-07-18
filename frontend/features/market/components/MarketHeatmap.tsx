"use client";

import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useSectorPerformance } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';

export function MarketHeatmap() {
  const { data, isLoading, isError, refetch } = useSectorPerformance();

  if (isError) {
    return <WidgetError title="Heatmap Error" message="Failed to load sector performance." onRetry={refetch} />;
  }

  const getOption = () => {
    if (!data) return {};

    return {
      tooltip: {
        position: 'top',
        formatter: (params: any) => `${params.name}: ${params.value > 0 ? '+' : ''}${params.value}%`
      },
      visualMap: {
        min: -5,
        max: 5,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0%',
        inRange: {
          color: ['#ef4444', '#1e293b', '#10b981'] // Red -> Slate -> Green
        }
      },
      series: [{
        name: 'Sector Performance',
        type: 'treemap',
        visibleMin: 300,
        label: {
          show: true,
          formatter: '{b}\n{c}%'
        },
        itemStyle: {
          borderColor: '#0f172a'
        },
        roam: false,
        nodeClick: false,
        data: data.map(item => ({
          name: item.sector,
          value: item.performance
        }))
      }]
    };
  };

  return (
    <Card className="col-span-full bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Market Heatmap</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 w-full min-h-0 relative">
        {isLoading || !data ? (
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <Skeleton className="h-full w-full rounded-md" />
          </div>
        ) : (
          <ReactECharts
            option={getOption()}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'svg' }}
          />
        )}
      </CardContent>
    </Card>
  );
}
