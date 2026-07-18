import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { WidgetCard } from '@/features/dashboard/components/WidgetCard';
import { WidgetError } from '@/features/dashboard/components/WidgetError';
import { WidgetEmpty } from '@/features/dashboard/components/WidgetEmpty';
import { WidgetSkeleton } from '@/features/dashboard/components/WidgetSkeleton';
import { WidgetGrid, WidgetGridItem } from '@/features/dashboard/components/WidgetGrid';
import { DashboardHeader } from '@/features/dashboard/components/DashboardHeader';

jest.mock('@/store/auth', () => ({
  useAuthStore: () => ({ user: { firstName: 'Test' } }),
}));

describe('Dashboard Component Architecture', () => {
  beforeEach(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders WidgetCard correctly', () => {
    render(
      <WidgetCard title="Test Title" description="Test Description" premium={true} headerAction={<button>Action</button>}>
        <div>Test Content</div>
      </WidgetCard>
    );
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });
  
  it('renders WidgetCard non-premium correctly', () => {
    render(
      <WidgetCard title="Test Title" premium={false}>
        <div>Test Content</div>
      </WidgetCard>
    );
    expect(screen.getByText('Test Title')).toBeInTheDocument();
  });

  it('renders WidgetError correctly and handles retry', () => {
    const onRetry = jest.fn();
    render(<WidgetError title="Error Occurred" message="Something broke" onRetry={onRetry} />);
    
    const btn = screen.getByText('Retry');
    fireEvent.click(btn);
    expect(onRetry).toHaveBeenCalledTimes(1);
  });

  it('renders WidgetEmpty correctly with action', () => {
    render(<WidgetEmpty title="No items" message="Empty state" action={<button>Add</button>} />);
    expect(screen.getByText('Add')).toBeInTheDocument();
  });

  it('renders WidgetSkeleton correctly', () => {
    const { container } = render(<WidgetSkeleton />);
    expect(container.firstChild).toBeInTheDocument();
  });

  it('renders WidgetGrid correctly', () => {
    render(
      <WidgetGrid>
        <WidgetGridItem colSpan={2} rowSpan={2} index={1}>
          <div>Item</div>
        </WidgetGridItem>
        <WidgetGridItem colSpan={3}>
          <div>Item 3</div>
        </WidgetGridItem>
        <WidgetGridItem colSpan={4}>
          <div>Item 4</div>
        </WidgetGridItem>
      </WidgetGrid>
    );
    expect(screen.getAllByText(/Item/).length).toBeGreaterThan(0);
  });

  it('renders DashboardHeader morning greeting', () => {
    const mockDate = new Date();
    jest.spyOn(mockDate, 'getHours').mockReturnValue(9);
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate as unknown as Date);
    
    render(<DashboardHeader />);
    expect(screen.getByText(/Good morning/)).toBeInTheDocument();
    jest.restoreAllMocks();
  });

  it('renders DashboardHeader afternoon greeting', () => {
    const mockDate = new Date();
    jest.spyOn(mockDate, 'getHours').mockReturnValue(15);
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate as unknown as Date);
    
    render(<DashboardHeader />);
    expect(screen.getByText(/Good afternoon/)).toBeInTheDocument();
    jest.restoreAllMocks();
  });
  
  it('renders DashboardHeader evening greeting', () => {
    const mockDate = new Date();
    jest.spyOn(mockDate, 'getHours').mockReturnValue(20);
    jest.spyOn(global, 'Date').mockImplementation(() => mockDate as unknown as Date);
    
    render(<DashboardHeader />);
    expect(screen.getByText(/Good evening/)).toBeInTheDocument();
    jest.restoreAllMocks();
  });
});
