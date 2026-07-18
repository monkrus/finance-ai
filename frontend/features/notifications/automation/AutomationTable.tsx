"use client";

import React, { useState } from 'react';
import { useAutomations, useToggleAutomation } from '../api/queries';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Search, Play, Pause, Settings2, MoreHorizontal, Activity } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/button';
import { motion, AnimatePresence } from 'framer-motion';

export function AutomationTable() {
  const { data, isLoading, isError, refetch } = useAutomations();
  const { mutate: toggle } = useToggleAutomation();
  const [search, setSearch] = useState('');

  if (isError) {
    return <WidgetError title="Automation Error" message="Failed to load engine rules." onRetry={refetch} />;
  }

  const filtered = data?.filter(r => r.name.toLowerCase().includes(search.toLowerCase())) || [];

  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
      <div className="p-4 border-b border-white/5 flex flex-col sm:flex-row justify-between gap-4 sticky top-[60px] z-30 bg-background/80 backdrop-blur-xl">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input 
            placeholder="Search rules..." 
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="pl-9 bg-background/50 border-white/10"
          />
        </div>
      </div>

      <CardContent className="p-0">
        <div className="divide-y divide-border/50">
          <AnimatePresence>
            {filtered.map(rule => (
              <motion.div 
                key={rule.id}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex flex-col sm:flex-row sm:items-center justify-between p-4 hover:bg-white/5 transition-colors group gap-4"
              >
                <div className="flex items-center gap-4">
                  <div className={cn(
                    "h-10 w-10 rounded-full flex items-center justify-center shrink-0 border border-white/5 transition-all",
                    rule.status === 'active' ? "bg-indigo-500/10 text-indigo-400 group-hover:bg-indigo-500/20" : "bg-muted/50 text-muted-foreground"
                  )}>
                    <Activity className="h-4 w-4" />
                  </div>
                  <div>
                    <div className="font-semibold text-sm flex items-center gap-2 group-hover:text-indigo-400 transition-colors">
                      {rule.name}
                      <span className={cn(
                        "text-[10px] uppercase tracking-wider px-1.5 py-0.5 rounded",
                        rule.status === 'active' ? "bg-indigo-500/10 text-indigo-400" : "bg-muted text-muted-foreground"
                      )}>
                        {rule.status}
                      </span>
                    </div>
                    <div className="flex gap-4 items-center mt-1 text-xs text-muted-foreground">
                      <span>Trigger: {rule.trigger.type}</span>
                      {rule.lastExecution && (
                        <span>Last run: {new Date(rule.lastExecution).toLocaleDateString()}</span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 sm:self-center self-start pl-14 sm:pl-0">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    onClick={() => toggle({ id: rule.id, status: rule.status === 'active' ? 'paused' : 'active' })}
                    className={cn("h-8 text-xs font-medium", rule.status === 'active' ? "text-amber-500 hover:text-amber-400 hover:bg-amber-500/10" : "text-emerald-500 hover:text-emerald-400 hover:bg-emerald-500/10")}
                  >
                    {rule.status === 'active' ? <><Pause className="h-3 w-3 mr-1" /> Pause</> : <><Play className="h-3 w-3 mr-1" /> Resume</>}
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10 text-muted-foreground">
                    <Settings2 className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10 text-muted-foreground">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isLoading && (
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
                  <Skeleton className="h-8 w-20 rounded" />
                </div>
              ))}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
