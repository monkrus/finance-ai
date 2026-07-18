"use client";

import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { usePortfolioAllocation } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';

export function RiskHeatmap() {
  const { data, isLoading, isError, refetch } = usePortfolioAllocation('sector');

  if (isError) {
    return <WidgetError title="Heatmap Error" message="Failed to load risk heatmap." onRetry={refetch} />;
  }

  const getOption = () => {
    if (!data) return {};

    const maxVal = Math.max(...data.map(d => d.value));

    return {
      tooltip: {
        position: 'top',
        formatter: (params: any) => `${params.name}: ${params.value}%`
      },
      visualMap: {
        min: 0,
        max: maxVal,
        calculable: true,
        orient: 'horizontal',
        left: 'center',
        bottom: '0%',
        inRange: {
          color: ['#cde4fa', '#4f46e5', '#312e81']
        }
      },
      series: [{
        name: 'Risk Map',
        type: 'treemap',
        visibleMin: 300,
        label: {
          show: true,
          formatter: '{b}'
        },
        itemStyle: {
          borderColor: 'transparent'
        },
        roam: false,
        nodeClick: false,
        data: data.map(item => ({
          name: item.name,
          value: item.value
        }))
      }]
    };
  };

  return (
    <Card className="col-span-full bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Sector Exposure</CardTitle>
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
