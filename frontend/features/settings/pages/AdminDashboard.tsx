"use client";

import React from 'react';
import { useSystemMetrics } from '../api/queries';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Server, Database, Activity, Layers, PlayCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export function AdminDashboard() {
  const { data, isLoading, isError, refetch } = useSystemMetrics();

  if (isError) return <WidgetError title="Admin Error" message="Failed to load system metrics." onRetry={refetch} />;

  const getStatusColor = (status?: string) => {
    if (status === 'ONLINE') return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30';
    if (status === 'DEGRADED') return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
    return 'bg-destructive/20 text-destructive border-destructive/30';
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
      <div>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight text-destructive flex items-center gap-2">
          <Server className="h-6 w-6" />
          Admin Dashboard
        </h2>
        <p className="text-muted-foreground mt-1">Read-only system health and infrastructure metrics.</p>
      </div>

      {isLoading || !data ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-32 w-full rounded-xl" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-medium flex items-center gap-2">
                <Database className="h-4 w-4" /> Postgres DB
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-bold border", getStatusColor(data.database))}>
                <span className={cn("w-2 h-2 rounded-full", data.database === 'ONLINE' ? 'bg-emerald-400' : 'bg-destructive')} />
                {data.database}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-medium flex items-center gap-2">
                <Layers className="h-4 w-4" /> Redis Cache
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={cn("inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs font-bold border", getStatusColor(data.redis))}>
                <span className={cn("w-2 h-2 rounded-full", data.redis === 'ONLINE' ? 'bg-emerald-400' : 'bg-destructive')} />
                {data.redis}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-medium flex items-center gap-2">
                <Activity className="h-4 w-4" /> Queue Depth
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.queueDepth.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">Pending jobs</p>
            </CardContent>
          </Card>

          <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
            <CardHeader className="pb-2">
              <CardTitle className="text-sm text-muted-foreground font-medium flex items-center gap-2">
                <PlayCircle className="h-4 w-4" /> Workers
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{data.activeWorkers}</div>
              <p className="text-xs text-muted-foreground">Active nodes</p>
            </CardContent>
          </Card>
        </div>
      )}

      {data && (
        <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg mt-8">
           <CardHeader>
             <CardTitle>System Information</CardTitle>
           </CardHeader>
           <CardContent className="grid grid-cols-2 gap-4 text-sm">
             <div>
               <div className="text-muted-foreground">Version</div>
               <div className="font-mono">{data.version}</div>
             </div>
             <div>
               <div className="text-muted-foreground">Environment</div>
               <div className="font-mono uppercase text-indigo-400">{data.environment}</div>
             </div>
           </CardContent>
        </Card>
      )}
    </motion.div>
  );
}
