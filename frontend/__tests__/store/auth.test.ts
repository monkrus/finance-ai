import { useAuthStore } from '@/store/auth';

describe('Auth Store', () => {
  beforeEach(() => {
    // Reset state
    useAuthStore.setState({
      user: null,
      accessToken: null,
      isAuthenticated: false,
    });
  });

  it('should set auth correctly', () => {
    const { setAuth } = useAuthStore.getState();
    const mockUser = { id: 1, email: 'test@example.com' } as any;
    const mockToken = 'mock-jwt-token';
    
    setAuth(mockUser, mockToken);
    
    const state = useAuthStore.getState();
    expect(state.user).toEqual(mockUser);
    expect(state.accessToken).toBe(mockToken);
    expect(state.isAuthenticated).toBe(true);
  });

  it('should logout correctly', () => {
    useAuthStore.setState({
      user: { id: 1, email: 'test@example.com' } as any,
      accessToken: 'token',
      isAuthenticated: true,
    });

    const { logout } = useAuthStore.getState();
    logout();

    const state = useAuthStore.getState();
    expect(state.user).toBeNull();
    expect(state.accessToken).toBeNull();
    expect(state.isAuthenticated).toBe(false);
  });

  it('should store the refresh token when provided', () => {
    const { setAuth } = useAuthStore.getState();
    setAuth({ id: 1, email: 'test@example.com' } as any, 'access-1', 'refresh-1');
    expect(useAuthStore.getState().refreshToken).toBe('refresh-1');
  });

  it('should preserve the existing refresh token when omitted (access-token refresh flow)', () => {
    const { setAuth } = useAuthStore.getState();
    setAuth({ id: 1, email: 'test@example.com' } as any, 'access-1', 'refresh-1');
    // Simulate the interceptor rotating only the access token.
    setAuth({ id: 1, email: 'test@example.com' } as any, 'access-2');
    const state = useAuthStore.getState();
    expect(state.accessToken).toBe('access-2');
    expect(state.refreshToken).toBe('refresh-1');
  });

  it('should clear the refresh token on logout', () => {
    const { setAuth, logout } = useAuthStore.getState();
    setAuth({ id: 1, email: 'test@example.com' } as any, 'access-1', 'refresh-1');
    logout();
    expect(useAuthStore.getState().refreshToken).toBeNull();
  });
});
