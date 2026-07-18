import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TopNavigation } from '@/components/layout/TopNavigation';
import { useUIStore } from '@/store/ui';
import { useAuthStore } from '@/store/auth';
import { authApi } from '@/features/auth/api';
import { useRouter } from 'next/navigation';

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('@/features/auth/api', () => ({
  authApi: { logout: jest.fn() },
}));

const mockReplace = jest.fn();

function renderNav() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  const utils = render(
    <QueryClientProvider client={queryClient}>
      <TopNavigation />
    </QueryClientProvider>
  );
  return { queryClient, ...utils };
}

describe('TopNavigation Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ replace: mockReplace, push: jest.fn() });
    (authApi.logout as jest.Mock).mockResolvedValue(undefined);
    useUIStore.setState({ notificationsCount: 0, sidebarOpen: true });
    useAuthStore.setState({
      user: { id: 1, email: 'test@example.com' } as any,
      accessToken: 'access-1',
      refreshToken: 'refresh-1',
      isAuthenticated: true,
    });
  });

  it('renders correctly', () => {
    renderNav();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
    expect(screen.getByText('Search...')).toBeInTheDocument();
  });

  it('toggles sidebar on menu click', () => {
    renderNav();
    const toggleButton = screen.getByLabelText('Toggle Sidebar');

    fireEvent.click(toggleButton);
    expect(useUIStore.getState().sidebarOpen).toBe(false);

    fireEvent.click(toggleButton);
    expect(useUIStore.getState().sidebarOpen).toBe(true);
  });

  it('shows notification badge when count > 0', () => {
    useUIStore.setState({ notificationsCount: 3 });
    const { container } = renderNav();
    // Badge has bg-destructive class
    const badge = container.querySelector('.bg-destructive');
    expect(badge).toBeInTheDocument();
  });

  it('does not show notification badge when count is 0', () => {
    const { container } = renderNav();
    const badge = container.querySelector('.bg-destructive');
    expect(badge).not.toBeInTheDocument();
  });

  describe('Logout', () => {
    it('hides the account menu until the profile button is clicked', () => {
      renderNav();
      expect(screen.queryByRole('menuitem', { name: /log out/i })).not.toBeInTheDocument();

      fireEvent.click(screen.getByLabelText('User Profile'));

      expect(screen.getByRole('menuitem', { name: /log out/i })).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
    });

    it('revokes the server session, clears auth state + query cache, and redirects to /login', async () => {
      document.cookie = 'finpilot_session=1; path=/';
      const { queryClient } = renderNav();
      queryClient.setQueryData(['dashboard', 'overview'], { netWorth: 123 });

      fireEvent.click(screen.getByLabelText('User Profile'));
      fireEvent.click(screen.getByRole('menuitem', { name: /log out/i }));

      // Backend session revoked via the existing endpoint
      await waitFor(() => expect(authApi.logout).toHaveBeenCalledTimes(1));

      // Local auth state fully cleared
      await waitFor(() => {
        const state = useAuthStore.getState();
        expect(state.isAuthenticated).toBe(false);
        expect(state.accessToken).toBeNull();
        expect(state.refreshToken).toBeNull();
        expect(state.user).toBeNull();
      });

      // Cached user data dropped so the next session cannot read it
      expect(queryClient.getQueryData(['dashboard', 'overview'])).toBeUndefined();

      // Middleware gating cookie removed
      expect(document.cookie).not.toContain('finpilot_session=1');

      // replace (not push) so Back cannot reopen an authenticated page
      await waitFor(() => expect(mockReplace).toHaveBeenCalledWith('/login'));
    });

    it('clears the local session even when the server logout call fails', async () => {
      (authApi.logout as jest.Mock).mockRejectedValue(new Error('network down'));
      renderNav();

      fireEvent.click(screen.getByLabelText('User Profile'));
      fireEvent.click(screen.getByRole('menuitem', { name: /log out/i }));

      await waitFor(() => expect(useAuthStore.getState().isAuthenticated).toBe(false));
      expect(useAuthStore.getState().accessToken).toBeNull();
      await waitFor(() => expect(mockReplace).toHaveBeenCalledWith('/login'));
    });

    it('revokes the session before clearing tokens (refresh token must still be present)', async () => {
      let refreshTokenAtCallTime: string | null | undefined;
      (authApi.logout as jest.Mock).mockImplementation(async () => {
        refreshTokenAtCallTime = useAuthStore.getState().refreshToken;
      });

      renderNav();
      fireEvent.click(screen.getByLabelText('User Profile'));
      fireEvent.click(screen.getByRole('menuitem', { name: /log out/i }));

      await waitFor(() => expect(authApi.logout).toHaveBeenCalled());
      expect(refreshTokenAtCallTime).toBe('refresh-1');
    });
  });
});
