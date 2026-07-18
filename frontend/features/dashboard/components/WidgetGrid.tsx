'use client';

import React from 'react';
import { cn } from '@/lib/utils';
import { motion } from 'motion/react';

interface WidgetGridProps {
  children: React.ReactNode;
  className?: string;
}

export function WidgetGrid({ children, className }: WidgetGridProps) {
  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6", className)}>
      {children}
    </div>
  );
}

interface WidgetGridItemProps {
  children: React.ReactNode;
  className?: string;
  colSpan?: 1 | 2 | 3 | 4;
  rowSpan?: 1 | 2;
  index?: number; // for staggered animation
}

export function WidgetGridItem({ 
  children, 
  className,
  colSpan = 1,
  rowSpan = 1,
  index = 0
}: WidgetGridItemProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05, ease: 'easeOut' }}
      className={cn(
        "w-full h-full min-h-[300px]",
        colSpan === 2 && "md:col-span-2",
        colSpan === 3 && "md:col-span-2 lg:col-span-3",
        colSpan === 4 && "md:col-span-2 lg:col-span-3 xl:col-span-4",
        rowSpan === 2 && "row-span-2 min-h-[600px]",
        className
      )}
    >
      {children}
    </motion.div>
  );
}
