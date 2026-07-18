import React from 'react';
import { render } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';
import { WidgetCard } from '@/features/dashboard/components/WidgetCard';
import { WidgetSkeleton } from '@/features/dashboard/components/WidgetSkeleton';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { WidgetEmpty } from '@/features/dashboard/components/WidgetEmpty';
import { DashboardHeader } from '@/features/dashboard/components/DashboardHeader';
import { KPIWidget } from '@/features/dashboard/widgets/KPIWidget';

expect.extend(toHaveNoViolations);

jest.mock('@/features/dashboard/api/queries', () => ({
  useKPIs: () => ({ isLoading: false, data: [{ id: '1', label: 'Net Worth', value: 100, delta: 0, trend: 'neutral', format: 'currency' }] }),
  useDashboardOverview: () => ({ isLoading: false, data: { portfolioValue: 100, portfolioChange: 1 } }),
  useMarketOverview: () => ({ isLoading: false, data: [] }),
  useDashboardNews: () => ({ isLoading: false, data: [] }),
  useAIInsights: () => ({ isLoading: false, data: [] }),
}));

jest.mock('@/store/auth', () => ({
  useAuthStore: () => ({ firstName: 'Test' }),
}));

jest.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light' }),
}));

describe('Dashboard Accessibility', () => {
  it('WidgetCard should have no accessibility violations', async () => {
    const { container } = render(
      <WidgetCard title="Test" description="Desc">
        <div>Content</div>
      </WidgetCard>
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('WidgetSkeleton should have no accessibility violations', async () => {
    const { container } = render(<WidgetSkeleton />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('WidgetError should have no accessibility violations', async () => {
    const { container } = render(<WidgetError title="Error" message="Msg" />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('WidgetEmpty should have no accessibility violations', async () => {
    const { container } = render(<WidgetEmpty title="Empty" message="Msg" />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('DashboardHeader should have no accessibility violations', async () => {
    const { container } = render(<DashboardHeader />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
  
  it('KPIWidget should have no accessibility violations', async () => {
    const { container } = render(<KPIWidget />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
