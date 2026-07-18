import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { User } from '@/features/auth/types';

// Name of the lightweight, non-HttpOnly cookie the Next.js middleware reads to
// perform coarse route gating. The real authorization is always the Bearer
// access token validated server-side on every API call; this cookie only lets
// edge middleware know a session exists (localStorage is not readable there).
const SESSION_COOKIE = 'finpilot_session';

// Lifetime mirrors the backend refresh-token window (7 days) so route gating
// survives page reloads and browser restarts, staying consistent with the
// persisted client session.
const SESSION_COOKIE_MAX_AGE = 60 * 60 * 24 * 7;

function setSessionCookie(present: boolean) {
  if (typeof document === 'undefined') return;
  if (present) {
    document.cookie = `${SESSION_COOKIE}=1; path=/; Max-Age=${SESSION_COOKIE_MAX_AGE}; SameSite=Lax`;
  } else {
    document.cookie = `${SESSION_COOKIE}=; path=/; Max-Age=0; SameSite=Lax`;
  }
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isHydrated: boolean;
  setAuth: (user: User, token: string, refreshToken?: string) => void;
  logout: () => void;
  updateUser: (user: Partial<User>) => void;
  setHydrated: (state: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isHydrated: false,
      setAuth: (user, token, refreshToken) => {
        setSessionCookie(true);
        set((state) => ({
          user,
          accessToken: token,
          // Preserve the existing refresh token when a caller (e.g. the access
          // token refresh flow) does not supply a rotated one.
          refreshToken: refreshToken !== undefined ? refreshToken : state.refreshToken,
          isAuthenticated: true,
        }));
      },
      logout: () => {
        setSessionCookie(false);
        set({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
      },
      updateUser: (updates) => set((state) => ({
        user: state.user ? { ...state.user, ...updates } : null
      })),
      setHydrated: (state) => set({ isHydrated: state }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated
      }),
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.setHydrated(true);
          // Re-mirror the session cookie after a page refresh so middleware
          // route gating stays consistent with the restored client session.
          setSessionCookie(!!state.isAuthenticated && !!state.accessToken);
        }
      },
    }
  )
);
