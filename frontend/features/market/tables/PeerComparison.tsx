"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { usePeerComparison } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';

export function PeerComparison({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = usePeerComparison(ticker);

  if (isError) {
    return <WidgetError title="Peers Error" message="Failed to load peer comparison." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg mt-6">
        <CardContent className="p-6">
          <Skeleton className="h-48 w-full" />
        </CardContent>
      </Card>
    );
  }

  // Find best values for highlighting
  const bestPE = Math.min(...data.filter(p => p.pe > 0).map(p => p.pe));
  const bestROE = Math.max(...data.map(p => p.roe));
  const bestMargin = Math.max(...data.map(p => p.grossMargin));

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg mt-6 overflow-hidden">
      <CardHeader className="pb-4 border-b border-white/5">
        <CardTitle className="text-lg font-semibold">Peer Comparison</CardTitle>
      </CardHeader>
      <CardContent className="p-0 overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-muted/30">
            <tr>
              <th className="px-6 py-4 font-medium tracking-wider">Company</th>
              <th className="px-6 py-4 font-medium tracking-wider text-right">Price</th>
              <th className="px-6 py-4 font-medium tracking-wider text-right">Market Cap</th>
              <th className="px-6 py-4 font-medium tracking-wider text-right">Revenue</th>
              <th className="px-6 py-4 font-medium tracking-wider text-right">P/E</th>
              <th className="px-6 py-4 font-medium tracking-wider text-right">ROE</th>
              <th className="px-6 py-4 font-medium tracking-wider text-right">Gross Margin</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {data.map((peer) => (
              <tr key={peer.symbol} className="hover:bg-accent/20 transition-colors">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="font-bold">{peer.symbol}</div>
                  <div className="text-xs text-muted-foreground truncate w-32">{peer.companyName}</div>
                </td>
                <td className="px-6 py-4 text-right whitespace-nowrap">
                  ${peer.price.toFixed(2)}
                </td>
                <td className="px-6 py-4 text-right whitespace-nowrap">
                  ${(peer.marketCap / 1e9).toFixed(1)}B
                </td>
                <td className="px-6 py-4 text-right whitespace-nowrap">
                  ${(peer.revenue / 1e9).toFixed(1)}B
                </td>
                <td className={`px-6 py-4 text-right font-medium whitespace-nowrap ${peer.pe === bestPE ? 'text-emerald-500' : ''}`}>
                  {peer.pe > 0 ? peer.pe.toFixed(2) : '-'}
                </td>
                <td className={`px-6 py-4 text-right font-medium whitespace-nowrap ${peer.roe === bestROE ? 'text-emerald-500' : ''}`}>
                  {(peer.roe * 100).toFixed(1)}%
                </td>
                <td className={`px-6 py-4 text-right font-medium whitespace-nowrap ${peer.grossMargin === bestMargin ? 'text-emerald-500' : ''}`}>
                  {(peer.grossMargin * 100).toFixed(1)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CardContent>
    </Card>
  );
}
