'use client';

import React from 'react';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetGridItem } from '../components/WidgetGrid';
import { Calendar } from 'lucide-react';

export function CalendarWidget() {
  return (
    <WidgetGridItem colSpan={2}>
      <WidgetCard
        title="Upcoming Events"
        description="Market and portfolio schedule"
        headerAction={<Calendar className="h-4 w-4 text-muted-foreground" />}
      >
        <div className="flex flex-col items-center justify-center text-center py-10 text-muted-foreground">
          <Calendar className="h-8 w-8 mb-3 opacity-40" />
          <p className="text-sm font-medium text-foreground">No upcoming events.</p>
          <p className="text-xs mt-1">Earnings and calendar events will appear here.</p>
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
