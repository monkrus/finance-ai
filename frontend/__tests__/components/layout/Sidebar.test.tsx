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
    // Reset matchMedia to a desktop viewport (a test may override it to mobile).
    (window.matchMedia as jest.Mock).mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));
  });

  it('renders correctly when open', () => {
    render(<Sidebar />);
    expect(screen.getByText('FinPilot AI')).toBeInTheDocument();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('does not render when collapsed on mobile', () => {
    // On mobile the sidebar defaults to collapsed; simulate a mobile viewport so
    // the responsive effect keeps it closed, then assert it renders nothing.
    (window.matchMedia as jest.Mock).mockImplementation((query: string) => ({
      matches: true,
      media: query,
      onchange: null,
      addListener: jest.fn(),
      removeListener: jest.fn(),
      addEventListener: jest.fn(),
      removeEventListener: jest.fn(),
      dispatchEvent: jest.fn(),
    }));
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
