import React from 'react';
import { cn } from '@/lib/utils';
import { Loader2, AlertCircle } from 'lucide-react';

export interface WidgetProps extends React.HTMLAttributes<HTMLDivElement> {
  title?: string;
  description?: string;
  isLoading?: boolean;
  isError?: boolean;
  errorMessage?: string;
  isEmpty?: boolean;
  emptyMessage?: string;
  action?: React.ReactNode;
  footer?: React.ReactNode;
}

export function Widget({
  title,
  description,
  isLoading = false,
  isError = false,
  errorMessage = "Something went wrong.",
  isEmpty = false,
  emptyMessage = "No data available.",
  action,
  footer,
  children,
  className,
  ...props
}: WidgetProps) {
  return (
    <div 
      className={cn("bg-card text-card-foreground rounded-xl border shadow-sm flex flex-col overflow-hidden", className)} 
      {...props}
    >
      {/* Header */}
      {(title || description || action) && (
        <div className="px-6 py-4 flex flex-row items-center justify-between border-b bg-muted/20">
          <div className="flex flex-col space-y-1">
            {title && <h3 className="font-semibold leading-none tracking-tight">{title}</h3>}
            {description && <p className="text-sm text-muted-foreground">{description}</p>}
          </div>
          {action && <div>{action}</div>}
        </div>
      )}

      {/* Content Area */}
      <div className="p-6 flex-1 flex flex-col relative min-h-[150px]">
        {isLoading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-background/50 z-10 backdrop-blur-sm">
            <Loader2 className="h-8 w-8 animate-spin text-primary" />
          </div>
        ) : isError ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-4">
            <AlertCircle className="h-10 w-10 text-destructive mb-4" />
            <p className="text-sm font-medium">{errorMessage}</p>
          </div>
        ) : isEmpty ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-4">
            <p className="text-sm text-muted-foreground">{emptyMessage}</p>
          </div>
        ) : (
          children
        )}
      </div>

      {/* Footer */}
      {footer && (
        <div className="px-6 py-4 border-t bg-muted/10">
          {footer}
        </div>
      )}
    </div>
  );
}
