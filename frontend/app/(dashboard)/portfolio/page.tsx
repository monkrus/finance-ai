import { Metadata } from 'next';
import { PortfolioHero } from '@/features/portfolio/components/PortfolioHero';
import { OverviewCards } from '@/features/portfolio/components/OverviewCards';
import { PortfolioGrowthChart } from '@/features/portfolio/charts/PortfolioGrowthChart';
import { AllocationDoughnut } from '@/features/portfolio/charts/AllocationDoughnut';
import { HoldingsTable } from '@/features/portfolio/tables/HoldingsTable';
import { RiskHeatmap } from '@/features/portfolio/charts/RiskHeatmap';
import { PortfolioAIInsights } from '@/features/portfolio/components/PortfolioAIInsights';
import { PortfolioNews } from '@/features/portfolio/components/PortfolioNews';

export const metadata: Metadata = {
  title: 'Portfolio | FinPilot AI',
  description: 'Manage and analyze your portfolio.',
};

export default function PortfolioPage() {
  return (
    <div className="flex flex-col gap-8 pb-8">
      <PortfolioHero />
      <OverviewCards />
      <div className="grid gap-8 grid-cols-1 lg:grid-cols-3">
        <PortfolioGrowthChart />
        <AllocationDoughnut />
      </div>
      <HoldingsTable />
      <div className="grid gap-8 grid-cols-1 lg:grid-cols-3">
        <PortfolioAIInsights />
        <PortfolioNews />
      </div>
      <RiskHeatmap />
    </div>
  );
}
