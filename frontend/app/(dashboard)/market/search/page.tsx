"use client";

import React, { useState } from 'react';
import { useStockSearch } from '@/features/market/api/queries';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Search, TrendingUp, Star, Clock } from 'lucide-react';
import { useDebounce } from '@/hooks/useDebounce'; // Assumes this hook exists
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function StockSearchPage() {
  const [query, setQuery] = useState('');
  const debouncedQuery = useDebounce(query, 300);
  const { data, isLoading } = useStockSearch(debouncedQuery);

  return (
    <div className="max-w-3xl mx-auto pt-12 pb-8 px-4 flex flex-col gap-8">
      <div className="text-center space-y-4">
        <h1 className="text-3xl md:text-4xl font-bold tracking-tight">Search Markets</h1>
        <p className="text-muted-foreground">Find stocks, ETFs, and indices instantly.</p>
      </div>

      <div className="relative group">
        <div className="absolute inset-0 bg-indigo-500/20 rounded-xl blur-xl group-focus-within:bg-indigo-500/30 transition-colors" />
        <div className="relative">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-muted-foreground" />
          <Input 
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search by ticker or company name..."
            className="pl-12 h-14 text-lg bg-card/80 backdrop-blur-xl border-white/20 rounded-xl shadow-2xl focus-visible:ring-indigo-500"
            autoFocus
          />
        </div>
      </div>

      {debouncedQuery.length > 1 ? (
        <Card className="bg-card/60 backdrop-blur-xl border-white/10 overflow-hidden">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-6 text-center text-muted-foreground animate-pulse">Searching...</div>
            ) : data && data.length > 0 ? (
              <motion.ul initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="divide-y divide-border/50">
                {data.map((item) => (
                  <li key={item.symbol}>
                    <Link 
                      href={`/market/${item.symbol.toLowerCase()}`}
                      className="flex items-center justify-between p-4 hover:bg-accent/50 transition-colors group"
                    >
                      <div>
                        <div className="font-bold text-lg group-hover:text-indigo-400 transition-colors">{item.symbol}</div>
                        <div className="text-sm text-muted-foreground">{item.name}</div>
                      </div>
                      <div className="text-right text-xs text-muted-foreground">
                        <div className="px-2 py-1 rounded bg-muted/50">{item.exchange}</div>
                      </div>
                    </Link>
                  </li>
                ))}
              </motion.ul>
            ) : (
              <div className="p-6 text-center text-muted-foreground">No results found for "{query}".</div>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center">
              <TrendingUp className="mr-2 h-4 w-4" /> Trending
            </h3>
            <div className="space-y-2">
              {['NVDA', 'AAPL', 'MSFT', 'TSLA'].map(ticker => (
                <Link key={ticker} href={`/market/${ticker.toLowerCase()}`} className="block p-3 rounded-lg bg-card/40 border border-white/5 hover:bg-card/80 transition-colors">
                  <span className="font-medium">{ticker}</span>
                </Link>
              ))}
            </div>
          </div>
          <div>
            <h3 className="text-sm font-semibold text-muted-foreground mb-3 flex items-center">
              <Star className="mr-2 h-4 w-4" /> Favorites
            </h3>
            <div className="space-y-2">
              {['SPY', 'QQQ'].map(ticker => (
                <Link key={ticker} href={`/market/${ticker.toLowerCase()}`} className="block p-3 rounded-lg bg-card/40 border border-white/5 hover:bg-card/80 transition-colors">
                  <span className="font-medium">{ticker}</span>
                </Link>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
