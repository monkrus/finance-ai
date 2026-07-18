import { Metadata } from 'next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { TransactionDialog } from '@/features/portfolio/dialogs/TransactionDialog';

export async function generateMetadata({ params }: { params: Promise<{ ticker: string }> }): Promise<Metadata> {
  const p = await params;
  return {
    title: `${p.ticker.toUpperCase()} | FinPilot AI`,
    description: `Detailed view for ${p.ticker.toUpperCase()}`,
  };
}

export default async function HoldingDetailPage({ params }: { params: Promise<{ ticker: string }> }) {
  const p = await params;
  const ticker = p.ticker.toUpperCase();

  return (
    <div className="flex flex-col gap-8 pb-8">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/portfolio">
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </Button>
        <h1 className="text-3xl font-bold tracking-tight text-foreground flex-1">{ticker} Overview</h1>
        <TransactionDialog defaultTicker={ticker}>
          <Button variant="default">Trade {ticker}</Button>
        </TransactionDialog>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Company</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{ticker} Corp</div></CardContent>
        </Card>
        <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Current Price</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">$150.00</div></CardContent>
        </Card>
        <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Your Position</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">100 Shares</div></CardContent>
        </Card>
        <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg">
          <CardHeader className="pb-2"><CardTitle className="text-sm text-muted-foreground">Total Return</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold text-emerald-500">+12.5%</div></CardContent>
        </Card>
      </div>

      {/* Placeholders for AI Insight and Transactions */}
      <div className="grid gap-8 grid-cols-1 lg:grid-cols-2">
        <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[300px]">
          <CardHeader><CardTitle>AI Analysis</CardTitle></CardHeader>
          <CardContent>
            <p className="text-muted-foreground">AI analysis for {ticker} will appear here.</p>
          </CardContent>
        </Card>
        <Card className="bg-card/60 backdrop-blur-lg border-white/10 shadow-lg h-[300px]">
          <CardHeader><CardTitle>Recent Transactions</CardTitle></CardHeader>
          <CardContent>
            <p className="text-muted-foreground">No recent transactions for {ticker}.</p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
