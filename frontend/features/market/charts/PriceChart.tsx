"use client";

import React, { useState } from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { usePriceData } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export function PriceChart({ ticker }: { ticker: string }) {
  const [range, setRange] = useState('1Y');
  const { data, isLoading, isError, refetch } = usePriceData(ticker, range);

  if (isError) {
    return <WidgetError title="Chart Error" message="Failed to load price data." onRetry={refetch} />;
  }

  const getOption = () => {
    if (!data) return {};

    const categoryData = data.map(d => new Date(d.time).toLocaleDateString());
    const values = data.map(d => [d.open, d.close, d.low, d.high]);
    const volumes = data.map((d, i) => [i, d.volume, d.close > d.open ? 1 : -1]);

    const upColor = '#10b981';
    const downColor = '#ef4444';

    return {
      tooltip: {
        trigger: 'axis',
        axisPointer: { type: 'cross' },
        backgroundColor: 'rgba(15, 23, 42, 0.9)',
        borderColor: '#334155',
        textStyle: { color: '#f8fafc' },
      },
      axisPointer: { link: { xAxisIndex: 'all' } },
      grid: [
        { left: '5%', right: '3%', top: '5%', height: '65%' },
        { left: '5%', right: '3%', top: '75%', height: '20%' }
      ],
      xAxis: [
        {
          type: 'category',
          data: categoryData,
          scale: true,
          boundaryGap: false,
          axisLine: { onZero: false, lineStyle: { color: '#475569' } },
          splitLine: { show: false },
          min: 'dataMin',
          max: 'dataMax'
        },
        {
          type: 'category',
          gridIndex: 1,
          data: categoryData,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false }
        }
      ],
      yAxis: [
        {
          scale: true,
          splitLine: { lineStyle: { color: '#1e293b' } },
          axisLine: { show: false },
          axisLabel: { formatter: '${value}', color: '#94a3b8' }
        },
        {
          scale: true,
          gridIndex: 1,
          splitNumber: 2,
          axisLabel: { show: false },
          axisLine: { show: false },
          axisTick: { show: false },
          splitLine: { show: false }
        }
      ],
      dataZoom: [
        { type: 'inside', xAxisIndex: [0, 1], start: 0, end: 100 },
        { show: true, type: 'slider', xAxisIndex: [0, 1], bottom: 0, start: 0, end: 100,
          borderColor: 'transparent',
          fillerColor: 'rgba(79, 70, 229, 0.2)',
          handleStyle: { color: '#4f46e5' },
          textStyle: { color: '#94a3b8' }
        }
      ],
      series: [
        {
          name: 'Price',
          type: 'candlestick',
          data: values,
          itemStyle: {
            color: upColor,
            color0: downColor,
            borderColor: upColor,
            borderColor0: downColor
          }
        },
        {
          name: 'Volume',
          type: 'bar',
          xAxisIndex: 1,
          yAxisIndex: 1,
          data: volumes,
          itemStyle: {
            color: (params: any) => {
              return params.value[2] > 0 ? upColor : downColor;
            },
            opacity: 0.5
          }
        }
      ]
    };
  };

  const ranges = ['1D', '1W', '1M', '3M', '6M', '1Y', '5Y', 'MAX'];

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[500px] flex flex-col overflow-hidden">
      <CardHeader className="pb-2 flex flex-row items-center justify-between border-b border-white/5">
        <CardTitle className="text-lg font-semibold">Price Action</CardTitle>
        <div className="flex bg-muted/30 p-1 rounded-md">
          {ranges.map(r => (
            <button
              key={r}
              onClick={() => setRange(r)}
              className={cn(
                "px-2 py-1 text-xs font-medium rounded-sm transition-colors",
                range === r ? "bg-card shadow-sm text-foreground" : "text-muted-foreground hover:text-foreground"
              )}
            >
              {r}
            </button>
          ))}
        </div>
      </CardHeader>
      <CardContent className="flex-1 w-full min-h-0 relative p-0">
        {isLoading || !data ? (
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <Skeleton className="h-full w-full rounded-md" />
          </div>
        ) : (
          <ReactECharts
            option={getOption()}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'canvas' }}
            notMerge={true}
          />
        )}
      </CardContent>
    </Card>
  );
}
