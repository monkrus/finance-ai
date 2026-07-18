import React from 'react';
import { render, screen } from '@testing-library/react';
import { Widget } from '@/components/cards/Widget';

describe('Widget Component', () => {
  it('renders title and description', () => {
    render(<Widget title="Test Title" description="Test Description">Content</Widget>);
    expect(screen.getByText('Test Title')).toBeInTheDocument();
    expect(screen.getByText('Test Description')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders loading state', () => {
    render(<Widget isLoading>Content</Widget>);
    // Since lucide-react renders an SVG, we can check if content is not visible or SVG exists
    // The content itself is still in the DOM but hidden by the absolute overlay in our implementation
    const content = screen.queryByText('Content');
    expect(content).not.toBeInTheDocument();
  });

  it('renders error state', () => {
    render(<Widget isError errorMessage="Failed to load" />);
    expect(screen.getByText('Failed to load')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    render(<Widget isEmpty emptyMessage="No items" />);
    expect(screen.getByText('No items')).toBeInTheDocument();
  });
});
