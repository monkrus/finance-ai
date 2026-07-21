import { Metadata } from 'next';
import { Card, CardDescription, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export const metadata: Metadata = {
  title: 'Privacy Settings | FinPilot AI',
  description: 'Manage your privacy settings',
};

export default function PrivacyPage() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Privacy</h3>
        <p className="text-sm text-muted-foreground">
          Manage your data and privacy preferences.
        </p>
      </div>
      <div className="shrink-0 bg-border h-[1px] w-full" />
      <Card className="glass-panel border-card-border">
        <CardHeader>
          <CardTitle>Data Export</CardTitle>
          <CardDescription>Placeholder for data export and deletion.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Coming soon in future modules.</p>
        </CardContent>
      </Card>
    </div>
  );
}
