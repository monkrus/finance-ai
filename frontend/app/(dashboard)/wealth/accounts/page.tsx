import { Metadata } from 'next';
import { AccountsTable } from '@/features/wealth/tables/AccountsTable';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Plus } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Connected Accounts | FinPilot AI',
};

export default function AccountsPage() {
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
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Connected Accounts</h1>
            <p className="text-muted-foreground">Manage your synced banks, brokerages, and loans.</p>
          </div>
        </div>
        <Button className="bg-indigo-600 hover:bg-indigo-700">
          <Plus className="h-4 w-4 mr-2" /> Add Account
        </Button>
      </div>

      <AccountsTable />
    </div>
  );
}
