import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from '@/features/auth/components/LoginForm';
import { authApi } from '@/features/auth/api';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

jest.mock('@/features/auth/api', () => ({
  authApi: {
    login: jest.fn(),
  },
}));

jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
}));

jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('LoginForm', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<LoginForm />);
    expect(screen.getByText('Welcome back')).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
  });

  it('shows validation errors for empty submission', async () => {
    render(<LoginForm />);
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
      expect(screen.getByText('Password is required')).toBeInTheDocument();
    });
  });

  it('submits successfully and redirects', async () => {
    (authApi.login as jest.Mock).mockResolvedValue({
      user: { id: 1, email: 'test@test.com', role: 'USER' },
      access_token: 'fake-token'
    });

    render(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@test.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } });
    
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(authApi.login).toHaveBeenCalledWith({
        email: 'test@test.com',
        password: 'password123',
        rememberMe: false
      });
      expect(toast.success).toHaveBeenCalledWith('Successfully logged in');
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows error toast on failure', async () => {
    (authApi.login as jest.Mock).mockRejectedValue({
      response: { data: { message: 'Invalid credentials' } }
    });

    render(<LoginForm />);
    
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@test.com' } });
    fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'password123' } });
    
    fireEvent.submit(screen.getByRole('button', { name: /sign in/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Invalid credentials');
    });
  });
});
