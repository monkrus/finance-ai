import { Metadata } from 'next';
import { Card, CardDescription, CardHeader, CardTitle, CardContent } from '@/components/ui/card';

export const metadata: Metadata = {
  title: 'Appearance Settings - FinPilot AI',
  description: 'Manage your appearance settings',
};

export default function AppearancePage() {
  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium">Appearance</h3>
        <p className="text-sm text-muted-foreground">
          Customize how FinPilot AI looks on your device.
        </p>
      </div>
      <div className="shrink-0 bg-border h-[1px] w-full" />
      <Card className="glass-panel border-card-border">
        <CardHeader>
          <CardTitle>Theme</CardTitle>
          <CardDescription>Placeholder for theme switcher.</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">Coming soon in future modules.</p>
        </CardContent>
      </Card>
    </div>
  );
}
