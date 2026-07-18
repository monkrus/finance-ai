'use client';

import { useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { authApi } from '../api';
import { useAuthStore } from '@/store/auth';

/**
 * Ends the session everywhere.
 *
 *  - Revokes the refresh token server-side via the existing
 *    POST /api/v1/auth/logout endpoint (must run before local state is cleared,
 *    since the request body carries the stored refresh token).
 *  - Clears persisted auth state: user, access token, refresh token and the
 *    `finpilot_session` cookie the middleware gates routes on.
 *  - Drops the React Query cache so no previously fetched user data can be
 *    read back by the next session.
 *  - Replaces the history entry with /login so the browser Back button cannot
 *    reopen an authenticated page.
 */
export function useLogout() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const clearAuth = useAuthStore((state) => state.logout);

  return useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // Best effort: if the server call fails (offline, already-expired token)
      // the local session must still be torn down, otherwise the user would
      // remain signed in on this device.
    } finally {
      clearAuth();
      queryClient.clear();
      router.replace('/login');
    }
  }, [clearAuth, queryClient, router]);
}
