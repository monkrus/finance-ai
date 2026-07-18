import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { axe, toHaveNoViolations } from 'jest-axe';
import PortfolioPage from '@/app/(dashboard)/portfolio/page';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

expect.extend(toHaveNoViolations);

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

jest.mock('@/store/auth', () => ({
  useAuthStore: () => ({
    user: { firstName: 'Test' },
  }),
}));

describe('Portfolio Page', () => {
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

  it('renders portfolio page', () => {
    render(
      <QueryClientProvider client={queryClient}>
        <PortfolioPage />
      </QueryClientProvider>
    );
    
    expect(screen.getByText(/Portfolio Management/i)).toBeInTheDocument();
  });

  it('should have no accessibility violations', async () => {
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <PortfolioPage />
      </QueryClientProvider>
    );
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
