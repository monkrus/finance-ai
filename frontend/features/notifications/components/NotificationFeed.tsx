"use client";

import React, { useRef, useEffect, useState } from 'react';
import { useNotifications } from '../api/queries';
import { NotificationCard } from './NotificationCard';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { Skeleton } from '@/components/ui/skeleton';
import { AnimatePresence } from 'framer-motion';

export function NotificationFeed() {
  const { data, isLoading, isError, fetchNextPage, hasNextPage, isFetchingNextPage, refetch } = useNotifications();
  const [activeTab, setActiveTab] = useState<'All' | 'Unread'>('All');
  const observerTarget = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasNextPage && !isFetchingNextPage) {
          fetchNextPage();
        }
      },
      { threshold: 0.1 }
    );
    if (observerTarget.current) observer.observe(observerTarget.current);
    return () => observer.disconnect();
  }, [hasNextPage, isFetchingNextPage, fetchNextPage]);

  if (isError) {
    return <WidgetError title="Feed Error" message="Failed to load notifications." onRetry={refetch} />;
  }

  const allNotifications = (data?.pages.flatMap(p => p.notifications ?? []) ?? []).filter(Boolean);
  const filtered = activeTab === 'Unread' ? allNotifications.filter(n => n.status === 'unread') : allNotifications;

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] border border-white/5 rounded-2xl bg-card/40 backdrop-blur-3xl overflow-hidden shadow-2xl">
      <div className="h-12 border-b border-white/5 flex items-center px-4 gap-6 text-sm shrink-0">
        <button 
          onClick={() => setActiveTab('All')}
          className={`h-full border-b-2 transition-colors ${activeTab === 'All' ? 'border-indigo-500 text-indigo-400 font-medium' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          All Notifications
        </button>
        <button 
          onClick={() => setActiveTab('Unread')}
          className={`h-full border-b-2 transition-colors flex items-center gap-2 ${activeTab === 'Unread' ? 'border-indigo-500 text-indigo-400 font-medium' : 'border-transparent text-muted-foreground hover:text-foreground'}`}
        >
          Unread
          <span className="bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded text-[10px]">
            {allNotifications.filter(n => n.status === 'unread').length}
          </span>
        </button>
      </div>

      <div className="flex-1 overflow-y-auto custom-scrollbar p-2">
        <div className="flex flex-col gap-1 max-w-4xl mx-auto">
          <AnimatePresence>
            {filtered.map(notification => (
              <NotificationCard key={notification.id} notification={notification} />
            ))}
          </AnimatePresence>
          
          {(isLoading || isFetchingNextPage) && (
            <div className="space-y-1">
              {Array.from({ length: 4 }).map((_, i) => (
                <div key={i} className="flex gap-4 p-4 rounded-xl border border-white/5 bg-background/20">
                  <Skeleton className="h-10 w-10 rounded-full shrink-0" />
                  <div className="space-y-2 w-full">
                    <Skeleton className="h-4 w-1/3" />
                    <Skeleton className="h-3 w-2/3" />
                  </div>
                </div>
              ))}
            </div>
          )}
          <div ref={observerTarget} className="h-4 w-full" />
        </div>
      </div>
    </div>
  );
}
