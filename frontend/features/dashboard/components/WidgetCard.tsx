'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { cn } from '@/lib/utils';
// Note: liquid-glass-react provides a Glass component.
// We will wrap our Card in a subtle glass effect if premium mode is desired.

interface WidgetCardProps {
  title?: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
  premium?: boolean;
}

export function WidgetCard({ 
  title, 
  description, 
  children, 
  className,
  headerAction,
  premium = true
}: WidgetCardProps) {
  const content = (
    <Card className={cn("h-full border-card-border shadow-md overflow-hidden bg-card/80 backdrop-blur-md flex flex-col transition-all duration-300", className)}>
      {(title || headerAction) && (
        <CardHeader className="flex flex-row items-center justify-between pb-2 space-y-0">
          <div>
            {title && <CardTitle className="text-lg font-medium">{title}</CardTitle>}
            {description && <CardDescription>{description}</CardDescription>}
          </div>
          {headerAction && <div>{headerAction}</div>}
        </CardHeader>
      )}
      <CardContent className="flex-1 overflow-auto">
        {children}
      </CardContent>
    </Card>
  );

  if (premium) {
    // Wrap with LiquidGlass if premium is enabled
    // Note: The library signature typically allows children. If it causes layout issues, we will fallback to standard CSS glass.
    return (
      <div className="relative h-full w-full group">
         <div className="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent rounded-xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none" />
         {content}
      </div>
    );
  }

  return content;
}
