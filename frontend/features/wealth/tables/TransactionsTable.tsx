"use client";

import React, { useState, useEffect, useRef } from 'react';
import { useTransactions } from '../api/queries';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Search, ShoppingBag, ArrowUpRight, ArrowDownRight, RefreshCcw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion, AnimatePresence } from 'framer-motion';

export function TransactionsTable() {
  const [search, setSearch] = useState('');
  const { data, isLoading, isError, refetch, fetchNextPage, hasNextPage, isFetchingNextPage } = useTransactions({
    search: search.length > 2 ? search : undefined
  });

  const observerTarget = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );
    if (observerTarget.current) {
      observer.observe(observerTarget.current);
    }
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  if (isError) {
    return <WidgetError title="Transactions Error" message="Failed to load ledger." onRetry={refetch} />;
  }

  const transactions = data?.pages.flatMap(page => page.transactions) || [];

  const getIcon = (type: string) => {
    switch(type) {
      case 'income': return <ArrowUpRight className="h-4 w-4 text-emerald-500" />;
      case 'expense': return <ArrowDownRight className="h-4 w-4 text-foreground" />;
      case 'transfer': return <RefreshCcw className="h-4 w-4 text-indigo-400" />;
      default: return <ShoppingBag className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
      <div className="p-4 border-b border-white/5 flex flex-col sm:flex-row justify-between gap-4 sticky top-[60px] z-30 bg-background/80 backdrop-blur-xl">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search transactions..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-9 bg-background/50 border-white/10"
          />
        </div>
      </div>

      <CardContent className="p-0">
        <div className="divide-y divide-border/50">
          <AnimatePresence>
            {transactions.map(tx => (
              <motion.div 
                key={tx.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center justify-between p-4 hover:bg-white/5 transition-colors group"
              >
                <div className="flex items-center gap-4">
                  <div className="h-10 w-10 rounded-full bg-muted/50 flex items-center justify-center shrink-0 border border-white/5 group-hover:scale-110 transition-transform">
                    {getIcon(tx.type)}
                  </div>
                  <div>
                    <div className="font-semibold text-sm group-hover:text-indigo-400 transition-colors">{tx.description}</div>
                    <div className="flex gap-2 items-center mt-1">
                      <span className="text-xs text-muted-foreground">{new Date(tx.date).toLocaleDateString()}</span>
                      <span className="text-[10px] uppercase tracking-wider bg-muted px-1.5 py-0.5 rounded text-muted-foreground">{tx.category}</span>
                      {tx.pending && (
                        <span className="text-[10px] uppercase tracking-wider bg-amber-500/10 text-amber-500 px-1.5 py-0.5 rounded">Pending</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className={cn(
                  "font-mono font-medium text-right",
                  tx.type === 'income' ? 'text-emerald-500' : 'text-foreground'
                )}>
                  {tx.type === 'income' ? '+' : tx.type === 'expense' ? '-' : ''}
                  ${Math.abs(tx.amount).toFixed(2)}
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {(isLoading || isFetchingNextPage) && (
            <div className="p-4 space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex justify-between items-center">
                  <div className="flex items-center gap-4">
                    <Skeleton className="h-10 w-10 rounded-full shrink-0" />
                    <div className="space-y-2">
                      <Skeleton className="h-4 w-40" />
                      <Skeleton className="h-3 w-24" />
                    </div>
                  </div>
                  <Skeleton className="h-5 w-20" />
                </div>
              ))}
            </div>
          )}

          {/* Infinite Scroll target */}
          <div ref={observerTarget} className="h-10 w-full" />
        </div>
      </CardContent>
    </Card>
  );
}
