import { Metadata } from 'next';
import { FileText } from 'lucide-react';
import { WidgetEmpty } from '@/features/dashboard/components/WidgetEmpty';

export const metadata: Metadata = {
  title: 'Documents | FinPilot AI',
  description: 'Upload financial documents and ask grounded questions.',
};

export default function DocumentsPage() {
  return (
    <div className="flex flex-col gap-6 pb-8 min-h-[70vh]">
      <div>
        <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Documents</h1>
        <p className="text-muted-foreground mt-1">
          Upload financial documents and ask grounded questions with AI.
        </p>
      </div>
      <div className="flex-1 min-h-[50vh]">
        <WidgetEmpty
          title="Document intelligence is coming soon"
          message="Uploading and querying documents isn't available yet. This section will light up once the feature ships."
          icon={<FileText className="h-10 w-10 text-muted-foreground mb-4" />}
        />
      </div>
    </div>
  );
}
