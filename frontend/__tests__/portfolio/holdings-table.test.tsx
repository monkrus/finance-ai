import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { HoldingsTable } from '@/features/portfolio/tables/HoldingsTable';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: jest.fn(),
      replace: jest.fn(),
    };
  },
  usePathname() {
    return '/portfolio';
  },
}));

describe('Holdings Table', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  it('renders loading state initially', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <HoldingsTable />
      </QueryClientProvider>
    );
    
    expect(screen.getByText(/Holdings/i)).toBeInTheDocument();
  });
});
