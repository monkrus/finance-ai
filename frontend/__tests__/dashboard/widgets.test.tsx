import React from 'react';
import { render, screen } from '@testing-library/react';
import { KPIWidget } from '@/features/dashboard/widgets/KPIWidget';
import { PortfolioSnapshotWidget } from '@/features/dashboard/widgets/PortfolioSnapshotWidget';
import { MarketOverviewWidget } from '@/features/dashboard/widgets/MarketOverviewWidget';
import { NewsWidget } from '@/features/dashboard/widgets/NewsWidget';
import { AIInsightsWidget } from '@/features/dashboard/widgets/AIInsightsWidget';
import { WatchlistWidget } from '@/features/dashboard/widgets/WatchlistWidget';
import { CalendarWidget } from '@/features/dashboard/widgets/CalendarWidget';
import { NotificationWidget } from '@/features/dashboard/widgets/NotificationWidget';
import { RecentActivityWidget } from '@/features/dashboard/widgets/RecentActivityWidget';
import { useKPIs, useDashboardOverview, useMarketOverview, useDashboardNews, useAIInsights } from '@/features/dashboard/api/queries';

jest.mock('@/features/dashboard/api/queries', () => ({
  useKPIs: jest.fn(),
  useDashboardOverview: jest.fn(),
  useMarketOverview: jest.fn(),
  useDashboardNews: jest.fn(),
  useAIInsights: jest.fn(),
}));

jest.mock('next-themes', () => ({
  useTheme: () => ({ theme: 'light' }),
}));

jest.mock('recharts', () => {
  const OriginalRecharts = jest.requireActual('recharts');
  return {
    ...OriginalRecharts,
    ResponsiveContainer: ({ children }: any) => <div data-testid="recharts-container">{children}</div>,
    PieChart: ({ children }: any) => <div>{children}</div>,
    Pie: () => <div />,
    Cell: () => <div />,
    Tooltip: ({ formatter }: any) => {
      // Trigger the formatter manually for coverage
      if (formatter) {
        formatter(45);
      }
      return <div />;
    },
    LineChart: ({ children }: any) => <div>{children}</div>,
    Line: () => <div />,
    YAxis: () => <div />,
  };
});

