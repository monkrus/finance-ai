import { Metadata } from 'next';
import { LineChart } from 'lucide-react';
import { WidgetEmpty } from '@/features/dashboard/components/WidgetEmpty';

export const metadata: Metadata = {
  title: 'Analysis | FinPilot AI',
  description: 'Financial analysis: ratios, valuation, forecasting, and risk.',
};

export default function AnalysisPage() {
  return (
    <div className="flex flex-col gap-6 pb-8 min-h-[70vh]">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Analysis</h1>
        <p className="text-muted-foreground mt-1">
          Financial analysis — ratios, valuation, forecasting, and risk scoring.
        </p>
      </div>
      <div className="flex-1 min-h-[50vh]">
        <WidgetEmpty
          title="Analysis workspace is coming soon"
          message="The dedicated analysis workspace isn't available yet. In the meantime, company financials and valuation live on each Market company page."
          icon={<LineChart className="h-10 w-10 text-muted-foreground mb-4" />}
        />
      </div>
    </div>
  );
}
