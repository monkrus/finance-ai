import { Metadata } from 'next';
import { GoalsTracker } from '@/features/wealth/components/GoalsTracker';
import { RetirementGauge } from '@/features/wealth/charts/RetirementGauge';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Wealth Planning & Goals | FinPilot AI',
};

export default function PlanningPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="flex items-center gap-4 mb-2">
        <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
          <Link href="/wealth">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Financial Planning</h1>
          <p className="text-muted-foreground">Track goals, FIRE progress, and retirement readiness.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-1">
          <RetirementGauge />
        </div>
        <div className="lg:col-span-2 space-y-8">
          <GoalsTracker />
        </div>
      </div>
    </div>
  );
}
