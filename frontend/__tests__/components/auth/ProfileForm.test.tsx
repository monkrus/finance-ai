import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ProfileForm } from '@/features/auth/components/ProfileForm';
import { authApi } from '@/features/auth/api';
import { useAuthStore } from '@/store/auth';
import { toast } from 'sonner';

jest.mock('@/features/auth/api', () => ({
  authApi: {
    updateProfile: jest.fn(),
  },
}));

jest.mock('sonner', () => ({
  toast: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

describe('ProfileForm', () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: {
        id: 1,
        email: 'test@test.com',
        firstName: 'John',
        lastName: 'Doe',
        username: 'johndoe',
        role: 'USER',
        isEmailVerified: true,
        createdAt: ''
      },
      isAuthenticated: true,
    });
    jest.clearAllMocks();
  });

  it('renders correctly with user data', () => {
    render(<ProfileForm />);
    expect(screen.getByDisplayValue('John')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
    expect(screen.getByDisplayValue('johndoe')).toBeInTheDocument();
  });

  it('submits successfully', async () => {
    (authApi.updateProfile as jest.Mock).mockResolvedValue({
      id: 1, email: 'test@test.com', firstName: 'Jane', lastName: 'Doe', username: 'janedoe', role: 'USER', isEmailVerified: true, createdAt: ''
    });

    render(<ProfileForm />);
    
    fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'janedoe' } });
    
    // The button should become enabled once fields are dirty
    const button = screen.getByRole('button', { name: /update profile/i });
    expect(button).not.toBeDisabled();
    
    fireEvent.submit(button);

    await waitFor(() => {
      expect(authApi.updateProfile).toHaveBeenCalledWith({
        firstName: 'Jane',
        lastName: 'Doe',
        username: 'janedoe',
        timezone: '',
        language: ''
      });
      expect(toast.success).toHaveBeenCalledWith('Profile updated successfully');
      expect(useAuthStore.getState().user?.firstName).toBe('Jane');
    });
  });

  it('shows error toast on failure', async () => {
    (authApi.updateProfile as jest.Mock).mockRejectedValue({
      response: { data: { message: 'Username taken' } }
    });

    render(<ProfileForm />);
    
    fireEvent.change(screen.getByLabelText('Username'), { target: { value: 'janedoe' } });
    fireEvent.submit(screen.getByRole('button', { name: /update profile/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith('Username taken');
    });
  });
});
