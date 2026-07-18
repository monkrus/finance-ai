import Link from 'next/link';
import { Card, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { ShieldAlert } from 'lucide-react';

export default function AccountLockedPage() {
  return (
    <Card className="glass-panel border-card-border shadow-xl">
      <CardHeader className="space-y-1 text-center">
        <div className="flex justify-center mb-4">
          <ShieldAlert className="h-12 w-12 text-destructive" />
        </div>
        <CardTitle className="text-2xl font-bold tracking-tight">Account Locked</CardTitle>
        <CardDescription>
          Your account has been temporarily locked due to too many failed login attempts. Please reset your password or contact support.
        </CardDescription>
      </CardHeader>
      <CardFooter className="flex flex-col space-y-2">
        <Link href="/forgot-password" className="w-full inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 mt-4">
          Reset Password
        </Link>
        <Link href="/login" className="text-sm text-primary hover:underline">
          Back to Login
        </Link>
      </CardFooter>
    </Card>
  );
}
