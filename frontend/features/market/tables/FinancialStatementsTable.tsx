"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useFinancialStatements } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';

export function FinancialStatementsTable({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useFinancialStatements(ticker);
  const [statementType, setStatementType] = useState<'income' | 'balance' | 'cashflow'>('income');

  if (isError) {
    return <WidgetError title="Financials Error" message="Failed to load statements." onRetry={refetch} />;
  }

  const renderTable = (type: 'income' | 'balance' | 'cashflow') => {
    if (isLoading || !data) {
      return (
        <div className="space-y-4 p-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <Skeleton key={i} className="h-10 w-full" />
          ))}
        </div>
      );
    }

    const statements = data[type] || [];
    if (statements.length === 0) return <div className="p-8 text-center text-muted-foreground">No data available.</div>;

    const years = statements.map(s => s.year).sort((a, b) => b - a);
    
    // We'll transpose the data: rows are metrics, columns are years
    const metrics = [
      { key: 'revenue', label: 'Revenue' },
      { key: 'costOfRevenue', label: 'Cost of Revenue' },
      { key: 'grossProfit', label: 'Gross Profit' },
      { key: 'operatingExpenses', label: 'Operating Expenses' },
      { key: 'operatingIncome', label: 'Operating Income' },
      { key: 'netIncome', label: 'Net Income' },
      { key: 'eps', label: 'EPS', format: 'number' },
    ];

    return (
      <div className="overflow-x-auto">
        <table className="w-full text-sm text-left">
          <thead className="text-xs text-muted-foreground uppercase bg-muted/30">
            <tr>
              <th className="px-6 py-4 font-medium tracking-wider sticky left-0 bg-card/90 backdrop-blur z-10 w-48">Metric</th>
              {years.map(year => (
                <th key={year} className="px-6 py-4 font-medium tracking-wider text-right">{year}</th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            {metrics.map(metric => (
              <tr key={metric.key} className="hover:bg-accent/20 transition-colors">
                <td className="px-6 py-4 font-medium sticky left-0 bg-card/90 backdrop-blur z-10">
                  {metric.label}
                </td>
                {years.map(year => {
                  const stat = statements.find(s => s.year === year) as any;
                  const val = stat ? stat[metric.key] : null;
                  const formatted = val == null ? '-' : 
                    metric.format === 'number' ? val.toFixed(2) : 
                    new Intl.NumberFormat('en-US', { notation: 'compact', compactDisplay: 'short' }).format(val);
                  
                  return (
                    <td key={year} className="px-6 py-4 text-right tabular-nums">
                      {formatted}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg overflow-hidden">
      <CardHeader className="pb-0 border-b border-border/50 px-0">
        <div className="px-6 flex items-center justify-between pb-4">
          <CardTitle className="text-lg font-semibold">Financial Statements</CardTitle>
        </div>
        <Tabs value={statementType} onValueChange={(v) => setStatementType(v as any)} className="w-full px-6">
          <TabsList className="bg-transparent h-auto p-0 border-b border-transparent space-x-6 w-full justify-start rounded-none">
            <TabsTrigger value="income" className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-indigo-500 rounded-none px-0 pb-3 pt-2">Income Statement</TabsTrigger>
            <TabsTrigger value="balance" className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-indigo-500 rounded-none px-0 pb-3 pt-2">Balance Sheet</TabsTrigger>
            <TabsTrigger value="cashflow" className="data-[state=active]:bg-transparent data-[state=active]:shadow-none data-[state=active]:border-b-2 data-[state=active]:border-indigo-500 rounded-none px-0 pb-3 pt-2">Cash Flow</TabsTrigger>
          </TabsList>
        </Tabs>
      </CardHeader>
      <CardContent className="p-0">
        {renderTable(statementType)}
      </CardContent>
    </Card>
  );
}
