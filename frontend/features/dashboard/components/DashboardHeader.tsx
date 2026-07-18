'use client';

import React from 'react';
import { useAuthStore } from '@/store/auth';
import { Search, Bell } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { motion } from 'motion/react';

export function DashboardHeader() {
  const user = useAuthStore((state) => state.user);

  // Time-based greeting
  const hour = new Date().getHours();
  let greeting = 'Good evening';
  if (hour < 12) greeting = 'Good morning';
  else if (hour < 18) greeting = 'Good afternoon';

  return (
    <motion.div 
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
      className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4"
    >
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-foreground">
          {greeting}, {user?.firstName || 'Investor'}
        </h1>
        <p className="text-muted-foreground mt-1">
          Here is your wealth overview for today.
        </p>
      </div>

      <div className="flex items-center gap-4 w-full md:w-auto">
        <div className="relative w-full md:w-64">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" aria-hidden="true" />
          <Input 
            type="search"
            aria-label="Search assets and news"
            placeholder="Search assets, news..." 
            className="pl-9 bg-background/50 backdrop-blur-sm border-card-border"
          />
        </div>
        
        <button 
          aria-label="View notifications"
          className="relative p-2 rounded-full hover:bg-accent transition-colors flex-shrink-0"
        >
          <Bell className="h-5 w-5 text-muted-foreground" aria-hidden="true" />
          <span className="absolute top-1 right-1 h-2 w-2 rounded-full bg-destructive border border-background" aria-label="Unread notifications"></span>
        </button>
      </div>
    </motion.div>
  );
}
