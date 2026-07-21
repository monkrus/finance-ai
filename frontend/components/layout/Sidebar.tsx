'use client';

import React, { useEffect } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useUIStore } from '@/store/ui';
import { 
  LayoutDashboard, 
  Briefcase, 
  LineChart, 
  Search, 
  FileText, 
  Newspaper, 
  Wallet, 
  Bell, 
  Link as LinkIcon, 
  Settings, 
  Bot 
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Portfolio', href: '/portfolio', icon: Briefcase },
  { name: 'Market', href: '/market', icon: LineChart },
  { name: 'Analysis', href: '/analysis', icon: Search },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'News', href: '/news', icon: Newspaper },
  { name: 'Wealth', href: '/wealth', icon: Wallet },
  { name: 'AI Coach', href: '/ai', icon: Bot },
];

const secondaryItems = [
  { name: 'Notifications', href: '/notifications', icon: Bell },
  { name: 'Integrations', href: '/integrations', icon: LinkIcon },
  { name: 'Settings', href: '/settings', icon: Settings },
];

const MOBILE_QUERY = '(max-width: 767px)';

export function Sidebar() {
  const pathname = usePathname();
  const sidebarOpen = useUIStore((state) => state.sidebarOpen);
  const setSidebarOpen = useUIStore((state) => state.setSidebarOpen);

  // Collapse the sidebar by default on small screens (so it never covers the
  // content) and keep it open on desktop. Re-applies when crossing the
  // breakpoint. On desktop this is a no-op relative to the store's default.
  useEffect(() => {
    const mq = window.matchMedia(MOBILE_QUERY);
    const apply = () => setSidebarOpen(!mq.matches);
    apply();
    mq.addEventListener('change', apply);
    return () => mq.removeEventListener('change', apply);
  }, [setSidebarOpen]);

  // On mobile, close the drawer after navigating so it doesn't stay over content.
  useEffect(() => {
    if (window.matchMedia(MOBILE_QUERY).matches) setSidebarOpen(false);
  }, [pathname, setSidebarOpen]);

  if (!sidebarOpen) return null;

  return (
    <>
      {/* Mobile backdrop — tap to dismiss the overlay drawer. */}
      <div
        className="fixed inset-0 z-30 bg-black/50 md:hidden"
        aria-hidden="true"
        onClick={() => setSidebarOpen(false)}
      />
      <aside className="fixed inset-y-0 left-0 z-40 w-64 border-r bg-card flex flex-col transition-all duration-300 md:relative md:z-auto">
      <div className="h-16 flex items-center px-6 border-b">
        <span className="text-xl font-bold tracking-tight">FinPilot AI</span>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4 flex flex-col gap-1 px-3">
        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2 px-3">Main</div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          
          return (
            <Link 
              key={item.href} 
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive 
                  ? "bg-primary/10 text-primary" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}

        <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mt-6 mb-2 px-3">System</div>
        {secondaryItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname.startsWith(item.href);
          
          return (
            <Link 
              key={item.href} 
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                isActive 
                  ? "bg-primary/10 text-primary" 
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="h-4 w-4" />
              {item.name}
            </Link>
          );
        })}
      </div>
    </aside>
    </>
  );
}
