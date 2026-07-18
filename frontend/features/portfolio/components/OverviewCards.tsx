"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { usePortfolioSummary } from '../api/queries';
import { motion } from 'framer-motion';
import { ArrowDownRight, ArrowUpRight, DollarSign, Activity, PieChart, Shield } from 'lucide-react';
import { cn } from '@/lib/utils';
import { WidgetError } from '@/features/dashboard/components/WidgetError';

export function OverviewCards() {
  const { data, isLoading, isError, refetch } = usePortfolioSummary();

  if (isError) {
    return (
      <div className="col-span-full">
        <WidgetError title="Portfolio Summary Error" message="Unable to load portfolio overview." onRetry={refetch} />
      </div>
    );
  }

  if (isLoading || !data) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="bg-card/50 backdrop-blur-md border-card-border">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-[100px]" />
              <Skeleton className="h-4 w-4 rounded-full" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-[120px] mb-2" />
              <Skeleton className="h-3 w-[80px]" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Portfolio Value',
      value: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(data.totalValue),
      subtext: `${data.dailyChangePercent >= 0 ? '+' : ''}${data.dailyChangePercent.toFixed(2)}% Today`,
      icon: <DollarSign className="h-4 w-4 text-muted-foreground" />,
      trend: data.dailyChangePercent >= 0 ? 'up' : 'down'
    },
    {
      title: 'Total Return',
      value: new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(data.totalReturn),
      subtext: `${data.totalReturnPercent >= 0 ? '+' : ''}${data.totalReturnPercent.toFixed(2)}% All Time`,
      icon: <Activity className="h-4 w-4 text-muted-foreground" />,
      trend: data.totalReturnPercent >= 0 ? 'up' : 'down'
    },
    {
      title: 'Diversification Score',
      value: data.diversificationScore.toString(),
      subtext: 'Out of 100',
      icon: <PieChart className="h-4 w-4 text-muted-foreground" />,
      trend: 'neutral'
    },
    {
      title: 'Portfolio Beta',
      value: data.beta.toFixed(2),
      subtext: 'vs S&P 500',
      icon: <Shield className="h-4 w-4 text-muted-foreground" />,
      trend: 'neutral'
    }
  ];

  const container = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const item: any = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0, transition: { type: "spring", stiffness: 300, damping: 24 } }
  };

  return (
    <motion.div 
      className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      variants={container}
      initial="hidden"
      animate="show"
    >
      {cards.map((card, i) => (
        <motion.div key={i} variants={item}>
          <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg hover:bg-card/80 transition-colors">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                {card.title}
              </CardTitle>
              {card.icon}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold text-foreground">{card.value}</div>
              <p className={cn(
                "text-xs mt-1 flex items-center",
                card.trend === 'up' ? "text-emerald-500" : 
                card.trend === 'down' ? "text-destructive" : "text-muted-foreground"
              )}>
                {card.trend === 'up' && <ArrowUpRight className="mr-1 h-3 w-3" />}
                {card.trend === 'down' && <ArrowDownRight className="mr-1 h-3 w-3" />}
                {card.subtext}
              </p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  );
}
