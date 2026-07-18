"use client";

import React from 'react';
import { useAuditLogs } from '../api/queries';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { History, Shield, Network, User, Settings2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export function AuditLogs() {
  const { data, isLoading, isError, refetch } = useAuditLogs();

  if (isError) return <WidgetError title="Audit Error" message="Failed to load logs." onRetry={refetch} />;

  const getActionIcon = (action: string) => {
    if (action.includes('LOGIN') || action.includes('AUTH')) return <Shield className="h-4 w-4 text-emerald-400" />;
    if (action.includes('SYNC') || action.includes('INTEGRATION')) return <Network className="h-4 w-4 text-indigo-400" />;
    if (action.includes('PROFILE')) return <User className="h-4 w-4 text-amber-400" />;
    return <Settings2 className="h-4 w-4 text-muted-foreground" />;
  };

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-8">
      <div>
        <h2 className="text-2xl md:text-3xl font-bold tracking-tight">Audit Logs</h2>
        <p className="text-muted-foreground mt-1">Review account activity and system events.</p>
      </div>

      <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg overflow-hidden">
        <div className="overflow-x-auto custom-scrollbar">
          <table className="w-full text-sm text-left">
            <thead className="bg-muted/50 text-muted-foreground border-b border-white/5 uppercase text-[10px] tracking-wider font-semibold">
              <tr>
                <th className="px-6 py-4">Event</th>
                <th className="px-6 py-4">Actor</th>
                <th className="px-6 py-4">Timestamp</th>
                <th className="px-6 py-4">IP Address</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border/50">
              {isLoading || !data ? (
                Array.from({ length: 6 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-24" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-32" /></td>
                    <td className="px-6 py-4"><Skeleton className="h-4 w-20" /></td>
                  </tr>
                ))
              ) : (
                <AnimatePresence>
                  {data.map(log => (
                    <motion.tr key={log.id} initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="hover:bg-white/5 transition-colors">
                      <td className="px-6 py-4">
                        <div className="flex flex-col gap-1">
                          <span className="font-medium flex items-center gap-2">
                            {getActionIcon(log.action)}
                            {log.action}
                          </span>
                          <span className="text-xs text-muted-foreground line-clamp-1">{log.details}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-muted-foreground">{log.actor}</td>
                      <td className="px-6 py-4 text-muted-foreground whitespace-nowrap">{new Date(log.timestamp).toLocaleString()}</td>
                      <td className="px-6 py-4 text-muted-foreground font-mono text-xs">{log.ip}</td>
                    </motion.tr>
                  ))}
                </AnimatePresence>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </motion.div>
  );
}
