"use client";

import React from 'react';
import { useArticleDetail } from '@/features/news/api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { AISummaryBox } from '@/features/news/components/AISummaryBox';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Clock, Share2, BookmarkPlus } from 'lucide-react';
import Link from 'next/link';
import { motion, useScroll, useSpring } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { cn } from '@/lib/utils';
import { sanitizeHtml } from '@/lib/sanitize';
import { use } from 'react';

export default function ArticleReaderPage({ params }: { params: Promise<{ id: string }> }) {
  const p = use(params);
  const { data, isLoading, isError, refetch } = useArticleDetail(p.id);
  const { scrollYProgress } = useScroll();
  const scaleX = useSpring(scrollYProgress, { stiffness: 100, damping: 30, restDelta: 0.001 });

  if (isError) {
    return (
      <div className="pt-12">
        <WidgetError title="Article Error" message="Failed to load article." onRetry={refetch} />
      </div>
    );
  }

  if (isLoading || !data) {
    return (
      <div className="max-w-4xl mx-auto pt-8 pb-16 px-4 space-y-8">
        <Skeleton className="h-10 w-32" />
        <Skeleton className="h-12 w-3/4" />
        <Skeleton className="h-[400px] w-full rounded-2xl" />
        <div className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </div>
    );
  }

  return (
    <div className="relative">
      {/* Reading Progress Bar */}
      <motion.div
        className="fixed top-0 left-0 right-0 h-1 bg-indigo-500 origin-left z-50"
        style={{ scaleX }}
      />

      <div className="max-w-4xl mx-auto pt-8 pb-16 px-4">
        {/* Navigation */}
        <div className="flex items-center justify-between mb-8 sticky top-[60px] z-30 bg-background/80 backdrop-blur-xl py-2 rounded-xl -mx-4 px-4">
          <Button variant="ghost" asChild className="hover:bg-accent/50 text-muted-foreground">
            <Link href="/news">
              <ArrowLeft className="h-5 w-5 mr-2" />
              Back to News
            </Link>
          </Button>
          <div className="flex gap-2">
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <BookmarkPlus className="h-5 w-5" />
            </Button>
            <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
              <Share2 className="h-5 w-5" />
            </Button>
          </div>
        </div>

        {/* Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-6 mb-8"
        >
          <div className="flex flex-wrap gap-2 items-center">
            {data.isBreaking && (
              <span className="bg-destructive text-destructive-foreground text-[10px] font-bold px-2 py-0.5 rounded uppercase tracking-wider animate-pulse">
                Breaking
              </span>
            )}
            <span className={cn(
              "text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded",
              data.sentiment === 'positive' ? 'bg-emerald-500/10 text-emerald-500' :
              data.sentiment === 'negative' ? 'bg-destructive/10 text-destructive' :
              'bg-muted text-muted-foreground'
            )}>
              {data.sentiment} Sentiment
            </span>
            {data.tickers.map(ticker => (
              <Link key={ticker} href={`/market/${ticker.toLowerCase()}`} className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded bg-indigo-500/10 text-indigo-400 hover:bg-indigo-500/20 transition-colors">
                ${ticker}
              </Link>
            ))}
          </div>

          <h1 className="text-3xl md:text-5xl font-bold tracking-tight leading-tight">
            {data.headline}
          </h1>

          <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground border-y border-border/50 py-4">
            <div className="font-medium text-foreground">{data.source}</div>
            {data.author && (
              <>
                <span className="opacity-30">•</span>
                <div>By {data.author}</div>
              </>
            )}
            <span className="opacity-30">•</span>
            <div className="flex items-center">
              <Clock className="h-4 w-4 mr-1" />
              {formatDistanceToNow(new Date(data.publishedAt), { addSuffix: true })}
            </div>
            <span className="opacity-30">•</span>
            <div>{data.readingTimeMin} min read</div>
          </div>
        </motion.div>

        {/* Hero Image */}
        {data.imageUrl && (
          <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1 }}
            className="w-full h-[300px] md:h-[450px] relative rounded-2xl overflow-hidden mb-12 shadow-2xl border border-white/5"
          >
            <img src={data.imageUrl} alt={data.headline} className="w-full h-full object-cover" />
            <div className="absolute inset-0 bg-gradient-to-t from-background/80 via-transparent to-transparent" />
          </motion.div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
          {/* Main Content */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2 prose prose-invert prose-indigo max-w-none"
            dangerouslySetInnerHTML={{ __html: sanitizeHtml(data.content) }}
          />

          {/* Sidebar */}
          <div className="space-y-8">
            <AISummaryBox summary={data.aiSummary} />
          </div>
        </div>
      </div>
    </div>
  );
}
