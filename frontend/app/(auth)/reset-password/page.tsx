import { Metadata } from 'next';
import { Suspense } from 'react';
import { ResetPasswordForm } from '@/features/auth/components/ResetPasswordForm';

export const metadata: Metadata = {
  title: 'Reset Password | FinPilot AI',
  description: 'Reset your FinPilot AI password',
};

export default function ResetPasswordPage() {
  return (
    <Suspense fallback={<div className="h-40 flex items-center justify-center">Loading...</div>}>
      <ResetPasswordForm />
    </Suspense>
  );
}
