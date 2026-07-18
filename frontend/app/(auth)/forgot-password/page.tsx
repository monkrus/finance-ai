import { Metadata } from 'next';
import { ForgotPasswordForm } from '@/features/auth/components/ForgotPasswordForm';

export const metadata: Metadata = {
  title: 'Forgot Password - FinPilot AI',
  description: 'Reset your FinPilot AI password',
};

export default function ForgotPasswordPage() {
  return <ForgotPasswordForm />;
}
