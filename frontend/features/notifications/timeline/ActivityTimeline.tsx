"use client";

import React from 'react';
import { useActivityTimeline } from '../api/queries';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Activity, Mail, CheckCircle2, XCircle, Clock } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export function ActivityTimeline() {
  const { data, isLoading, isError, refetch } = useActivityTimeline();

  if (isError) return <WidgetError title="Timeline Error" message="Failed to load activity." onRetry={refetch} />;

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-4 border-b border-white/5">
        <CardTitle className="text-lg font-semibold flex items-center">
          <Activity className="h-5 w-5 mr-2 text-indigo-400" />
          Delivery & Execution History
        </CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-6 overflow-y-auto custom-scrollbar">
        {isLoading || !data ? (
          <div className="space-y-6">
            {Array.from({ length: 4 }).map((_, i) => (
              <div key={i} className="flex gap-4">
                <Skeleton className="h-4 w-4 rounded-full shrink-0" />
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-1/3" />
                  <Skeleton className="h-3 w-2/3" />
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="relative border-l border-border/50 ml-3 space-y-8">
            {data.map((event, index) => (
              <motion.div 
                key={event.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="relative pl-6"
              >
                <div className={cn(
                  "absolute -left-[9px] top-1 rounded-full p-0.5 bg-background border",
                  event.status === 'success' ? 'text-emerald-500 border-emerald-500/50' :
                  event.status === 'failed' ? 'text-destructive border-destructive/50' :
                  'text-amber-500 border-amber-500/50'
                )}>
                  {event.status === 'success' ? <CheckCircle2 className="h-3 w-3 bg-background rounded-full" /> : 
                   event.status === 'failed' ? <XCircle className="h-3 w-3 bg-background rounded-full" /> :
                   <Clock className="h-3 w-3 bg-background rounded-full" />}
                </div>
                
                <div className="flex flex-col gap-1">
                  <div className="flex items-center gap-2">
                    <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                      {event.type.replace('_', ' ')}
                    </span>
                    <span className="text-xs text-muted-foreground font-medium">
                      {formatDistanceToNow(new Date(event.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                  <p className="text-sm text-foreground leading-relaxed mt-1">
                    {event.description}
                  </p>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
