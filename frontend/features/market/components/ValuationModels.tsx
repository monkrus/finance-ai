"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useValuation } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';

export function ValuationModels({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useValuation(ticker);

  if (isError) {
    return <WidgetError title="Valuation Error" message="Failed to load valuation models." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
        <CardContent className="p-6 space-y-4">
          <Skeleton className="h-4 w-1/3" />
          <Skeleton className="h-8 w-full" />
          <div className="grid grid-cols-2 gap-4 mt-6">
            <Skeleton className="h-20 w-full" />
            <Skeleton className="h-20 w-full" />
          </div>
        </CardContent>
      </Card>
    );
  }

  const formatCurrency = (val: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(val);

  // Calculate position of current price within the fair value range
  const rangeWidth = data.fairValueUpper - data.fairValueLower;
  const currentPos = data.currentPrice - data.fairValueLower;
  const currentPercent = Math.max(0, Math.min(100, (currentPos / rangeWidth) * 100));

  const isUndervalued = data.currentPrice < data.fairValueLower;
  const isOvervalued = data.currentPrice > data.fairValueUpper;
  const isFair = !isUndervalued && !isOvervalued;

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
      <CardHeader className="pb-2">
        <CardTitle className="text-lg font-semibold">Valuation Analysis</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Discounted Cash Flow (DCF) Base</span>
              <span className="font-bold">{formatCurrency(data.intrinsicValueDCF)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-muted-foreground">Dividend Discount Model (DDM)</span>
              <span className="font-bold">{formatCurrency(data.intrinsicValueDDM)}</span>
            </div>
          </div>

          <div className="pt-4 border-t border-border/50">
            <h4 className="text-sm font-medium mb-4">Fair Value Range vs Current Price</h4>
            <div className="relative pt-6 pb-2">
              {/* Range bar */}
              <div className="h-2 w-full bg-muted rounded-full overflow-hidden flex">
                <div className="h-full bg-emerald-500/50" style={{ width: '33.3%' }} title="Undervalued" />
                <div className="h-full bg-blue-500/50" style={{ width: '33.3%' }} title="Fairly Valued" />
                <div className="h-full bg-destructive/50" style={{ width: '33.3%' }} title="Overvalued" />
              </div>
              
              {/* Current Price Marker */}
              <motion.div 
                initial={{ left: '0%' }}
                animate={{ left: `${currentPercent}%` }}
                transition={{ duration: 1, ease: 'easeOut' }}
                className="absolute top-0 -translate-x-1/2 flex flex-col items-center"
              >
                <div className="bg-foreground text-background text-xs font-bold px-2 py-0.5 rounded shadow-sm mb-1 whitespace-nowrap">
                  {formatCurrency(data.currentPrice)}
                </div>
                <div className="w-0.5 h-6 bg-foreground" />
              </motion.div>

              <div className="flex justify-between text-xs text-muted-foreground mt-2">
                <span>{formatCurrency(data.fairValueLower)}</span>
                <span>{formatCurrency(data.fairValueUpper)}</span>
              </div>
            </div>

            <div className="mt-4 flex items-center justify-center">
              <div className={`px-4 py-1.5 rounded-full text-sm font-bold ${
                isUndervalued ? 'bg-emerald-500/10 text-emerald-500' :
                isOvervalued ? 'bg-destructive/10 text-destructive' :
                'bg-blue-500/10 text-blue-500'
              }`}>
                {isUndervalued ? 'Undervalued' : isOvervalued ? 'Overvalued' : 'Fairly Valued'}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
