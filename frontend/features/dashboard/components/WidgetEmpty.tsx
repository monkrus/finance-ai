'use client';

import React from 'react';
import { Card, CardTitle, CardDescription } from '@/components/ui/card';
import { Ghost } from 'lucide-react';
import { cn } from '@/lib/utils';
import { motion } from 'motion/react';

interface WidgetEmptyProps {
  title?: string;
  message?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
}

export function WidgetEmpty({ 
  title = "No Data Found", 
  message = "There is nothing to display here yet.", 
  icon = <Ghost className="h-10 w-10 text-muted-foreground mb-4" />,
  action,
  className 
}: WidgetEmptyProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-full w-full"
    >
      <Card className={cn("h-full border-dashed border-card-border shadow-sm bg-card/20 flex flex-col items-center justify-center text-center p-6", className)}>
        {icon}
        <CardTitle className="text-lg font-medium text-foreground mb-2">{title}</CardTitle>
        <CardDescription className="mb-4 max-w-[250px]">{message}</CardDescription>
        {action && <div>{action}</div>}
      </Card>
    </motion.div>
  );
}
