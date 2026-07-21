'use client';

import React from 'react';
import { Card, CardTitle, CardDescription } from '@/components/ui/card';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'motion/react';

interface WidgetErrorProps {
  title?: string;
  message?: string;
  onRetry?: () => void;
  className?: string;
}

export function WidgetError({ 
  title = "Error Loading Widget", 
  message = "We encountered a problem fetching this data.", 
  onRetry,
  className 
}: WidgetErrorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      className="h-full w-full"
    >
      <Card className={cn("h-full border-destructive/20 shadow-md bg-destructive/5 flex flex-col items-center justify-center text-center p-6", className)}>
        <AlertCircle className="h-10 w-10 text-destructive mb-4" />
        <CardTitle className="text-lg font-medium text-destructive mb-2">{title}</CardTitle>
        <CardDescription className="mb-4 max-w-[250px]">{message}</CardDescription>
        
        {onRetry && (
          <button 
            onClick={onRetry}
            className="inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 border border-input bg-background hover:bg-accent hover:text-accent-foreground h-9 px-4 py-2"
          >
            <RefreshCw className="mr-2 h-4 w-4" />
            Retry
          </button>
        )}
      </Card>
    </motion.div>
  );
}
