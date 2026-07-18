'use client';

import React from 'react';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetGridItem } from '../components/WidgetGrid';
import { Bell } from 'lucide-react';

export function NotificationWidget() {
  return (
    <WidgetGridItem colSpan={2}>
      <WidgetCard
        title="Notification Center"
        description="Recent alerts and system messages"
        headerAction={<Bell className="h-4 w-4 text-muted-foreground" />}
      >
        <div className="flex flex-col items-center justify-center text-center py-10 text-muted-foreground">
          <Bell className="h-8 w-8 mb-3 opacity-40" />
          <p className="text-sm font-medium text-foreground">No notifications.</p>
          <p className="text-xs mt-1">Alerts and system messages will appear here.</p>
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
