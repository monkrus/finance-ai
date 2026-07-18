import { Metadata } from 'next';
import { Suspense } from 'react';
import { VerifyEmail } from '@/features/auth/components/VerifyEmail';

export const metadata: Metadata = {
  title: 'Verify Email - FinPilot AI',
  description: 'Verify your FinPilot AI email address',
};

export default function VerifyEmailPage() {
  return (
    <Suspense fallback={<div className="h-40 flex items-center justify-center">Loading...</div>}>
      <VerifyEmail />
    </Suspense>
  );
}
