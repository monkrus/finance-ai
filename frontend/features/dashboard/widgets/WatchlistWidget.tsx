'use client';

import React from 'react';
import { WidgetCard } from '../components/WidgetCard';
import { WidgetGridItem } from '../components/WidgetGrid';
import { Star } from 'lucide-react';

export function WatchlistWidget() {
  return (
    <WidgetGridItem colSpan={2}>
      <WidgetCard
        title="Watchlist"
        description="Your favorite assets"
        headerAction={<Star className="h-4 w-4 text-amber-400 fill-amber-400" />}
      >
        <div className="flex flex-col items-center justify-center text-center py-10 text-muted-foreground">
          <Star className="h-8 w-8 mb-3 opacity-40" />
          <p className="text-sm font-medium text-foreground">Create your first watchlist.</p>
          <p className="text-xs mt-1">Assets you follow will appear here.</p>
        </div>
      </WidgetCard>
    </WidgetGridItem>
  );
}
