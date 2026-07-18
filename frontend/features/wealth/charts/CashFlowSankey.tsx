"use client";

import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useCashFlowSummary } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { RefreshCw, ArrowUpRight, ArrowDownRight, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';

export function CashFlowSankey() {
  const { data, isLoading, isError, refetch } = useCashFlowSummary();

  if (isError) {
    return <WidgetError title="Cash Flow Error" message="Failed to load cash flow." onRetry={refetch} />;
  }

  const formatCurrency = (v: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(v);

  const getOption = () => {
    if (!data) return {};

    const nodes = [
      ...data.incomeSources.map(s => ({ name: s.source, itemStyle: { color: '#10b981' } })),
      { name: 'Total Income', itemStyle: { color: '#4f46e5' } },
      ...data.expenseCategories.map(c => ({ name: c.category, itemStyle: { color: '#ef4444' } })),
      { name: 'Free Cash Flow', itemStyle: { color: '#8b5cf6' } }
    ];

    const links = [
      ...data.incomeSources.map(s => ({ source: s.source, target: 'Total Income', value: s.amount })),
      ...data.expenseCategories.map(c => ({ source: 'Total Income', target: c.category, value: c.amount })),
      { source: 'Total Income', target: 'Free Cash Flow', value: data.freeCashFlow > 0 ? data.freeCashFlow : 0 }
    ];

    return {
      tooltip: {
        trigger: 'item',
        triggerOn: 'mousemove',
        formatter: (params: any) => {
          if (params.dataType === 'node') {
            return `${params.name}: ${formatCurrency(params.value)}`;
          }
          return `${params.data.source} → ${params.data.target}: ${formatCurrency(params.data.value)}`;
        },
        backgroundColor: 'rgba(9, 9, 11, 0.9)',
        borderColor: 'rgba(255,255,255,0.1)',
        textStyle: { color: '#f8fafc' },
        borderRadius: 8
      },
      series: {
        type: 'sankey',
        layout: 'none',
        emphasis: {
          focus: 'adjacency'
        },
        nodeAlign: 'justify',
        data: nodes,
        links: links,
        lineStyle: {
          color: 'source',
          curveness: 0.5,
          opacity: 0.2
        },
        label: {
          color: '#f8fafc',
          fontSize: 12
        }
      }
    };
  };

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard title="Monthly Income" amount={data?.monthlyIncome} icon={<ArrowUpRight />} loading={isLoading} highlight="emerald" />
        <MetricCard title="Monthly Expenses" amount={data?.monthlyExpenses} icon={<ArrowDownRight />} loading={isLoading} />
        <MetricCard title="Free Cash Flow" amount={data?.freeCashFlow} icon={<Activity />} loading={isLoading} highlight="indigo" />
      </div>

      <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-lg h-[600px] flex flex-col">
        <CardHeader className="pb-2 border-b border-white/5">
          <CardTitle className="text-lg font-semibold flex items-center">
            <RefreshCw className="h-5 w-5 mr-2 text-indigo-400" />
            Cash Flow Sankey Diagram
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 w-full min-h-0 relative p-6">
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
    </div>
  );
}

function MetricCard({ title, amount, icon, loading, highlight }: any) {
  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
      <CardContent className="p-6">
        <div className="flex justify-between items-start mb-4">
          <div className="p-2 bg-muted/50 rounded-lg text-muted-foreground border border-white/5">
            {React.cloneElement(icon, { className: 'w-5 h-5' })}
          </div>
        </div>
        <div className="text-sm font-medium text-muted-foreground mb-1">{title}</div>
        {loading || amount === undefined ? (
          <Skeleton className="h-8 w-32 mt-2" />
        ) : (
          <div className={cn(
            "text-3xl font-bold tracking-tight",
            highlight === 'emerald' ? 'text-emerald-500' : highlight === 'indigo' ? 'text-indigo-400' : 'text-foreground'
          )}>
            {new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(amount)}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
