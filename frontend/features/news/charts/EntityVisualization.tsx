"use client";

import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEntityGraph } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';

export function EntityVisualization({ articleId }: { articleId: string }) {
  const { data, isLoading, isError, refetch } = useEntityGraph(articleId);

  if (isError) {
    return <WidgetError title="Entity Error" message="Failed to load graph." onRetry={refetch} />;
  }

  const getOption = () => {
    if (!data) return {};

    const colorMap: Record<string, string> = {
      'Company': '#4f46e5', // indigo
      'Person': '#10b981', // emerald
      'Country': '#f59e0b', // amber
      'Product': '#ec4899', // pink
      'Regulator': '#ef4444', // red
      'Industry': '#8b5cf6', // violet
    };

    const nodes = data.nodes.map(n => ({
      id: n.id,
      name: n.name,
      symbolSize: Math.max(20, n.relevance * 50),
      category: n.type,
      itemStyle: { color: colorMap[n.type] || '#cbd5e1' }
    }));

    const links = data.links.map(l => ({
      source: l.sourceId,
      target: l.targetId,
      lineStyle: { width: l.strength * 5, opacity: 0.6 }
    }));

    const categories = Object.keys(colorMap).map(k => ({ name: k }));

    return {
      tooltip: { formatter: '{b}' },
      legend: {
        data: categories.map(a => a.name),
        textStyle: { color: '#94a3b8' },
        bottom: 0
      },
      series: [{
        type: 'graph',
        layout: 'force',
        animation: false,
        roam: true,
        draggable: true,
        data: nodes,
        categories: categories,
        force: {
          repulsion: 300,
          edgeLength: 100
        },
        edges: links,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
          color: '#f8fafc',
          fontSize: 10
        },
        lineStyle: {
          color: 'source',
          curveness: 0.2
        }
      }]
    };
  };

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[500px] flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Entity Relationships</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 w-full min-h-0 relative p-2">
        {isLoading || !data ? (
          <div className="absolute inset-0 flex items-center justify-center p-4">
            <Skeleton className="h-full w-full rounded-md" />
          </div>
        ) : (
          <ReactECharts
            option={getOption()}
            style={{ height: '100%', width: '100%' }}
            opts={{ renderer: 'canvas' }}
          />
        )}
      </CardContent>
    </Card>
  );
}
