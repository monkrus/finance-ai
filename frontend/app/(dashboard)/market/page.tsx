import { Metadata } from 'next';
import { MarketHero } from '@/features/market/components/MarketHero';
import { GlobalMarkets } from '@/features/market/components/GlobalMarkets';
import { MarketHeatmap } from '@/features/market/components/MarketHeatmap';
import { Button } from '@/components/ui/button';
import { Search } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Market Intelligence | FinPilot AI',
  description: 'Global market data, sectors, and trending stocks.',
};

export default function MarketPage() {
  return (
    <div className="flex flex-col gap-8 pb-8">
      <div className="flex justify-end">
        <Button variant="outline" asChild className="w-full sm:w-64 justify-start text-muted-foreground">
          <Link href="/market/search">
            <Search className="mr-2 h-4 w-4" />
            Search companies, tickers...
          </Link>
        </Button>
      </div>

      <MarketHero />
      
      <section>
        <h2 className="text-xl font-bold mb-4">Global Markets</h2>
        <GlobalMarkets />
      </section>

      <section>
        <MarketHeatmap />
      </section>
    </div>
  );
}
