import { Metadata } from 'next';
import { RegisterForm } from '@/features/auth/components/RegisterForm';

export const metadata: Metadata = {
  title: 'Create an account | FinPilot AI',
  description: 'Create your FinPilot AI account',
};

export default function RegisterPage() {
  return <RegisterForm />;
}
