"use client";

import React, { useState } from 'react';
import {
  flexRender,
  getCoreRowModel,
  useReactTable,
  getSortedRowModel,
  SortingState,
  getFilteredRowModel,
} from '@tanstack/react-table';
import { useAccounts } from '../api/queries';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { formatDistanceToNow } from 'date-fns';
import { ArrowUpDown, Search, Building2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Account } from '../types';
import { motion } from 'framer-motion';

export function AccountsTable() {
  const { data, isLoading, isError, refetch } = useAccounts();
  const [sorting, setSorting] = useState<SortingState>([]);
  const [globalFilter, setGlobalFilter] = useState('');

  const columns = [
    {
      accessorKey: 'name',
      header: ({ column }: any) => (
        <div className="flex items-center cursor-pointer hover:text-white" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Account <ArrowUpDown className="ml-2 h-4 w-4" />
        </div>
      ),
      cell: ({ row }: any) => {
        const account = row.original as Account;
        return (
          <div className="flex items-center gap-3">
            <div className="h-10 w-10 rounded-full bg-muted/50 flex items-center justify-center shrink-0 border border-white/5">
              <Building2 className="h-5 w-5 text-muted-foreground" />
            </div>
            <div>
              <div className="font-semibold">{account.name}</div>
              <div className="text-xs text-muted-foreground">{account.institution}</div>
            </div>
          </div>
        );
      },
    },
    {
      accessorKey: 'type',
      header: 'Type',
      cell: ({ row }: any) => (
        <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded bg-muted/50 text-muted-foreground">
          {row.getValue('type')}
        </span>
      ),
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ row }: any) => {
        const status = row.getValue('status') as string;
        return (
          <div className="flex items-center gap-2 text-sm">
            {status === 'connected' ? (
              <><CheckCircle2 className="h-4 w-4 text-emerald-500" /> <span className="text-emerald-500">Connected</span></>
            ) : status === 'error' ? (
              <><AlertCircle className="h-4 w-4 text-destructive" /> <span className="text-destructive">Needs Attention</span></>
            ) : (
              <><div className="h-2 w-2 rounded-full bg-muted-foreground ml-1" /> <span className="text-muted-foreground">Disconnected</span></>
            )}
          </div>
        );
      },
    },
    {
      accessorKey: 'lastSync',
      header: 'Last Sync',
      cell: ({ row }: any) => (
        <span className="text-sm text-muted-foreground">
          {formatDistanceToNow(new Date(row.getValue('lastSync')), { addSuffix: true })}
        </span>
      ),
    },
    {
      accessorKey: 'balance',
      header: ({ column }: any) => (
        <div className="flex items-center justify-end cursor-pointer hover:text-white" onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}>
          Balance <ArrowUpDown className="ml-2 h-4 w-4" />
        </div>
      ),
      cell: ({ row }: any) => {
        const amount = parseFloat(row.getValue('balance'));
        const formatted = new Intl.NumberFormat('en-US', {
          style: 'currency',
          currency: row.original.currency,
        }).format(amount);
        
        return <div className="text-right font-mono font-medium text-lg">{formatted}</div>;
      },
    },
  ];

  const table = useReactTable({
    data: data || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: { sorting, globalFilter },
    onGlobalFilterChange: setGlobalFilter,
  });

  if (isError) {
    return <WidgetError title="Accounts Error" message="Failed to load connected accounts." onRetry={refetch} />;
  }

  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
      <div className="p-4 border-b border-white/5 flex flex-col sm:flex-row justify-between gap-4">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search accounts or institutions..." 
            value={globalFilter ?? ''}
            onChange={e => setGlobalFilter(e.target.value)}
            className="pl-9 bg-background/50 border-white/10"
          />
        </div>
      </div>
      <CardContent className="p-0">
        {isLoading ? (
          <div className="p-4 space-y-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full" />
            ))}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                {table.getHeaderGroups().map(headerGroup => (
                  <tr key={headerGroup.id} className="border-b border-border/50 bg-muted/20">
                    {headerGroup.headers.map(header => (
                      <th key={header.id} className="p-4 text-sm font-medium text-muted-foreground whitespace-nowrap">
                        {header.isPlaceholder ? null : flexRender(header.column.columnDef.header, header.getContext())}
                      </th>
                    ))}
                  </tr>
                ))}
              </thead>
              <motion.tbody 
                initial={{ opacity: 0 }} 
                animate={{ opacity: 1 }} 
                className="divide-y divide-border/50"
              >
                {table.getRowModel().rows.length ? (
                  table.getRowModel().rows.map(row => (
                    <tr key={row.id} className="hover:bg-white/5 transition-colors group">
                      {row.getVisibleCells().map(cell => (
                        <td key={cell.id} className="p-4 whitespace-nowrap">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                        </td>
                      ))}
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={columns.length} className="h-32 text-center text-muted-foreground">
                      No accounts found.
                    </td>
                  </tr>
                )}
              </motion.tbody>
            </table>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
