import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/store/auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: unknown) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });

  failedQueue = [];
};

// Request Interceptor to attach JWT
apiClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().accessToken;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response Interceptor for token refresh logic
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    // Never attempt a token refresh for the auth endpoints themselves. A 401 from
    // /auth/login (wrong password) or /auth/refresh is a genuine auth failure, not
    // an expired access token — refreshing there fires a needless request, clobbers
    // the real error, and can log the user out mid-login.
    const AUTH_PATHS = [
      '/api/v1/auth/login',
      '/api/v1/auth/register',
      '/api/v1/auth/refresh',
      '/api/v1/auth/logout',
    ];
    const isAuthPath = AUTH_PATHS.some((p) => originalRequest.url?.includes(p));

    if (error.response?.status === 401 && !originalRequest._retry && !isAuthPath) {
      // With no refresh token there is nothing to refresh with. A 401 on a
      // protected route then means the session is unrecoverable — clear auth
      // state (so the app redirects to login) and reject.
      if (!useAuthStore.getState().refreshToken) {
        useAuthStore.getState().logout();
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise(function (resolve, reject) {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = 'Bearer ' + token;
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const currentRefreshToken = useAuthStore.getState().refreshToken;
        const response = await axios.post<{ access_token: string; refresh_token?: string }>(
          `${API_BASE_URL}/api/v1/auth/refresh`,
          { refresh_token: currentRefreshToken },
          { withCredentials: true }
        );

        const newToken = response.data.access_token;
        const rotatedRefreshToken = response.data.refresh_token;

        useAuthStore.getState().setAuth(
          useAuthStore.getState().user!,
          newToken,
          rotatedRefreshToken
        );

        processQueue(null, newToken);
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        useAuthStore.getState().logout();
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);
