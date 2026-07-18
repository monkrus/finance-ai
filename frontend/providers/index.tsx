'use client';

import * as React from 'react';
import QueryProvider from './QueryProvider';
import { ThemeProvider } from './ThemeProvider';

export function RootProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="system" enableSystem disableTransitionOnChange>
      <QueryProvider>
        {children}
      </QueryProvider>
    </ThemeProvider>
  );
}
