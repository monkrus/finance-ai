"use client";

import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ChartIntent } from '../types';
import { BarChart3 } from 'lucide-react';

export function ChartCard({ intent }: { intent: ChartIntent }) {
  
  const getOption = () => {
    // Generate basic ECharts option from backend intent
    const isPie = intent.type === 'donut';
    return {
      tooltip: { trigger: isPie ? 'item' : 'axis', backgroundColor: 'rgba(9, 9, 11, 0.9)', borderColor: 'rgba(255,255,255,0.1)', textStyle: { color: '#f8fafc' } },
      xAxis: isPie ? undefined : { type: 'category', data: intent.data.map(d => d[intent.xAxisKey || 'name']) },
      yAxis: isPie ? undefined : { type: 'value', splitLine: { lineStyle: { color: 'rgba(255,255,255,0.05)' } } },
      series: [
        {
          data: intent.data.map(d => isPie ? { name: d[intent.xAxisKey || 'name'], value: d[intent.seriesKey || 'value'] } : d[intent.seriesKey || 'value']),
          type: intent.type === 'donut' ? 'pie' : intent.type,
          radius: intent.type === 'donut' ? ['40%', '70%'] : undefined,
          smooth: intent.type === 'line' || intent.type === 'area',
          areaStyle: intent.type === 'area' ? { opacity: 0.2 } : undefined,
          itemStyle: { borderRadius: intent.type === 'bar' ? [4,4,0,0] : 0 }
        }
      ],
      color: ['#8b5cf6', '#10b981', '#3b82f6', '#f59e0b', '#ec4899']
    };
  };

  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 my-4 w-full max-w-2xl">
      <CardHeader className="pb-2 border-b border-white/5 px-4 py-3">
        <CardTitle className="text-sm font-semibold flex items-center">
          <BarChart3 className="h-4 w-4 mr-2 text-indigo-400" />
          {intent.title}
        </CardTitle>
      </CardHeader>
      <CardContent className="p-4 h-[250px]">
        <ReactECharts
          option={getOption()}
          style={{ height: '100%', width: '100%' }}
          opts={{ renderer: 'canvas' }}
        />
      </CardContent>
    </Card>
  );
}
