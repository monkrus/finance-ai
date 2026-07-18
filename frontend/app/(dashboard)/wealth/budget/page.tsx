import { Metadata } from 'next';
import { BudgetDashboard } from '@/features/wealth/components/BudgetDashboard';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Budget Dashboard | FinPilot AI',
};

export default function BudgetPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="flex items-center gap-4 mb-2">
        <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
          <Link href="/wealth">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Budget & Utilization</h1>
          <p className="text-muted-foreground">Monitor burn rate, track spending, and adjust limits.</p>
        </div>
      </div>

      <BudgetDashboard />
    </div>
  );
}
