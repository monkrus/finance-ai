import { Metadata } from 'next';
import { TransactionsTable } from '@/features/wealth/tables/TransactionsTable';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Download, Upload } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Transactions | FinPilot AI',
};

export default function TransactionsPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
            <Link href="/wealth">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Transactions</h1>
            <p className="text-muted-foreground">Unified ledger across all your connected accounts.</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" className="border-white/10 bg-background/50">
            <Upload className="h-4 w-4 mr-2" /> Import CSV
          </Button>
          <Button variant="outline" className="border-white/10 bg-background/50">
            <Download className="h-4 w-4 mr-2" /> Export
          </Button>
        </div>
      </div>

      <TransactionsTable />
    </div>
  );
}
