import React from 'react';
import { render } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopNavigation } from '@/components/layout/TopNavigation';
import { Widget } from '@/components/cards/Widget';
import { useUIStore } from '@/store/ui';
import { usePathname } from 'next/navigation';

expect.extend(toHaveNoViolations);

// TopNavigation's account menu uses useLogout(), which needs the app router.
jest.mock('next/navigation', () => ({
  usePathname: jest.fn().mockReturnValue('/dashboard'),
  useRouter: jest.fn().mockReturnValue({ replace: jest.fn(), push: jest.fn() }),
}));

describe('Accessibility tests', () => {
  beforeEach(() => {
    useUIStore.setState({ sidebarOpen: true, notificationsCount: 0 });
  });

  it('Sidebar should have no accessibility violations', async () => {
    const { container } = render(<Sidebar />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('TopNavigation should have no accessibility violations', async () => {
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
    const { container } = render(
      <QueryClientProvider client={queryClient}>
        <TopNavigation />
      </QueryClientProvider>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('Widget should have no accessibility violations', async () => {
    const { container } = render(
      <Widget title="Test Widget" description="Widget description">
        <p>Widget content</p>
      </Widget>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
