import { Metadata } from 'next';
import { Plug } from 'lucide-react';
import { WidgetEmpty } from '@/features/dashboard/components/WidgetEmpty';

export const metadata: Metadata = {
  title: 'Integrations | FinPilot AI',
  description: 'Connect banks, brokers, and data providers.',
};

export default function IntegrationsPage() {
  return (
    <div className="flex flex-col gap-6 pb-8 min-h-[70vh]">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Integrations</h1>
        <p className="text-muted-foreground mt-1">
          Connect banks, brokers, and external data providers to FinPilot.
        </p>
      </div>
      <div className="flex-1 min-h-[50vh]">
        <WidgetEmpty
          title="Integrations are coming soon"
          message="Connecting external accounts isn't available yet. This section will light up once integrations ship."
          icon={<Plug className="h-10 w-10 text-muted-foreground mb-4" />}
        />
      </div>
    </div>
  );
}
