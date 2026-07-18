"use client";

import React from 'react';
import { Notification } from '../types';
import { useMarkAsRead, useArchiveNotification } from '../api/queries';
import { PieChart, Globe, Newspaper, Briefcase, Sparkles, Network, Circle, CheckCircle2, Archive, MoreHorizontal } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';
import { cn } from '@/lib/utils';
import { formatDistanceToNow } from 'date-fns';

export function NotificationCard({ notification }: { notification: Notification }) {
  const { mutate: markRead } = useMarkAsRead();
  const { mutate: archive } = useArchiveNotification();

  const getIcon = () => {
    switch (notification.category) {
      case 'Portfolio': return <PieChart className="h-5 w-5 text-indigo-400" />;
      case 'Market': return <Globe className="h-5 w-5 text-emerald-400" />;
      case 'News': return <Newspaper className="h-5 w-5 text-blue-400" />;
      case 'Wealth': return <Briefcase className="h-5 w-5 text-amber-400" />;
      case 'AI': return <Sparkles className="h-5 w-5 text-fuchsia-400" />;
      default: return <Network className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getPriorityColor = () => {
    switch (notification.priority) {
      case 'CRITICAL': return 'bg-destructive text-destructive-foreground';
      case 'HIGH': return 'bg-amber-500 text-black';
      case 'MEDIUM': return 'bg-blue-500 text-white';
      default: return 'bg-muted text-muted-foreground';
    }
  };

  return (
    <motion.div 
      layout
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className={cn(
        "group relative flex items-start gap-4 p-4 rounded-xl transition-all border",
        notification.status === 'unread' 
          ? "bg-white/5 border-white/10 hover:bg-white/10" 
          : "bg-transparent border-transparent hover:bg-white/5"
      )}
    >
      <div className="shrink-0 p-2.5 bg-background rounded-full border border-white/10 shadow-sm mt-1">
        {getIcon()}
      </div>

      <div className="flex-1 min-w-0 pr-8">
        <div className="flex items-center gap-2 mb-1">
          <span className={cn("text-[10px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded", getPriorityColor())}>
            {notification.priority}
          </span>
          <span className="text-xs text-muted-foreground font-medium">
            {formatDistanceToNow(new Date(notification.timestamp), { addSuffix: true })}
          </span>
        </div>
        <h4 className={cn("text-base font-semibold truncate mb-1", notification.status === 'unread' ? 'text-foreground' : 'text-foreground/80')}>
          {notification.title}
        </h4>
        <p className="text-sm text-muted-foreground line-clamp-2 leading-relaxed">
          {notification.summary}
        </p>
      </div>

      <div className="absolute right-4 top-4 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
        {notification.status === 'unread' && (
          <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10 text-emerald-400" onClick={() => markRead(notification.id)} title="Mark as read">
            <CheckCircle2 className="h-4 w-4" />
          </Button>
        )}
        <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10 text-muted-foreground hover:text-foreground" onClick={() => archive(notification.id)} title="Archive">
          <Archive className="h-4 w-4" />
        </Button>
        <Button variant="ghost" size="icon" className="h-8 w-8 hover:bg-white/10 text-muted-foreground">
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </div>
      
      {notification.status === 'unread' && (
        <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-indigo-500 rounded-r-full" />
      )}
    </motion.div>
  );
}
