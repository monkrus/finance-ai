import { Metadata } from 'next';
import { DashboardHeader } from '@/features/dashboard/components/DashboardHeader';
import { WidgetGrid } from '@/features/dashboard/components/WidgetGrid';
import { KPIWidget } from '@/features/dashboard/widgets/KPIWidget';
import { PortfolioSnapshotWidget } from '@/features/dashboard/widgets/PortfolioSnapshotWidget';
import { MarketOverviewWidget } from '@/features/dashboard/widgets/MarketOverviewWidget';
import { NewsWidget } from '@/features/dashboard/widgets/NewsWidget';
import { WatchlistWidget } from '@/features/dashboard/widgets/WatchlistWidget';
import { CalendarWidget } from '@/features/dashboard/widgets/CalendarWidget';
import { AIInsightsWidget } from '@/features/dashboard/widgets/AIInsightsWidget';
import { NotificationWidget } from '@/features/dashboard/widgets/NotificationWidget';
import { RecentActivityWidget } from '@/features/dashboard/widgets/RecentActivityWidget';

export const metadata: Metadata = {
  title: 'Dashboard | FinPilot AI',
  description: 'Your wealth and portfolio overview',
};

export default function DashboardPage() {
  return (
    <div className="relative w-full pb-20">
      <DashboardHeader />
      
      <WidgetGrid>
        {/* Row 1: KPI Cards (Spans 4 columns internally, rendering 4 items) */}
        <KPIWidget />
        
        {/* Row 2 & 3: Main Data Area */}
        <PortfolioSnapshotWidget /> {/* ColSpan: 2, RowSpan: 2 */}
        
        <MarketOverviewWidget />    {/* ColSpan: 2 */}
        <AIInsightsWidget />        {/* ColSpan: 2 */}
        
        {/* Row 4: News & Watchlist */}
        <NewsWidget />              {/* ColSpan: 2 */}
        <WatchlistWidget />         {/* ColSpan: 2 */}
        
        {/* Row 5: Schedule & Alerts */}
        <CalendarWidget />          {/* ColSpan: 2 */}
        <NotificationWidget />      {/* ColSpan: 2 */}
        
        {/* Row 6: Activity */}
        <RecentActivityWidget />    {/* ColSpan: 2 */}
      </WidgetGrid>
    </div>
  );
}
