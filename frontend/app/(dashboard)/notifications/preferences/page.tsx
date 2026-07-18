import { Metadata } from 'next';
import { PreferenceMatrix } from '@/features/notifications/preferences/PreferenceMatrix';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Save } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Alert Preferences | FinPilot AI',
};

export default function PreferencesPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
            <Link href="/notifications">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Delivery Preferences</h1>
            <p className="text-muted-foreground">Manage how and when you receive financial alerts.</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button size="sm" className="bg-indigo-600 hover:bg-indigo-700">
            <Save className="h-4 w-4 mr-2" /> Save Changes
          </Button>
        </div>
      </div>

      <PreferenceMatrix />
    </div>
  );
}
