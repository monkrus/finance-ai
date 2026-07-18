import { apiClient } from '@/services/api';
import { useAuthStore } from '@/store/auth';
import { AuthResponse, User } from '../types';
import { 
  LoginFormData, 
  RegisterFormData, 
  ForgotPasswordFormData, 
  ResetPasswordFormData,
  UpdateProfileFormData
} from '../utils/validations';

export const authApi = {
  login: async (data: LoginFormData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/login', data);
    return response.data;
  },

  register: async (data: RegisterFormData): Promise<AuthResponse> => {
    const response = await apiClient.post<AuthResponse>('/api/v1/auth/register', data);
    return response.data;
  },

  logout: async (): Promise<void> => {
    // Backend revokes the server-side session by refresh token.
    const refresh_token = useAuthStore.getState().refreshToken;
    await apiClient.post('/api/v1/auth/logout', { refresh_token });
  },

  refresh: async (): Promise<{ access_token: string; refresh_token: string }> => {
    const refresh_token = useAuthStore.getState().refreshToken;
    const response = await apiClient.post<{ access_token: string; refresh_token: string }>(
      '/api/v1/auth/refresh',
      { refresh_token }
    );
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await apiClient.get<User>('/api/v1/users/me');
    return response.data;
  },

  updateProfile: async (data: UpdateProfileFormData): Promise<User> => {
    const response = await apiClient.put<User>('/api/v1/users/me', data);
    return response.data;
  },

  verifyEmail: async (token: string): Promise<void> => {
    await apiClient.post('/api/v1/users/verify-email', { token });
  },

  forgotPassword: async (data: ForgotPasswordFormData): Promise<void> => {
    await apiClient.post('/api/v1/users/password-reset/request', data);
  },

  resetPassword: async (token: string, data: ResetPasswordFormData): Promise<void> => {
    await apiClient.post('/api/v1/users/password-reset/confirm', { token, ...data });
  }
};
