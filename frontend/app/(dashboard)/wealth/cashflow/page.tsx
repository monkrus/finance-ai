import { Metadata } from 'next';
import { CashFlowSankey } from '@/features/wealth/charts/CashFlowSankey';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Cash Flow Dashboard | FinPilot AI',
};

export default function CashFlowPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="flex items-center gap-4 mb-2">
        <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
          <Link href="/wealth">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <div>
          <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Cash Flow</h1>
          <p className="text-muted-foreground">Visualize income, expenses, and free cash flow distribution.</p>
        </div>
      </div>

      <CashFlowSankey />
    </div>
  );
}
