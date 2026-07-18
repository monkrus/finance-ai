"use client";

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useUnreadCount } from '../api/queries';
import { BellRing } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { motion } from 'framer-motion';

export function NotificationWidget() {
  const { data: unreadCount = 0, isLoading } = useUnreadCount();

  return (
    <Card className="bg-card/40 backdrop-blur-xl border-white/10 shadow-lg relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/20 rounded-full blur-3xl pointer-events-none -translate-y-1/2 translate-x-1/2 transition-all group-hover:bg-indigo-500/30" />
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-semibold flex items-center text-muted-foreground">
          <BellRing className="h-4 w-4 mr-2" />
          Alerts
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex justify-between items-end">
          <div>
            {isLoading ? (
              <div className="h-10 w-16 bg-white/5 animate-pulse rounded" />
            ) : (
              <motion.div 
                key={unreadCount}
                initial={{ scale: 0.8, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="text-4xl font-bold tracking-tight text-foreground"
              >
                {unreadCount}
              </motion.div>
            )}
            <p className="text-xs text-muted-foreground mt-1">Unread Notifications</p>
          </div>
          <Button variant="ghost" size="sm" asChild className="hover:bg-white/10 text-indigo-400">
            <Link href="/notifications">View Inbox</Link>
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
