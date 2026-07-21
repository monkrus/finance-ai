'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AxiosError } from 'axios';
import { useState } from 'react';

export default function QueryProvider({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000, // 1 minute
            refetchOnWindowFocus: false,
            // Don't retry client errors (4xx) — a 404/400/403 will never recover
            // by retrying, and doing so leaves widgets in a loading skeleton for
            // seconds before their error state appears. Retry only transient
            // network/5xx failures, and cap the attempts.
            retry: (failureCount, error) => {
              const status = (error as AxiosError)?.response?.status;
              if (status && status >= 400 && status < 500) return false;
              return failureCount < 2;
            },
          },
        },
      })
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
