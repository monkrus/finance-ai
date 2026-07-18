"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useEventTimeline } from '../api/queries';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { CircleDot } from 'lucide-react';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';

export function EventTimeline({ ticker }: { ticker?: string }) {
  const { data, isLoading, isError, refetch } = useEventTimeline(ticker);

  if (isError) {
    return <WidgetError title="Timeline Error" message="Failed to load events." onRetry={refetch} />;
  }

  if (isLoading || !data) {
    return (
      <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px]">
        <CardContent className="p-6 space-y-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <div key={i} className="flex gap-4">
              <Skeleton className="h-4 w-4 rounded-full shrink-0" />
              <div className="space-y-2 flex-1">
                <Skeleton className="h-4 w-1/3" />
                <Skeleton className="h-3 w-2/3" />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[400px] flex flex-col">
      <CardHeader className="pb-4 border-b border-white/5">
        <CardTitle className="text-lg font-semibold">Event Timeline</CardTitle>
      </CardHeader>
      <CardContent className="flex-1 p-6 overflow-y-auto custom-scrollbar">
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
                "absolute -left-[9px] top-1 rounded-full p-0.5 bg-background",
                event.sentiment === 'positive' ? 'text-emerald-500' :
                event.sentiment === 'negative' ? 'text-destructive' :
                'text-indigo-500'
              )}>
                <CircleDot className="h-4 w-4 bg-background rounded-full" />
              </div>
              
              <div className="flex flex-col gap-1">
                <div className="flex items-center gap-2">
                  <span className="text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-muted text-muted-foreground">
                    {event.type}
                  </span>
                  <span className="text-xs text-muted-foreground font-medium">
                    {new Date(event.date).toLocaleDateString()}
                  </span>
                </div>
                <h4 className="text-sm font-semibold">{event.title}</h4>
                <p className="text-xs text-muted-foreground leading-relaxed">
                  {event.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
