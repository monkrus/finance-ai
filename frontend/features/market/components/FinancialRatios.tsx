"use client";

import React from 'react';
import { Card, CardContent, CardTitle } from '@/components/ui/card';
import { useFinancialRatios } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';

export function FinancialRatios({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useFinancialRatios(ticker);

  if (isError) {
    return <WidgetError title="Ratios Error" message="Failed to load financial ratios." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {Array.from({ length: 10 }).map((_, i) => (
          <Skeleton key={i} className="h-24 w-full" />
        ))}
      </div>
    );
  }

  const ratios = [
    { label: 'P/E Ratio', value: data.pe?.toFixed(2) ?? '-' },
    { label: 'P/B Ratio', value: data.pb?.toFixed(2) ?? '-' },
    { label: 'PEG Ratio', value: data.peg?.toFixed(2) ?? '-' },
    { label: 'EV/EBITDA', value: data.evToEbitda?.toFixed(2) ?? '-' },
    { label: 'ROE', value: data.roe ? `${(data.roe * 100).toFixed(1)}%` : '-' },
    { label: 'ROA', value: data.roa ? `${(data.roa * 100).toFixed(1)}%` : '-' },
    { label: 'ROIC', value: data.roic ? `${(data.roic * 100).toFixed(1)}%` : '-' },
    { label: 'Current Ratio', value: data.currentRatio?.toFixed(2) ?? '-' },
    { label: 'Gross Margin', value: data.grossMargin ? `${(data.grossMargin * 100).toFixed(1)}%` : '-' },
    { label: 'Net Margin', value: data.netMargin ? `${(data.netMargin * 100).toFixed(1)}%` : '-' },
  ];

  return (
    <div className="space-y-4">
      <h3 className="text-lg font-semibold tracking-tight">Key Financial Ratios</h3>
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
        {ratios.map((ratio, i) => (
          <motion.div
            key={ratio.label}
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.05 }}
          >
            <Card className="bg-card/40 backdrop-blur-md border-white/5 shadow-sm h-full flex flex-col justify-center text-center py-4">
              <CardTitle className="text-xs font-medium text-muted-foreground mb-1">{ratio.label}</CardTitle>
              <CardContent className="p-0">
                <div className="text-xl font-bold">{ratio.value}</div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>
    </div>
  );
}
