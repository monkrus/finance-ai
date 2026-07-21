'use client';

import * as React from 'react';
import QueryProvider from './QueryProvider';
import { ThemeProvider } from './ThemeProvider';
import { Toaster } from '@/components/ui/sonner';

export function RootProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <QueryProvider>
        {children}
        {/* Global toast host — without this every toast.*() call is silent
            (e.g. login errors, success messages) across the whole app. */}
        <Toaster />
      </QueryProvider>
    </ThemeProvider>
  );
}
