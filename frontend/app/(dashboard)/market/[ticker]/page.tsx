import { Metadata } from 'next';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ArrowLeft } from 'lucide-react';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { CompanyProfile } from '@/features/market/components/CompanyProfile';
import { PriceChart } from '@/features/market/charts/PriceChart';
import { TechIndicators } from '@/features/market/components/TechIndicators';
import { FinancialStatementsTable } from '@/features/market/tables/FinancialStatementsTable';
import { FinancialRatios } from '@/features/market/components/FinancialRatios';
import { ValuationModels } from '@/features/market/components/ValuationModels';
import { PeerComparison } from '@/features/market/tables/PeerComparison';
import { EarningsTimeline } from '@/features/market/components/EarningsTimeline';
import { AnalystRatings } from '@/features/market/components/AnalystRatings';
import { CompanyNews } from '@/features/market/components/CompanyNews';
import { AIResearchReport } from '@/features/market/components/AIResearchReport';

export async function generateMetadata({ params }: { params: Promise<{ ticker: string }> }): Promise<Metadata> {
  const p = await params;
  return {
    title: `${p.ticker.toUpperCase()} Research | FinPilot AI`,
  };
}

export default async function CompanyOverviewPage({ params }: { params: Promise<{ ticker: string }> }) {
  const p = await params;
  const ticker = p.ticker.toUpperCase();

  return (
    <div className="flex flex-col gap-6 pb-8 min-h-screen">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
          <Link href="/market">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">{ticker} Research & Analysis</h1>
      </div>

      <CompanyProfile ticker={ticker} />

      <Tabs defaultValue="overview" className="w-full">
        <TabsList className="bg-card/50 backdrop-blur-md border border-white/10 flex flex-wrap h-auto p-1 sticky top-[60px] z-30 justify-start">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="financials">Financials</TabsTrigger>
          <TabsTrigger value="valuation">Valuation & Peers</TabsTrigger>
          <TabsTrigger value="estimates">Earnings & Analysts</TabsTrigger>
          <TabsTrigger value="news">News & AI</TabsTrigger>
        </TabsList>
        
        <div className="mt-6">
          <TabsContent value="overview" className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <PriceChart ticker={ticker} />
            <TechIndicators ticker={ticker} />
          </TabsContent>
          
          <TabsContent value="financials" className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <FinancialRatios ticker={ticker} />
            <FinancialStatementsTable ticker={ticker} />
          </TabsContent>
          
          <TabsContent value="valuation" className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ValuationModels ticker={ticker} />
            <PeerComparison ticker={ticker} />
          </TabsContent>
          
          <TabsContent value="estimates" className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <EarningsTimeline ticker={ticker} />
              <AnalystRatings ticker={ticker} />
            </div>
          </TabsContent>
          
          <TabsContent value="news" className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 items-start">
              <AIResearchReport ticker={ticker} />
              <CompanyNews ticker={ticker} />
            </div>
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}
