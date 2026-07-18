"use client";

import React from 'react';
import ReactECharts from 'echarts-for-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useWealthPlan } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { ShieldCheck, HeartPulse } from 'lucide-react';

export function RetirementGauge() {
  const { data, isLoading, isError, refetch } = useWealthPlan();

  if (isError) {
    return <WidgetError title="Planning Error" message="Failed to load plan." onRetry={refetch} />;
  }

  const getGaugeOption = (value: number, name: string) => ({
    series: [
      {
        type: 'gauge',
        startAngle: 180,
        endAngle: 0,
        min: 0,
        max: 100,
        splitNumber: 10,
        itemStyle: {
          color: '#8b5cf6',
          shadowColor: 'rgba(139, 92, 246, 0.4)',
          shadowBlur: 10,
          shadowOffsetX: 2,
          shadowOffsetY: 2
        },
        progress: {
          show: true,
          roundCap: true,
          width: 12
        },
        pointer: {
          icon: 'path://M12.8,0.7l12,40.1H0.7L12.8,0.7z',
          length: '12%',
          width: 10,
          offsetCenter: [0, '-60%'],
          itemStyle: { color: 'auto' }
        },
        axisLine: {
          roundCap: true,
          lineStyle: { width: 12, color: [[1, '#334155']] }
        },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
        title: { show: false },
        detail: {
          valueAnimation: true,
          offsetCenter: [0, '0%'],
          fontSize: 32,
          fontWeight: 'bolder',
          formatter: '{value}%',
          color: '#f8fafc'
        },
        data: [{ value, name }]
      }
    ]
  });

  return (
    <div className="space-y-6">
      <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-lg h-[300px] flex flex-col">
        <CardHeader className="pb-0">
          <CardTitle className="text-lg font-semibold flex items-center">
            <ShieldCheck className="h-5 w-5 mr-2 text-indigo-400" />
            Retirement Readiness
          </CardTitle>
        </CardHeader>
        <CardContent className="flex-1 w-full min-h-0 relative p-4 pb-0 flex items-center justify-center">
          {isLoading || !data ? (
            <Skeleton className="h-48 w-48 rounded-full" />
          ) : (
            <ReactECharts
              option={getGaugeOption(data.retirementReadiness, 'Readiness')}
              style={{ height: '220px', width: '100%' }}
              opts={{ renderer: 'canvas' }}
            />
          )}
        </CardContent>
      </Card>

      <Card className="bg-card/60 backdrop-blur-xl border-white/10 shadow-lg relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/20 rounded-full blur-3xl pointer-events-none -translate-y-1/2 translate-x-1/2" />
        <CardContent className="p-6">
          <div className="flex items-center gap-4 mb-4">
            <div className="p-3 bg-emerald-500/10 rounded-xl border border-white/5">
              <HeartPulse className="h-6 w-6 text-emerald-500" />
            </div>
            <div>
              <div className="text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-1">Health Score</div>
              {isLoading || !data ? (
                <Skeleton className="h-8 w-24" />
              ) : (
                <div className="text-3xl font-bold">{data.healthScore} <span className="text-lg font-medium text-muted-foreground">/ 1000</span></div>
              )}
            </div>
          </div>
          
          <div className="space-y-4 pt-4 border-t border-border/50">
            {isLoading || !data ? (
              <div className="space-y-2">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-2/3" />
              </div>
            ) : (
              <>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">Savings Ratio</span>
                  <span className="font-semibold">{data.savingsRatio.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">Debt-to-Income</span>
                  <span className="font-semibold">{data.debtToIncomeRatio.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">Emergency Fund</span>
                  <span className="font-semibold">{data.emergencyFundMonths.toFixed(1)} mo</span>
                </div>
                <div className="flex justify-between items-center text-sm">
                  <span className="text-muted-foreground">FIRE Progress</span>
                  <span className="font-semibold text-indigo-400">{data.fireProgress.toFixed(1)}%</span>
                </div>
              </>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
