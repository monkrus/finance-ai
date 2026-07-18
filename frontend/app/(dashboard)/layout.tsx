import React from 'react';
import { Sidebar } from '@/components/layout/Sidebar';
import { TopNavigation } from '@/components/layout/TopNavigation';
import { ProtectedRoute } from '@/components/auth/ProtectedRoute';

import { HeroBackground } from '@/components/ui/HeroBackground';

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <ProtectedRoute>
      <div className="flex h-screen overflow-hidden bg-background relative z-0">
        <HeroBackground />
        <Sidebar />
        <div className="flex flex-col flex-1 min-w-0 overflow-hidden relative z-10">
          <TopNavigation />
          <main className="flex-1 overflow-y-auto p-4 md:p-6 lg:p-8">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
