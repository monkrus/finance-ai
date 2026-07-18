export type Role = 'USER' | 'ADMIN' | 'PREMIUM';

export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: Role;
  username?: string;
  timezone?: string;
  language?: string;
  theme?: string;
  avatarUrl?: string;
  isEmailVerified: boolean;
  createdAt: string;
}

export interface AuthResponse {
  user: User;
  access_token: string;
  refresh_token?: string;
}

export interface ApiErrorResponse {
  message: string;
  details?: Record<string, string[]>;
}
