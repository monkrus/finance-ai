import React from 'react';
import { Metadata } from 'next';
import { NetWorthChart } from '@/features/wealth/charts/NetWorthChart';
import { AICoachCard } from '@/features/wealth/components/AICoachCard';
import { WealthTimeline } from '@/features/wealth/components/WealthTimeline';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowRight, Wallet, Target, CreditCard, PieChart } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Wealth Management | FinPilot AI',
  description: 'Track net worth, budgets, cash flow, and financial goals.',
};

export default function WealthPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      {/* Hero Section */}
      <div className="relative overflow-hidden rounded-3xl bg-indigo-950/20 border border-white/5 p-8 md:p-12">
        <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-500/20 rounded-full blur-[120px] pointer-events-none translate-x-1/2 -translate-y-1/2" />
        <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none -translate-x-1/2 translate-y-1/2" />
        
        <div className="relative z-10 max-w-2xl">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-transparent bg-clip-text bg-gradient-to-br from-white to-white/60">
            Wealth Intelligence
          </h1>
          <p className="text-muted-foreground text-lg mb-8">
            Comprehensive tracking of your net worth, cash flow, and financial goals powered by FinPilot AI.
          </p>
          <div className="flex flex-wrap gap-4">
            <Button asChild className="bg-indigo-600 hover:bg-indigo-700 text-white rounded-full px-6">
              <Link href="/wealth/accounts">
                <Wallet className="w-4 h-4 mr-2" /> Connect Accounts
              </Link>
            </Button>
            <Button asChild variant="outline" className="rounded-full px-6 bg-background/50 backdrop-blur border-white/10 hover:bg-white/10 text-white">
              <Link href="/wealth/budget">
                <PieChart className="w-4 h-4 mr-2" /> View Budget
              </Link>
            </Button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-8">
          {/* Net Worth Chart */}
          <NetWorthChart />

          {/* Quick Links Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4">
            <QuickLinkCard href="/wealth/accounts" title="Accounts" icon={<Wallet />} />
            <QuickLinkCard href="/wealth/transactions" title="Transactions" icon={<CreditCard />} />
            <QuickLinkCard href="/wealth/budget" title="Budgets" icon={<PieChart />} />
            <QuickLinkCard href="/wealth/planning" title="Planning" icon={<Target />} />
          </div>
        </div>
        
        <div className="space-y-8">
          <AICoachCard />
          <WealthTimeline />
        </div>
      </div>
    </div>
  );
}

function QuickLinkCard({ href, title, icon }: { href: string, title: string, icon: React.ReactNode }) {
  return (
    <Link href={href} className="group block">
      <div className="bg-card/40 backdrop-blur-md border border-white/5 rounded-2xl p-6 hover:bg-card/60 transition-colors h-full flex flex-col items-center justify-center text-center gap-4">
        <div className="p-3 bg-indigo-500/10 text-indigo-400 rounded-full group-hover:scale-110 group-hover:bg-indigo-500 group-hover:text-white transition-all">
          {React.cloneElement(icon as React.ReactElement<{ className?: string }>, { className: 'w-6 h-6' })}
        </div>
        <div className="font-semibold">{title}</div>
      </div>
    </Link>
  );
}
