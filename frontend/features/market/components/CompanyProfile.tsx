"use client";

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { useCompanyProfile } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { motion } from 'framer-motion';
import { Building2, Globe, Users, Briefcase } from 'lucide-react';

export function CompanyProfile({ ticker }: { ticker: string }) {
  const { data, isLoading, isError, refetch } = useCompanyProfile(ticker);

  if (isError) {
    return <WidgetError title="Profile Error" message="Failed to load company profile." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
        <CardContent className="p-6 space-y-4">
          <div className="flex items-center gap-4">
            <Skeleton className="h-16 w-16 rounded-full" />
            <div className="space-y-2">
              <Skeleton className="h-6 w-48" />
              <Skeleton className="h-4 w-24" />
            </div>
          </div>
          <Skeleton className="h-20 w-full" />
        </CardContent>
      </Card>
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}>
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg overflow-hidden relative">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl pointer-events-none -translate-y-1/2 translate-x-1/3" />
        <CardContent className="p-6 md:p-8 relative z-10">
          <div className="flex flex-col md:flex-row md:items-start gap-6">
            {data.logo ? (
              <img src={data.logo} alt={data.companyName} className="h-16 w-16 md:h-20 md:w-20 rounded-2xl bg-white/5 object-contain p-2 shrink-0 border border-white/10" />
            ) : (
              <div className="h-16 w-16 md:h-20 md:w-20 rounded-2xl bg-indigo-500/20 flex items-center justify-center shrink-0 border border-indigo-500/30 text-2xl font-bold text-indigo-200">
                {data.ticker.charAt(0)}
              </div>
            )}
            
            <div className="flex-1 space-y-4">
              <div>
                <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
                  <h2 className="text-2xl md:text-3xl font-bold tracking-tight">{data.companyName}</h2>
                  <span className="text-sm font-medium px-2 py-0.5 rounded bg-muted/50 text-muted-foreground border border-white/5">
                    {data.exchange}:{data.ticker}
                  </span>
                </div>
                <p className="text-muted-foreground mt-2 max-w-4xl leading-relaxed text-sm">
                  {data.description}
                </p>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-border/50">
                <div>
                  <div className="flex items-center text-xs text-muted-foreground mb-1">
                    <Briefcase className="h-3 w-3 mr-1" /> Sector
                  </div>
                  <div className="text-sm font-medium">{data.sector}</div>
                </div>
                <div>
                  <div className="flex items-center text-xs text-muted-foreground mb-1">
                    <Building2 className="h-3 w-3 mr-1" /> Industry
                  </div>
                  <div className="text-sm font-medium truncate" title={data.industry}>{data.industry}</div>
                </div>
                <div>
                  <div className="flex items-center text-xs text-muted-foreground mb-1">
                    <Users className="h-3 w-3 mr-1" /> Employees
                  </div>
                  <div className="text-sm font-medium">{new Intl.NumberFormat('en-US').format(data.employees)}</div>
                </div>
                <div>
                  <div className="flex items-center text-xs text-muted-foreground mb-1">
                    <Globe className="h-3 w-3 mr-1" /> Website
                  </div>
                  <a href={data.website} target="_blank" rel="noreferrer" className="text-sm font-medium text-indigo-400 hover:underline truncate block">
                    {data.website.replace(/^https?:\/\/(www\.)?/, '')}
                  </a>
                </div>
              </div>
            </div>
            
            <div className="md:w-48 shrink-0 flex flex-col gap-3 md:text-right pt-4 md:pt-0 border-t md:border-t-0 md:border-l border-border/50 md:pl-6">
              <div>
                <div className="text-xs text-muted-foreground mb-1">Market Cap</div>
                <div className="text-lg font-bold">
                  ${(data.marketCap / 1e9).toFixed(2)}B
                </div>
              </div>
              <div>
                <div className="text-xs text-muted-foreground mb-1">Enterprise Value</div>
                <div className="text-lg font-bold">
                  ${(data.enterpriseValue / 1e9).toFixed(2)}B
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
