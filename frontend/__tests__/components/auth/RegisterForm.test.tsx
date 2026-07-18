import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { RegisterForm } from '@/features/auth/components/RegisterForm';
import { authApi } from '@/features/auth/api';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

jest.mock('@/features/auth/api', () => ({
  authApi: {
    register: jest.fn(),
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

describe('RegisterForm', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    jest.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<RegisterForm />);
    expect(screen.getByText('Create an account')).toBeInTheDocument();
  });

  it('shows validation errors for empty submission', async () => {
    render(<RegisterForm />);
    fireEvent.submit(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(screen.getByText('First name is required')).toBeInTheDocument();
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });
  });

  it('submits successfully and redirects', async () => {
    (authApi.register as jest.Mock).mockResolvedValue({
      user: { id: 1, email: 'test@test.com', role: 'USER' },
      access_token: 'fake-token'
    });

    render(<RegisterForm />);
    
    fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@test.com' } });
    fireEvent.change(screen.getByLabelText(/^Password/), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'Password123!' } });
    
    fireEvent.submit(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(authApi.register).toHaveBeenCalled();
      expect(toast.success).toHaveBeenCalledWith('Account created successfully');
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('shows error toast on failure', async () => {
    (authApi.register as jest.Mock).mockRejectedValue({
      response: { data: { message: 'Email already in use' } }
    });

    render(<RegisterForm />);
    
    fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'John' } });
    fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } });
    fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'test@test.com' } });
    fireEvent.change(screen.getByLabelText(/^Password/), { target: { value: 'Password123!' } });
    fireEvent.change(screen.getByLabelText('Confirm Password'), { target: { value: 'Password123!' } });
    
    fireEvent.submit(screen.getByRole('button', { name: /create account/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Email already in use');
    });
  });
});
