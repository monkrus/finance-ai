'use client';

import React from 'react';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetGridItem } from '../components/WidgetGrid';
import { Activity } from 'lucide-react';

export function RecentActivityWidget() {
  return (
    <WidgetGridItem colSpan={2}>
      <WidgetCard
        title="Recent Activity"
        description="Your latest account actions"
        headerAction={<Activity className="h-4 w-4 text-muted-foreground" />}
      >
        <div className="flex flex-col items-center justify-center text-center py-10 text-muted-foreground">
          <Activity className="h-8 w-8 mb-3 opacity-40" />
          <p className="text-sm font-medium text-foreground">No activity yet.</p>
          <p className="text-xs mt-1">Your trades and transfers will show up here.</p>
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
