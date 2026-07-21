"use client";

import React, { useEffect, useRef, useState } from 'react';
import { useNewsFeed } from '../api/queries';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import Link from 'next/link';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { Clock, BookmarkPlus } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Input } from '@/components/ui/input';

const categories = ['All', 'Market', 'Company', 'Economy', 'Crypto', 'Earnings', 'M&A'];

export function NewsFeed({ isPortfolio = false }: { isPortfolio?: boolean }) {
  const [activeCategory, setActiveCategory] = useState('All');
  const [search, setSearch] = useState('');
  
  const { 
    data, 
    isLoading, 
    isError, 
    refetch, 
    fetchNextPage, 
    hasNextPage, 
    isFetchingNextPage 
  } = useNewsFeed({ 
    category: activeCategory === 'All' ? undefined : activeCategory, 
    search: search.length > 2 ? search : undefined,
    isPortfolio 
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
    return <WidgetError title="Feed Error" message="Failed to load news feed." onRetry={refetch} />;
  }

  const articles = data?.pages.flatMap(page => page.articles) || [];

  return (
    <div className="flex flex-col gap-6">
      <div className="flex flex-col sm:flex-row gap-4 justify-between sticky top-[60px] z-30 bg-background/80 backdrop-blur-xl p-2 rounded-xl border border-white/5 shadow-sm">
        <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0 scrollbar-hide">
          {categories.map(cat => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={cn(
                "px-4 py-1.5 rounded-full text-sm font-medium whitespace-nowrap transition-colors",
                activeCategory === cat ? "bg-indigo-500 text-white shadow-md shadow-indigo-500/20" : "bg-muted/50 text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              {cat}
            </button>
          ))}
        </div>
        <div className="w-full sm:w-64 shrink-0">
          <Input 
            placeholder="Search news..." 
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="bg-card/50 border-white/10 focus-visible:ring-indigo-500"
          />
        </div>
      </div>

      <div className="flex flex-col gap-4">
        <AnimatePresence mode="popLayout">
          {articles.map((article, index) => (
            <motion.div
              key={article.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.3, delay: Math.min(index * 0.05, 0.5) }}
            >
              <Link href={`/news/article/${article.id}`} className="block group">
                <Card className="bg-card/40 backdrop-blur-md border-white/5 hover:bg-card/60 transition-colors shadow-sm overflow-hidden h-full">
                  <CardContent className="p-0 flex flex-col sm:flex-row h-full">
                    {article.imageUrl && (
                      <div className="w-full sm:w-48 h-48 sm:h-auto shrink-0 relative overflow-hidden bg-muted">
                        <img 
                          src={article.imageUrl} 
                          alt="" 
                          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-700" 
                        />
                        {article.isBreaking && (
                          <div className="absolute top-2 left-2 bg-destructive text-destructive-foreground text-[10px] font-bold px-2 py-0.5 rounded shadow uppercase tracking-wider animate-pulse">
                            Breaking
                          </div>
                        )}
                      </div>
                    )}
                    <div className="p-5 flex flex-col flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <div className="flex gap-2">
                          <span className={cn(
                            "text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded",
                            article.sentiment === 'positive' ? 'bg-emerald-500/10 text-emerald-500' :
                            article.sentiment === 'negative' ? 'bg-destructive/10 text-destructive' :
                            'bg-muted text-muted-foreground'
                          )}>
                            {article.sentiment}
                          </span>
                          {article.tickers.slice(0,3).map(ticker => (
                            <span key={ticker} className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-indigo-500/10 text-indigo-400">
                              {ticker}
                            </span>
                          ))}
                        </div>
                        <span className="text-xs text-muted-foreground flex items-center shrink-0">
                          <Clock className="h-3 w-3 mr-1" />
                          {formatDistanceToNow(new Date(article.publishedAt), { addSuffix: true })}
                        </span>
                      </div>
                      
                      <h3 className="text-lg font-bold mb-2 group-hover:text-indigo-400 transition-colors line-clamp-2">
                        {article.headline}
                      </h3>
                      
                      <p className="text-sm text-muted-foreground line-clamp-2 mb-4 flex-1">
                        {article.summary}
                      </p>

                      <div className="flex justify-between items-center text-xs pt-4 border-t border-border/50">
                        <span className="font-medium text-muted-foreground">{article.source}</span>
                        <div className="flex items-center gap-3">
                          <span className="text-muted-foreground opacity-50">{article.readingTimeMin} min read</span>
                          <button className="text-muted-foreground hover:text-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                            <BookmarkPlus className="h-4 w-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {(isLoading || isFetchingNextPage) && (
        <div className="flex flex-col gap-4">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="bg-card/40 backdrop-blur-md border-white/5 h-40">
              <CardContent className="p-4 flex gap-4 h-full">
                <Skeleton className="w-48 h-full rounded-md" />
                <div className="flex-1 space-y-4">
                  <Skeleton className="h-6 w-3/4" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Infinite Scroll Observer Target */}
      <div ref={observerTarget} className="h-10 w-full" />
    </div>
  );
}
