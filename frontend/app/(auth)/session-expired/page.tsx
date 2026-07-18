import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle, CardFooter } from '@/components/ui/card';
import { Clock } from 'lucide-react';

export default function SessionExpiredPage() {
  return (
    <Card className="glass-panel border-card-border shadow-xl">
      <CardHeader className="space-y-1 text-center">
        <div className="flex justify-center mb-4">
          <Clock className="h-12 w-12 text-destructive" />
        </div>
        <CardTitle className="text-2xl font-bold tracking-tight">Session Expired</CardTitle>
        <CardDescription>
          Your session has expired due to inactivity. Please log in again to continue.
        </CardDescription>
      </CardHeader>
      <CardFooter className="flex flex-col">
        <Link href="/login" className="w-full inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 bg-primary text-primary-foreground hover:bg-primary/90 h-10 px-4 py-2 mt-4">
          Log In Again
        </Link>
      </CardFooter>
    </Card>
  );
}
