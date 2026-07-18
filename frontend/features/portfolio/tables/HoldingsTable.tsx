"use client";

import React, { useMemo, useRef, useState } from 'react';
import {
  useReactTable,
  getCoreRowModel,
  getSortedRowModel,
  getFilteredRowModel,
  ColumnDef,
  flexRender,
  SortingState
} from '@tanstack/react-table';
import { useVirtualizer } from '@tanstack/react-virtual';
import { usePortfolioHoldings } from '../api/queries';
import { Holding } from '../types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { ArrowUpDown, Search } from 'lucide-react';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';

export function HoldingsTable() {
  const { data, isLoading, isError, refetch } = usePortfolioHoldings();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('');

  const columns = useMemo<ColumnDef<Holding>[]>(
    () => [
      {
        accessorKey: 'ticker',
        header: ({ column }) => (
          <button className="flex items-center space-x-1 hover:text-foreground transition-colors" onClick={() => column.toggleSorting(column.getIsSorted() === 'asc')}>
            <span>Ticker</span>
            <ArrowUpDown className="h-3 w-3" />
          </button>
        ),
        cell: (info) => <span className="font-bold">{info.getValue() as string}</span>,
        size: 100,
      },
      {
        accessorKey: 'companyName',
        header: 'Company',
        size: 180,
      },
      {
        accessorKey: 'quantity',
        header: 'Qty',
        size: 80,
      },
      {
        accessorKey: 'currentPrice',
        header: 'Price',
        cell: (info) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(info.getValue() as number),
        size: 120,
      },
      {
        accessorKey: 'marketValue',
        header: 'Market Value',
        cell: (info) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(info.getValue() as number),
        size: 140,
      },
      {
        accessorKey: 'dailyChangePercent',
        header: 'Daily %',
        cell: (info) => {
          const val = info.getValue() as number;
          return <span className={val >= 0 ? 'text-emerald-500' : 'text-destructive'}>{val >= 0 ? '+' : ''}{val.toFixed(2)}%</span>;
        },
        size: 100,
      },
      {
        accessorKey: 'totalReturnPercent',
        header: 'Total %',
        cell: (info) => {
          const val = info.getValue() as number;
          return <span className={val >= 0 ? 'text-emerald-500' : 'text-destructive'}>{val >= 0 ? '+' : ''}{val.toFixed(2)}%</span>;
        },
        size: 100,
      },
      {
        accessorKey: 'sector',
        header: 'Sector',
        size: 140,
      }
    ],
    []
  );

  const table = useReactTable({
    data: data || [],
    columns,
    state: { sorting, globalFilter },
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
  });

  const { rows } = table.getRowModel();
  const tableContainerRef = useRef<HTMLDivElement>(null);

  const rowVirtualizer = useVirtualizer({
    count: rows.length,
    getScrollElement: () => tableContainerRef.current,
    estimateSize: () => 48,
    overscan: 10,
  });

  if (isError) {
    return <WidgetError title="Holdings Error" message="Failed to load holdings." onRetry={refetch} />;
  }

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg flex flex-col h-[500px]">
      <CardHeader className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-4">
        <CardTitle>Holdings</CardTitle>
        <div className="relative w-full sm:w-64 mt-2 sm:mt-0">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search holdings..." 
            value={globalFilter ?? ''}
            onChange={(e) => setGlobalFilter(e.target.value)}
            className="pl-9 bg-background/50 backdrop-blur-sm"
          />
        </div>
      </CardHeader>
      <CardContent className="flex-1 overflow-hidden p-0">
        {isLoading ? (
          <div className="p-6 space-y-4">
            {Array.from({length: 5}).map((_, i) => (
              <Skeleton key={i} className="h-10 w-full" />
            ))}
          </div>
        ) : (
          <div 
            ref={tableContainerRef} 
            className="h-full w-full overflow-auto"
          >
            <table className="w-full text-sm text-left relative">
              <thead className="text-xs text-muted-foreground uppercase bg-muted/50 sticky top-0 z-10 backdrop-blur-md">
                {table.getHeaderGroups().map(headerGroup => (
                  <tr key={headerGroup.id}>
                    {headerGroup.headers.map(header => (
                      <th 
                        key={header.id} 
                        style={{ width: header.getSize() }} 
                        className="px-6 py-3 font-medium tracking-wider"
                      >
                        {header.isPlaceholder
                          ? null
                          : flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <tbody className="divide-y divide-border/50 bg-transparent">
                {rowVirtualizer.getVirtualItems().length === 0 ? (
                  <tr>
                    <td colSpan={columns.length} className="px-6 py-8 text-center text-muted-foreground">
                      No holdings found.
                    </td>
                  </tr>
                ) : (
                  <>
                    <tr style={{ height: `${rowVirtualizer.getVirtualItems()[0]?.start ?? 0}px` }} />
                    {rowVirtualizer.getVirtualItems().map(virtualRow => {
                      const row = rows[virtualRow.index];
                      return (
                        <tr 
                          key={row.id} 
                          className="hover:bg-accent/50 transition-colors"
                        >
                          {row.getVisibleCells().map(cell => (
                            <td 
                              key={cell.id} 
                              className="px-6 py-3 whitespace-nowrap"
                            >
                              {flexRender(cell.column.columnDef.cell, cell.getContext())}
                            </td>
                          ))}
                        </tr>
                      );
                    })}
                    <tr style={{ height: `${rowVirtualizer.getTotalSize() - (rowVirtualizer.getVirtualItems()[rowVirtualizer.getVirtualItems().length - 1]?.end ?? 0)}px` }} />
                  </>
                )}
              </tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
