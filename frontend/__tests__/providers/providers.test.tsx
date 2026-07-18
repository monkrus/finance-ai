import React from 'react';
import { render, screen } from '@testing-library/react';
import { RootProviders } from '@/providers';
import { useQueryClient } from '@tanstack/react-query';

// Component to test if context is provided
const TestComponent = () => {
  const queryClient = useQueryClient();
  return <div>{queryClient ? 'Has Query Client' : 'No Query Client'}</div>;
};

describe('RootProviders', () => {
  it('provides all necessary contexts to children', () => {
    // Suppress NextThemes hydration warnings in test environment
    const originalConsoleError = console.error;
    console.error = jest.fn();

    render(
      <RootProviders>
        <TestComponent />
      </RootProviders>
    );

    expect(screen.getByText('Has Query Client')).toBeInTheDocument();
    
    // Restore console
    console.error = originalConsoleError;
  });
});
