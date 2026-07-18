'use client';

import React, { useEffect, useRef, useState } from 'react';
import { useUIStore } from '@/store/ui';
import { useAuthStore } from '@/store/auth';
import { useLogout } from '@/features/auth/hooks/useLogout';
import { Menu, Search, Bell, User, LogOut } from 'lucide-react';

export function TopNavigation() {
  const toggleSidebar = useUIStore((state) => state.toggleSidebar);
  const notificationsCount = useUIStore((state) => state.notificationsCount);
  const userEmail = useAuthStore((state) => state.user?.email);
  const logout = useLogout();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Dismiss the account menu on outside click or Escape.
  useEffect(() => {
    if (!menuOpen) return;

    const handlePointerDown = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') setMenuOpen(false);
    };

    document.addEventListener('mousedown', handlePointerDown);
    document.addEventListener('keydown', handleKeyDown);
    return () => {
      document.removeEventListener('mousedown', handlePointerDown);
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [menuOpen]);

  return (
    <header className="h-16 border-b bg-background flex items-center justify-between px-4 lg:px-6">
      <div className="flex items-center gap-4">
        <button 
          onClick={toggleSidebar}
          className="p-2 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Toggle Sidebar"
        >
          <Menu className="h-5 w-5" />
        </button>
        
        {/* Placeholder for Breadcrumbs */}
        <div className="hidden md:flex text-sm text-muted-foreground">
          Dashboard
        </div>
      </div>

      <div className="flex items-center gap-2 md:gap-4">
        {/* Global Search Button */}
        <button className="p-2 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors hidden sm:flex items-center gap-2">
          <Search className="h-4 w-4" />
          <span className="text-sm">Search...</span>
          <kbd className="hidden md:inline-flex h-5 items-center gap-1 rounded border bg-muted px-1.5 font-mono text-[10px] font-medium text-muted-foreground">
            <span className="text-xs">⌘</span>K
          </kbd>
        </button>

        {/* Notifications */}
        <button 
          className="relative p-2 rounded-md hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
          aria-label="View Notifications"
        >
          <Bell className="h-5 w-5" />
          {notificationsCount > 0 && (
            <span className="absolute top-1 right-1.5 h-2 w-2 rounded-full bg-destructive"></span>
          )}
        </button>

        {/* Profile / account menu */}
        <div className="relative" ref={menuRef}>
          <button
            onClick={() => setMenuOpen((open) => !open)}
            className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-primary hover:bg-primary/20 transition-colors"
            aria-label="User Profile"
            aria-haspopup="menu"
            aria-expanded={menuOpen}
          >
            <User className="h-4 w-4" />
          </button>

          {menuOpen && (
            <div
              role="menu"
              aria-label="Account menu"
              className="absolute right-0 mt-2 w-56 rounded-md border border-border bg-popover py-1 shadow-lg z-50"
            >
              {userEmail && (
                <div className="border-b border-border px-3 py-2 text-xs text-muted-foreground truncate">
                  {userEmail}
                </div>
              )}
              <button
                role="menuitem"
                onClick={() => {
                  setMenuOpen(false);
                  logout();
                }}
                className="flex w-full items-center gap-2 px-3 py-2 text-sm text-foreground hover:bg-muted transition-colors"
              >
                <LogOut className="h-4 w-4" />
                Log out
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
