"use client";

import React from 'react';
import { useApiKeys } from '../api/queries';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { Key, Plus, Copy, Trash, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';

export function ApiKeys() {
  const { data, isLoading, isError, refetch } = useApiKeys();

  if (isError) return <WidgetError title="API Keys Error" message="Failed to load keys." onRetry={refetch} />;

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl md:text-3xl font-bold tracking-tight">API Keys</h2>
          <p className="text-muted-foreground mt-1">Manage programmatic access to your FinPilot account.</p>
        </div>
        <Button className="bg-indigo-600 hover:bg-indigo-700">
          <Plus className="h-4 w-4 mr-2" /> Generate Key
        </Button>
      </div>

      <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg">
        <CardHeader>
          <CardTitle>Active Tokens</CardTitle>
          <CardDescription>Keep these keys secret. Do not share them in public repositories.</CardDescription>
        </CardHeader>
        <CardContent className="p-0">
          <div className="divide-y divide-border/50">
            {isLoading || !data ? (
              <div className="p-6 space-y-4">
                <Skeleton className="h-12 w-full" />
                <Skeleton className="h-12 w-full" />
              </div>
            ) : (
              <AnimatePresence>
                {data.map(key => (
                  <motion.div key={key.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="p-4 hover:bg-white/5 transition-colors flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 shrink-0 rounded-full bg-indigo-500/10 border border-white/10 flex items-center justify-center">
                        <Key className="h-5 w-5 text-indigo-400" />
                      </div>
                      <div>
                        <div className="font-semibold">{key.name}</div>
                        <div className="text-sm font-mono text-muted-foreground mt-1 bg-background/50 px-2 py-0.5 rounded border border-white/5 inline-flex items-center gap-2">
                          {key.prefix}••••••••••••
                          <button className="hover:text-foreground transition-colors"><Copy className="h-3 w-3" /></button>
                        </div>
                      </div>
                    </div>
                    <div className="flex flex-col md:items-end gap-2 text-sm text-muted-foreground">
                      <div className="flex gap-2">
                        {key.permissions.map(p => (
                          <span key={p} className="text-[10px] uppercase bg-white/5 px-1.5 py-0.5 rounded border border-white/10">{p}</span>
                        ))}
                      </div>
                      <span className="text-xs">
                        Last used: {key.lastUsed ? formatDistanceToNow(new Date(key.lastUsed), { addSuffix: true }) : 'Never'}
                      </span>
                    </div>
                    <div className="flex items-center gap-2 mt-2 md:mt-0">
                      <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10" title="Rotate Key">
                        <RefreshCw className="h-4 w-4" />
                      </Button>
                      <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-destructive/20 hover:text-destructive text-muted-foreground" title="Delete Key">
                        <Trash className="h-4 w-4" />
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
