import React from 'react';
import { render, screen } from '@testing-library/react';
import { Sidebar } from '@/components/layout/Sidebar';
import { useUIStore } from '@/store/ui';
import { usePathname } from 'next/navigation';

jest.mock('next/navigation', () => ({
  usePathname: jest.fn(),
}));

describe('Sidebar Component', () => {
  beforeEach(() => {
    (usePathname as jest.Mock).mockReturnValue('/dashboard');
    useUIStore.setState({ sidebarOpen: true });
  });

  it('renders correctly when open', () => {
    render(<Sidebar />);
    expect(screen.getByText('FinPilot AI')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('does not render when sidebarOpen is false', () => {
    useUIStore.setState({ sidebarOpen: false });
    const { container } = render(<Sidebar />);
    expect(container).toBeEmptyDOMElement();
  });

  it('applies active class to current route', () => {
    render(<Sidebar />);
    // Dashboard should be active since mock returns /dashboard
    const dashboardLink = screen.getByText('Dashboard').closest('a');
    expect(dashboardLink).toHaveClass('bg-primary/10');
    expect(dashboardLink).toHaveClass('text-primary');

    // Portfolio should not be active
    const portfolioLink = screen.getByText('Portfolio').closest('a');
    expect(portfolioLink).toHaveClass('text-muted-foreground');
  });
});
