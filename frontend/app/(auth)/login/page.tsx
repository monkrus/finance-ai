import { Metadata } from 'next';
import { LoginForm } from '@/features/auth/components/LoginForm';

export const metadata: Metadata = {
  title: 'Login - FinPilot AI',
  description: 'Login to your FinPilot AI account',
};

export default function LoginPage() {
  return <LoginForm />;
}
