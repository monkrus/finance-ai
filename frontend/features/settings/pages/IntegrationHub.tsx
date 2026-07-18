"use client";

import React from 'react';
import { useIntegrations } from '../api/queries';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Network, Building2, Landmark, RefreshCw, Plus, MoreHorizontal } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export function IntegrationHub() {
  const { data, isLoading, isError, refetch } = useIntegrations();

  if (isError) return <WidgetError title="Integrations Error" message="Failed to load connections." onRetry={refetch} />;

  const getIcon = (type: string) => {
    switch(type) {
      case 'bank': return <Building2 className="h-5 w-5 text-indigo-400" />;
      case 'broker': return <Landmark className="h-5 w-5 text-emerald-400" />;
      default: return <Network className="h-5 w-5 text-muted-foreground" />;
    }
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight">Integrations Hub</h2>
          <p className="text-muted-foreground mt-1">Manage connected banks, brokers, exchanges, and CSV imports.</p>
        </div>
        <Button className="bg-indigo-600 hover:bg-indigo-700">
          <Plus className="h-4 w-4 mr-2" /> Connect Institution
        </Button>
      </div>

      {isLoading || !data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Skeleton className="h-[200px] w-full rounded-2xl" />
          <Skeleton className="h-[200px] w-full rounded-2xl" />
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <AnimatePresence>
            {data.map((integration) => (
              <motion.div key={integration.id} layout initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }}>
                <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg h-full flex flex-col group hover:bg-white/5 transition-colors">
                  <CardHeader className="flex flex-row items-start justify-between pb-2">
                    <div className="flex items-center gap-4">
                      <div className="h-12 w-12 rounded-xl bg-background/50 border border-white/10 flex items-center justify-center shrink-0">
                        {getIcon(integration.type)}
                      </div>
                      <div>
                        <CardTitle className="text-lg">{integration.provider}</CardTitle>
                        <CardDescription className="uppercase tracking-wider text-[10px] font-bold mt-1">
                          {integration.type} Connection
                        </CardDescription>
                      </div>
                    </div>
                    <Button variant="ghost" size="icon" className="h-8 w-8 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col justify-end pt-4">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Status</span>
                        <span className={cn(
                          "flex items-center gap-1.5 font-medium px-2 py-0.5 rounded-full text-xs",
                          integration.status === 'connected' ? 'bg-emerald-500/10 text-emerald-400' : 
                          integration.status === 'error' ? 'bg-destructive/10 text-destructive' : 'bg-muted text-muted-foreground'
                        )}>
                          <span className={cn("w-1.5 h-1.5 rounded-full", integration.status === 'connected' ? 'bg-emerald-400' : integration.status === 'error' ? 'bg-destructive' : 'bg-muted-foreground')} />
                          {integration.status.charAt(0).toUpperCase() + integration.status.slice(1)}
                        </span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span className="text-muted-foreground">Last Sync</span>
                        <span>{integration.lastSync ? formatDistanceToNow(new Date(integration.lastSync), { addSuffix: true }) : 'Never'}</span>
                      </div>
                      <div className="flex gap-2 pt-2">
                        <Button variant="outline" size="sm" className="w-full bg-background/50 border-white/10">
                          <RefreshCw className="h-3 w-3 mr-2" /> Sync Now
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </motion.div>
  );
}
