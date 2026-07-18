'use client';

import React from 'react';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { cn } from '@/lib/utils';
import { motion } from 'motion/react';

interface WidgetSkeletonProps {
  className?: string;
}

export function WidgetSkeleton({ className }: WidgetSkeletonProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="h-full w-full"
    >
      <Card className={cn("h-full border-card-border shadow-md bg-card/50", className)}>
        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
          <div className="space-y-2 w-full">
            <Skeleton className="h-4 w-[150px]" />
            <Skeleton className="h-3 w-[100px]" />
          </div>
          <Skeleton className="h-8 w-8 rounded-full" />
        </CardHeader>
        <CardContent className="space-y-4 pt-4 flex-1">
          <Skeleton className="h-[40px] w-full" />
          <Skeleton className="h-[20px] w-3/4" />
          <Skeleton className="h-[60px] w-full mt-4" />
        </CardContent>
      </Card>
    </motion.div>
  );
}
