'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { Loader2, CheckCircle2, XCircle } from 'lucide-react';

import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { authApi } from '../api';

export function VerifyEmail() {
  const searchParams = useSearchParams();
  const token = searchParams.get('token');
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [errorMessage, setErrorMessage] = useState('');
  const hasAttempted = useRef(false);

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setErrorMessage('Invalid verification link.');
      return;
    }

    if (hasAttempted.current) return;
    hasAttempted.current = true;

    const verify = async () => {
      try {
        await authApi.verifyEmail(token);
        setStatus('success');
      } catch (error: any) {
        setStatus('error');
        setErrorMessage(error.response?.data?.message || 'Verification failed. The link may have expired.');
      }
    };

    verify();
  }, [token]);

  return (
    <Card className="glass-panel border-card-border shadow-xl">
      <CardHeader className="space-y-1 text-center">
        {status === 'loading' && (
          <>
            <CardTitle className="text-2xl font-bold tracking-tight">Verifying email</CardTitle>
            <CardDescription>Please wait while we verify your email address...</CardDescription>
          </>
        )}
        {status === 'success' && (
          <>
            <div className="flex justify-center mb-4">
              <CheckCircle2 className="h-12 w-12 text-primary" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight">Email Verified!</CardTitle>
            <CardDescription>Your email address has been successfully verified.</CardDescription>
          </>
        )}
        {status === 'error' && (
          <>
            <div className="flex justify-center mb-4">
              <XCircle className="h-12 w-12 text-destructive" />
            </div>
            <CardTitle className="text-2xl font-bold tracking-tight text-destructive">Verification Failed</CardTitle>
            <CardDescription>{errorMessage}</CardDescription>
          </>
        )}
      </CardHeader>
      
      {status === 'loading' && (
        <CardContent className="flex justify-center py-6">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </CardContent>
      )}

      {(status === 'success' || status === 'error') && (
        <CardFooter className="flex flex-col">
          <Link href="/login" className="w-full inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 mt-4">
            Proceed to Login
          </Link>
        </CardFooter>
      )}
    </Card>
  );
}
