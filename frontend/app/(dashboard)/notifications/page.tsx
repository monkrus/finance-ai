import { Metadata } from 'next';
import { NotificationFeed } from '@/features/notifications/components/NotificationFeed';
import { Button } from '@/components/ui/button';
import { ArrowLeft, Settings, Filter, CheckSquare } from 'lucide-react';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Notifications | FinPilot AI',
};

export default function NotificationsPage() {
  return (
    <div className="flex flex-col gap-8 pb-8 min-h-screen">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild className="hover:bg-accent/50 text-muted-foreground">
            <Link href="/">
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-2xl md:text-3xl font-bold tracking-tight">Notification Center</h1>
            <p className="text-muted-foreground">Manage alerts, events, and portfolio updates.</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="bg-background/50 border-white/10 hidden md:flex">
            <CheckSquare className="h-4 w-4 mr-2" /> Mark All Read
          </Button>
          <Button variant="outline" size="sm" className="bg-background/50 border-white/10 hidden md:flex">
            <Filter className="h-4 w-4 mr-2" /> Filter
          </Button>
          <Button variant="outline" size="icon" asChild className="bg-background/50 border-white/10">
            <Link href="/notifications/preferences">
              <Settings className="h-4 w-4" />
            </Link>
          </Button>
        </div>
      </div>

      <NotificationFeed />
    </div>
  );
}