describe('Dashboard Widgets', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  // KPI Widget
  it('renders KPIWidget loading state', () => {
    (useKPIs as jest.Mock).mockReturnValue({ isLoading: true });
    render(<KPIWidget />);
    expect(screen.queryAllByTestId('recharts-container').length).toBe(0); // Skeletons are rendering
  });

  it('renders KPIWidget error state', () => {
    const refetch = jest.fn();
    (useKPIs as jest.Mock).mockReturnValue({ isError: true, refetch });
    render(<KPIWidget />);
    expect(screen.getByText('Error Loading Widget')).toBeInTheDocument();
  });

  it('renders KPIWidget data with varying trends and formats', () => {
    (useKPIs as jest.Mock).mockReturnValue({
      isLoading: false,
      data: [
        { id: '1', label: 'Net Worth', value: 1000, delta: 5, trend: 'up', format: 'currency' },
        { id: '2', label: 'Cash', value: 500, delta: -2, trend: 'down', format: 'percentage' },
        { id: '3', label: 'Score', value: 88, delta: 0, trend: 'neutral', format: 'number' }
      ]
    });
    render(<KPIWidget />);
    expect(screen.getByText('Net Worth')).toBeInTheDocument();
    expect(screen.getByText('$1,000.00')).toBeInTheDocument();
    expect(screen.getByText('Cash')).toBeInTheDocument();
    expect(screen.getByText('500')).toBeInTheDocument();
    expect(screen.getByText('88')).toBeInTheDocument();
  });

  // Portfolio Widget
  it('renders PortfolioSnapshotWidget loading/error', () => {
    (useDashboardOverview as jest.Mock).mockReturnValue({ isError: true });
    render(<PortfolioSnapshotWidget />);
    expect(screen.getByText('Error Loading Widget')).toBeInTheDocument();
  });

  it('renders PortfolioSnapshotWidget data', () => {
    (useDashboardOverview as jest.Mock).mockReturnValue({
      isLoading: false,
      data: { portfolioValue: 500000, portfolioChange: 1.5 }
    });
    render(<PortfolioSnapshotWidget />);
    expect(screen.getByText('Portfolio Snapshot')).toBeInTheDocument();
    // Real total value is shown...
    expect(screen.getByText('$500,000.00')).toBeInTheDocument();
    // ...but no fabricated holdings are ever invented.
    expect(screen.queryByText('AAPL')).not.toBeInTheDocument();
    expect(screen.queryByText('MSFT')).not.toBeInTheDocument();
    expect(screen.queryByText('NVDA')).not.toBeInTheDocument();
  });

  it('PortfolioSnapshotWidget shows an empty state (no invented holdings) for a new user', () => {
    (useDashboardOverview as jest.Mock).mockReturnValue({
      isLoading: false,
      data: { portfolioValue: 0, portfolioChange: 0 }
    });
    render(<PortfolioSnapshotWidget />);
    expect(screen.getByText("You don't have any investments yet.")).toBeInTheDocument();
    expect(screen.getByText('$0.00')).toBeInTheDocument();
    expect(screen.queryByText('AAPL')).not.toBeInTheDocument();
    expect(screen.queryByText('MSFT')).not.toBeInTheDocument();
    expect(screen.queryByText('NVDA')).not.toBeInTheDocument();
  });

  // Market Widget
  it('renders MarketOverviewWidget loading/error', () => {
    (useMarketOverview as jest.Mock).mockReturnValue({ isError: true });
    render(<MarketOverviewWidget />);
    expect(screen.getByText('Error Loading Widget')).toBeInTheDocument();
  });

  it('renders MarketOverviewWidget data with up/down trends', () => {
    (useMarketOverview as jest.Mock).mockReturnValue({
      isLoading: false,
      data: [
        { symbol: 'SPX', name: 'S&P 500', price: 5000, change: 10, changePercent: 0.2 },
        { symbol: 'VIX', name: 'Volatility', price: 14, change: -1, changePercent: -5.0 }
      ]
    });
    render(<MarketOverviewWidget />);
    expect(screen.getByText('SPX')).toBeInTheDocument();
    expect(screen.getByText('VIX')).toBeInTheDocument();
  });

  // News Widget
  it('renders NewsWidget loading/error', () => {
    (useDashboardNews as jest.Mock).mockReturnValue({ isError: true });
    render(<NewsWidget />);
    expect(screen.getByText('Error Loading Widget')).toBeInTheDocument();
  });

  it('renders NewsWidget data with multiple sentiments', () => {
    (useDashboardNews as jest.Mock).mockReturnValue({
      isLoading: false,
      data: [
        { id: '1', title: 'Pos', summary: '', source: '', publishedAt: '2026-07-16T12:00:00Z', sentiment: 'positive', importance: 'high' },
        { id: '2', title: 'Neg', summary: '', source: '', publishedAt: '2026-07-16T12:00:00Z', sentiment: 'negative', importance: 'medium' },
        { id: '3', title: 'Neu', summary: '', source: '', publishedAt: '2026-07-16T12:00:00Z', sentiment: 'neutral', importance: 'low' },
      ]
    });
    render(<NewsWidget />);
    expect(screen.getByText('POSITIVE')).toBeInTheDocument();
    expect(screen.getByText('NEGATIVE')).toBeInTheDocument();
    expect(screen.getByText('NEUTRAL')).toBeInTheDocument();
    expect(screen.getByText('IMPORTANT')).toBeInTheDocument();
  });

  // AI Widget
  it('renders AIInsightsWidget loading/error/empty', () => {
    (useAIInsights as jest.Mock).mockReturnValue({ data: [] });
    render(<AIInsightsWidget />);
    expect(screen.getByText('Error Loading Widget')).toBeInTheDocument();
  });

  it('renders AIInsightsWidget data', () => {
    (useAIInsights as jest.Mock).mockReturnValue({
      isLoading: false,
      data: [{ id: '1', title: 'Insight', description: 'Desc', category: 'portfolio', timestamp: '', confidence: 0.9 }]
    });
    render(<AIInsightsWidget />);
    expect(screen.getByText('Insight')).toBeInTheDocument();
  });

  // These widgets have no wired client data source. They must show empty
  // states, never fabricated financial data (P0-2).
  it('renders empty states for the non-data-backed widgets', () => {
    render(
      <>
        <WatchlistWidget />
        <CalendarWidget />
        <NotificationWidget />
        <RecentActivityWidget />
      </>
    );
    // Titles preserved
    expect(screen.getByText('Watchlist')).toBeInTheDocument();
    expect(screen.getByText('Upcoming Events')).toBeInTheDocument();
    expect(screen.getByText('Notification Center')).toBeInTheDocument();
    expect(screen.getByText('Recent Activity')).toBeInTheDocument();
    // Empty-state copy shown
    expect(screen.getByText('Create your first watchlist.')).toBeInTheDocument();
    expect(screen.getByText('No upcoming events.')).toBeInTheDocument();
    expect(screen.getByText('No notifications.')).toBeInTheDocument();
    expect(screen.getByText('No activity yet.')).toBeInTheDocument();
  });

  // P0-2: guard that these widgets NEVER fabricate financial information,
  // regardless of user. A snapshot of the rendered text must contain none of
  // the previously hardcoded tickers, trades, prices, or events.
  it('never renders fabricated financial data in the non-data-backed widgets', () => {
    const { container } = render(
      <>
        <WatchlistWidget />
        <CalendarWidget />
        <NotificationWidget />
        <RecentActivityWidget />
      </>
    );
    const text = container.textContent || '';
    [
      'AAPL', 'MSFT', 'TSLA', 'NVDA',        // fabricated tickers
      'Apple Inc.', 'Microsoft', 'Tesla',    // fabricated names
      'Bought', 'Sold', 'Dividend Reinvested', 'Deposit cleared', // fabricated trades
      'Margin Call', 'Portfolio Rebalanced', // fabricated alerts
      'Q2 Earnings', 'Ex-Date', 'Fed Interest Rate', // fabricated events
      '173.50', '415.20', '175.22',          // fabricated prices
    ].forEach((forbidden) => {
      expect(text).not.toContain(forbidden);
    });
  });
});
